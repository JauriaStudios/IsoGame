import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
						"packages": ["os", "pygame"],
						"excludes": ['_gtkagg', '_tkagg', 'bsddb', 'curses', 'email', 'pywin.debugger', 'pywin.debugger.dbgcon', 'pywin.dialogs', 'tcl', 'Tkconstants', 'Tkinter'],
						"include_files" : ["data"]
					}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None

if sys.platform == "win32":
    base = "Win32GUI"

target = Executable(
						script="main.py",
						base=base,
						targetName="IsoGame.exe",
						compress=False,
						copyDependentFiles=True,
						appendScriptToExe=True,
						appendScriptToLibrary=False,
						#icon="icon.ico",
						shortcutName="IsoGame",
						shortcutDir="DesktopFolder",
)

setup(	name = "Iso Game",
		version = "0.1",
		author="Jauria Studios",
		description = "Iso Game by Jauria Studios",
		options = {"build_exe": build_exe_options},
		executables = [target]
)
