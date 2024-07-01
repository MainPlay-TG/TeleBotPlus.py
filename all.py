#!/data/data/com.termux/files/usr/bin/python3
import os
import sys
from shutil import which
from subprocess import Popen
from time import sleep
package = "TeleBotPlus"
os.chdir(os.path.dirname(__file__))
for i in os.listdir("src"):
  if os.path.isfile(f"src/{i}/__init__.py"):
    Popen(["nano", f"src/{i}/__init__.py"]).wait()
    if which("autopep8"):
      Popen(["autopep8", "-r", "--in-place", f"src/{i}"]).wait()
Popen(["nano", "pyproject.toml"]).wait()
Popen(["poetry", "publish", "--build"]).wait()
Popen([sys.executable, "-m", "pip", "install", "-U", package]).wait()
sleep(10)
Popen([sys.executable, "-m", "pip", "install", "-U", package]).wait()
