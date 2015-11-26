import pygame
import pygame.gfxdraw
import math
import threading
from itertools import islice, product, chain
from six.moves import queue, range
from . import quadtree


class RendererBase(object):
    """ Renderer that can be updated incrementally

    Base class to render a map onto a buffer that is suitable for blitting onto
    the screen as one surface, rather than a collection of tiles.

    The class supports differed rendering, multiple layers, shapes and layering
    surfaces (usually from sprites) in the map, creating an illusion of depth.

    This class works well for maps that operate on a small display and where
    the map is much larger than the display, but you will get poor performance
    if the map is smaller than the display.

    The buffered renderer must be used with a data class to get tile and shape
    information.  See the data class api in pyscroll.data, or use the built in
    pytmx support.
    """
    def __init__(self, data, size, colorkey=None, padding=4,
                 clamp_camera=False):

        # default options
        self.colorkey = colorkey
        self.padding = padding
        self.clamp_camera = clamp_camera
        self.clipping = True
        self.flush_on_draw = True
        self.update_rate = 25
        self.default_shape_texture_gid = 1
        self.default_shape_color = (0, 255, 0)

        # internal defaults
        self.idle = False
        self.blank = False
        self.data = None
        self.size = None
        self.xoffset = None
        self.yoffset = None
        self.old_x = None
        self.old_y = None
        self.default_image = None
        self.buffer = None
        self.rect = None
        self.view = None
        self.half_width = None
        self.half_height = None
        self.iso_double_height = False

        self.lock = threading.Lock()
        self.set_data(data)
        self.set_size(size)
        self.queue = iter([])

    def set_data(self, data):
        self.data = data
        self.generate_default_image()

    def set_size(self, size):
        """ Set the size of the map in pixels
        """
        tw = self.data.tilewidth
        th = self.data.tileheight
        buffer_width = size[0] + tw * self.padding
        buffer_height = size[1] + th * self.padding
        self.buffer = pygame.Surface((buffer_width, buffer_height))
        self.view = pygame.Rect(0, 0, math.ceil(buffer_width / tw),
                                math.ceil(buffer_height / th))

        # this is the pixel size of the entire map
        self.rect = pygame.Rect(0, 0, self.data.width * tw,
                                self.data.height * th)

        self.half_width = size[0] / 2
        self.half_height = size[1] / 2

        if self.data.orientation == 'orthogonal':
            # quadtree is used to correctly draw tiles that cover 'sprites'
            def make_rect(x, y):
                return pygame.Rect((x * tw, y * th), (tw, th))

            rects = [make_rect(x, y)
                     for x, y in product(range(self.view.width),
                                         range(self.view.height))]

            # TODO: figure out what depth -actually- does
            self.layer_quadtree = quadtree.FastQuadTree(rects, 1)

        if self.colorkey:
            self.buffer.set_colorkey(self.colorkey)
            self.buffer.fill(self.colorkey)

        self.size = size
        self.idle = False
        self.blank = True
        self.xoffset = 0
        self.yoffset = 0
        self.old_x = 0
        self.old_y = 0

    def get_tile_image(self, position):
        try:
            return self.data.get_tile_image(position)
        except ValueError:
            return self.default_image

    def scroll(self, vector):
        """ scroll the background in pixels
        """
        self.center((vector[0] + self.old_x, vector[1] + self.old_y))

    def center(self, coords):
        """ center the map on a pixel
        """
        x, y = [round(i, 0) for i in coords]
        hpad = int(self.padding / 2)
        tw = self.data.tilewidth
        th = self.data.tileheight

        if self.clamp_camera:
            if x < self.half_width:
                x = self.half_width
            elif x + self.half_width > self.rect.width:
                x = self.rect.width - self.half_width
            if y < self.half_height:
                y = self.half_height
            elif y + self.half_height > self.rect.height:
                y = self.rect.height - self.half_height

        if self.old_x == x and self.old_y == y:
            self.idle = True
            return

        self.idle = False

        # calc the new position in tiles and offset
        left, self.xoffset = divmod(x - self.half_width, tw)
        top, self.yoffset = divmod(y - self.half_height, th)

        # determine if tiles should be redrawn
        dx = int(left - hpad - self.view.left)
        dy = int(top - hpad - self.view.top)

        # adjust the offsets of the buffer
        self.xoffset += hpad * tw
        self.yoffset += hpad * th

        # adjust the view if the buffer is scrolled too far
        if (abs(dx) >= 1) or (abs(dy) >= 1):
            self.flush()
            self.view = self.view.move((dx, dy))

            # scroll the image (much faster than redrawing the tiles!)
            self.buffer.scroll(-dx * tw, -dy * th)
            self.update_queue(self.get_edge_tiles((dx, dy)))

        self.old_x, self.old_y = x, y

    def update_queue(self, iterator):
        """ Add some tiles to the queue
        """
        self.queue = chain(self.queue, iterator)

    def get_edge_tiles(self, offset):
        """ Get the tile coordinates that need to be redrawn
        """
        x, y = map(int, offset)
        layers = list(self.data.visible_tile_layers)
        view = self.view
        queue = None

        # NOTE: i'm not sure why the the -1 in right and bottom are required
        #       for python 3.  it may have some performance implications, but
        #       i'll benchmark it later.

        # right
        if x > 0:
            queue = product(range(view.right - x - 1, view.right),
                            range(view.top, view.bottom), layers)

        # left
        elif x < 0:
            queue = product(range(view.left, view.left - x),
                            range(view.top, view.bottom), layers)

        # bottom
        if y > 0:
            p = product(range(view.left, view.right),
                        range(view.bottom - y - 1, view.bottom), layers)
            if queue is None:
                queue = p
            else:
                queue = chain(p, queue)

        # top
        elif y < 0:
            p = product(range(view.left, view.right),
                        range(view.top, view.top - y), layers)
            if queue is None:
                queue = p
            else:
                queue = chain(p, queue)

        return queue

    def update(self, dt=None):
        """ Draw tiles in the background

        the drawing operations and management of the buffer is handled here.
        if you are updating more than drawing, then updating here will draw
        off screen tiles.  this will limit expensive tile blits during screen
        draws.  if your draw and update happens every game loop, then you will
        not benefit from updates, but it won't hurt either.
        """
        self.blit_tiles(islice(self.queue, self.update_rate))

    def draw(self, surface, rect, surfaces):
        raise NotImplementedError

    def flush(self):
        """ Blit the tiles and block until the tile queue is empty
        """
        self.blit_tiles(self.queue)
        self.draw_objects()

    def draw_objects(self):
        """ Totally unoptimized drawing of objects to the map
        """
        tw = self.data.tilewidth
        th = self.data.tileheight
        buff = self.buffer
        blit = buff.blit
        map_gid = self.data.tmx.map_gid
        default_color = self.default_shape_color
        get_image_by_gid = self.data.get_tile_image_by_gid
        _draw_textured_poly = pygame.gfxdraw.textured_polygon
        _draw_poly = pygame.draw.polygon
        _draw_lines = pygame.draw.lines

        ox = self.view.left * tw
        oy = self.view.top * th

        def draw_textured_poly(texture, points):
            try:
                _draw_textured_poly(buff, points, texture, tw, th)
            except pygame.error:
                pass

        def draw_poly(color, points, width=0):
            _draw_poly(buff, color, points, width)

        def draw_lines(color, points, width=2):
            _draw_lines(buff, color, False, points, width)

        def to_buffer(pt):
            return pt[0] - ox, pt[1] - oy

        for layer in self.data.visible_object_layers:
            for o in (o for o in layer if o.visible):
                texture_gid = getattr(o, "texture", None)
                color = getattr(o, "color", default_color)

                # BUG: this is not going to be completely accurate, because it
                # does not take into account times where texture is flipped.
                if texture_gid:
                    texture_gid = map_gid(texture_gid)[0][0]
                    texture = get_image_by_gid(int(texture_gid))

                if hasattr(o, 'points'):
                    points = [to_buffer(i) for i in o.points]
                    if o.closed:
                        if texture_gid:
                            draw_textured_poly(texture, points)
                        else:
                            draw_poly(color, points)
                    else:
                        draw_lines(color, points)

                elif o.gid:
                    tile = get_image_by_gid(o.gid)
                    if tile:
                        pt = to_buffer((o.x, o.y))
                        blit(tile, pt)

                else:
                    x, y = to_buffer((o.x, o.y))
                    points = ((x, y), (x + o.width, y),
                              (x + o.width, y + o.height), (x, y + o.height))
                    if texture_gid:
                        draw_textured_poly(texture, points)
                    else:
                        draw_poly(color, points)

    def blit_tiles(self, iterator):
        raise NotImplementedError

    def redraw(self):
        """ redraw the visible portion of the buffer -- it is slow.
        """
        queue = product(range(self.view.left, self.view.right),
                        range(self.view.top, self.view.bottom),
                        self.data.visible_tile_layers)

        self.update_queue(queue)
        self.flush()


class BufferedRenderer(RendererBase):
    """ TEST ORTHOGRAPHIC
    """
    def generate_default_image(self):
        self.default_image = pygame.Surface((self.data.tilewidth,
                                             self.data.tileheight))
        self.default_image.fill((0, 0, 0))

    def draw(self, surface, rect, surfaces=None):
        """ Draw the map onto a surface

        pass a rect that defines the draw area for:
            dirty screen update support
            drawing to an area smaller that the whole window/screen

        surfaces may optionally be passed that will be blited onto the surface.
        this must be a list of tuples containing a layer number, image, and
        rect in screen coordinates.  surfaces will be drawn in order passed,
        and will be correctly drawn with tiles from a higher layer overlapping
        the surface.
        """
        if self.blank:
            self.blank = False
            self.redraw()

        surblit = surface.blit
        left, top = self.view.topleft
        ox, oy = self.xoffset, self.yoffset
        ox -= rect.left
        oy -= rect.top

        if self.flush_on_draw:
            self.flush()

        # need to set clipping otherwise the map will draw outside its area
        original_clip = None
        if self.clipping:
            original_clip = surface.get_clip()
            surface.set_clip(rect)

        # draw the entire map to the surface,
        # taking in account the scrolling offset
        surblit(self.buffer, (-ox, -oy))

        if surfaces is None:
            dirty = list()

        else:
            def above(x, y):
                return x > y

            hit = self.layer_quadtree.hit
            get_tile = self.get_tile_image
            tile_layers = tuple(self.data.visible_tile_layers)
            dirty = [(surblit(i[0], i[1]), i[2]) for i in surfaces]

            for dirty_rect, layer in dirty:
                for r in hit(dirty_rect.move(ox, oy)):
                    x, y, tw, th = r
                    for l in [i for i in tile_layers if above(i, layer)]:
                        tile = get_tile((int(x / tw + left),
                                         int(y / th + top), int(l)))
                        if tile:
                            surblit(tile, (x - ox, y - oy))

        if self.clipping:
            surface.set_clip(original_clip)

        if self.idle:
            return [i[0] for i in dirty]
        else:
            return [rect]

    def blit_tiles(self, iterator):
        """ Bilts (x, y, layer) tuples to buffer from iterator
        """
        tw = self.data.tilewidth
        th = self.data.tileheight
        blit = self.buffer.blit
        ltw = self.view.left * tw
        tth = self.view.top * th
        get_tile = self.get_tile_image

        if self.colorkey:
            fill = self.buffer.fill
            old_tiles = set()
            for x, y, l in iterator:
                tile = get_tile((x, y, l))
                if tile:
                    if l == 0:
                        fill(self.colorkey,
                             (x * tw - ltw, y * th - tth, tw, th))
                    old_tiles.add((x, y))
                    blit(tile, (x * tw - ltw, y * th - tth))
                else:
                    if l > 0:
                        if (x, y) not in old_tiles:
                            fill(self.colorkey,
                                 (x * tw - ltw, y * th - tth, tw, th))
        else:
            for x, y, l in iterator:
                tile = get_tile((x, y, l))
                if tile:
                    blit(tile, (x * tw - ltw, y * th - tth))


class BufferedRenderer(RendererBase):
    """ TEST ISOMETRIC

    here be dragons.  lots of odd, untested, and unoptimised stuff.

    - coalescing of surfaces is not supported
    - drawing may have depth sorting issues
    - will be slower than orthographic maps for window of same size
    - consumes more memory than orthographic maps for same window size
    """
    def __init__(self, *args, **kwargs):
        super(BufferedRenderer, self).__init__(*args, **kwargs)
        if self.data.tileheight == self.data.tilewidth / 2:
            self.iso_double_height = True
        self.view = pygame.Rect(0, 0, 25, 25)

    def set_size(self, size):
        """ Set the size of the map in pixels
        """
        tw = self.data.tilewidth
        th = self.data.tileheight / 2

        buffer_width = size[0] + tw * self.padding
        buffer_height = size[1] + th * self.padding
        self.buffer = pygame.Surface((buffer_width, buffer_height))
        self.view = pygame.Rect(0, 0, math.ceil(buffer_width / tw),
                                      math.ceil(buffer_height / th))

        # this is the pixel size of the entire map
        self.rect = pygame.Rect(0, 0, self.data.width * tw,
                                      self.data.height * th)

        self.half_width = size[0] / 2
        self.half_height = size[1] / 2

        if self.colorkey:
            self.buffer.set_colorkey(self.colorkey)
            self.buffer.fill(self.colorkey)

        self.size = size
        self.idle = False
        self.blank = True
        self.xoffset = 0
        self.yoffset = 0
        self.old_x = 0
        self.old_y = 0

    def generate_default_image(self):
        self.default_image = pygame.Surface((self.data.tilewidth,
                                             self.data.tileheight))
        self.default_image.fill((0, 0, 0))

    def draw(self, surface, rect, surfaces=None):
        """ Draw the map onto a surface

        pass a rect that defines the draw area for:
            dirty screen update support
            drawing to an area smaller that the whole window/screen

        surfaces may optionally be passed that will be blited onto the surface.
        this must be a list of tuples containing a layer number, image, and
        rect in screen coordinates.  surfaces will be drawn in order passed,
        and will be correctly drawn with tiles from a higher layer overlapping
        the surface.
        """
        if self.blank:
            self.blank = False
            self.redraw()

        surblit = surface.blit
        left, top = self.view.topleft
        ox, oy = self.xoffset, self.yoffset
        ox -= rect.left
        oy -= rect.top

        w, h = self.buffer.get_size()
        ox -= rect.width / 2 - w / 2
        oy -= rect.height / 2 - h / 2

        if self.flush_on_draw:
            self.flush()

        # need to set clipping otherwise the map will draw outside its area
        original_clip = None
        if self.clipping:
            original_clip = surface.get_clip()
            surface.set_clip(rect)

        # draw the entire map to the surface,
        # taking in account the scrolling offset
        surblit(self.buffer, (-ox, -oy))

        dirty = list()

        if self.clipping:
            surface.set_clip(original_clip)

        if self.idle:
            return [i[0] for i in dirty]
        else:
            return [rect]

    def blit_tiles(self, iterator):
        """ Bilts (x, y, layer) tuples to buffer from iterator
        """
        tw = self.data.tilewidth
        th = self.data.tileheight
        blit = self.buffer.blit
        get_tile = self.get_tile_image

        bw, bh = self.buffer.get_size()
        bw /= 2
        bh /= 2

        thh = th / 2
        thw = tw / 2

        ltw = self.view.left * tw
        tth = self.view.top * th
        dxx = ltw - tth
        dyy = (ltw + tth) / 2

        for y, x in iterator:
            # unproject the screen coordinate to a map coordinate
            xx = (x * tw)
            yy = y * th / 2

            # yep
            color = (255, 0, 0)
            if y % 2:
                xx += thw
                color = (0, 255, 0)

            yyth = float(yy) / th
            xxtw = float(xx) / tw
            tx = int(yyth + xxtw)
            ty = int(yyth - xxtw)

            # get the tile that is under the point in the buffer
            tile = get_tile((tx, ty, 0))

            print x, y, xx, yy, tx, ty

            xxx = xx
            yyy = yy

            if tile:
                blit(tile, (xxx, yyy))

            pygame.draw.circle(self.buffer, color, (xxx, yyy), 2)

    def center(self, coords):
        """ center the map on a "map pixel"
        """
        x, y = [round(i, 0) for i in coords]
        hpad = int(self.padding / 2)
        tw = self.data.tilewidth
        th = self.data.tileheight

        # a hack?  i don't know.
        if self.iso_double_height:
            tw /= 2

        # calc the new offset
        ox = (x % tw)
        oy = (y % th)
        self.xoffset = ox - oy
        self.yoffset = (ox + oy) / 2

        # calc new view
        left = int(x / tw)
        top = int(y / th)

        # determine if tiles should be redrawn
        dx = int(left - hpad - self.view.left)
        dy = int(top - hpad - self.view.top)

        # adjust the offsets of the buffer
        self.xoffset += hpad * tw
        self.yoffset += hpad * th

        # adjust the view if the buffer is scrolled too far
        if (abs(dx) >= 1) or (abs(dy) >= 1):
            self.view = self.view.move((dx, dy))

            # cannot reliably use the scroll trick, so map must be redrawn
            # this is because new tiles might need to be drawn 'under' old
            # tiles, causing a many tiles that need to be redrawn
            # this just resets the drawing queue to redraw the map
            self.buffer.fill((64, 64, 64))
            self.redraw()

        self.old_x, self.old_y = x, y

    def redraw(self):
        """ redraw the visible portion of the buffer -- it is slow.
        """
        self.queue = product(range(self.view.height * 2), range(self.view.width))
        self.flush()
