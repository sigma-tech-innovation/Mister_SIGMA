import platform
import sys
from pathlib import Path

ROOT = Path.cwd()

def run(args):

    print("=========== SIGMA INFO ===========")
    print("Python      :", sys.version.split()[0])
    print("Platform    :", platform.system())
    print("Release     :", platform.release())
    print("Machine     :", platform.machine())
    print("Root        :", ROOT)
    print("Git         :", (ROOT/".git").exists())
    print("Workspace   :", (ROOT/".sigma-workspace").exists())
    print("Database    :", (ROOT/"sigma-db").exists())
    print("Projects    :", (ROOT/"sigma-projects").exists())
