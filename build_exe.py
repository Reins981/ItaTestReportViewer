import subprocess
import sys


def build_exe():
    subprocess.run([sys.executable, "setup.py", "build"])

if __name__ == '__main__':  # noqa C901
    build_exe()
