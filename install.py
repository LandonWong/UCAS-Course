import sys
from cx_Freeze import setup, Executable

build_exe_options = {"packages": ["os", "pkg_resources", "idna"],
                     "excludes": ["tkinter"],
                     "include_files": ["user.txt", "README.md", "ui/", "template_ui/"]}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(name="Test",
      version='1.0',
      description="Python Test",
      options={"build_exe": build_exe_options},
      executables=[Executable("main.py", base=base)])
