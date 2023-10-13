import subprocess
import sys

subprocess.run([sys.executable, "-m", "pip", "freeze"], stdout=open("requirements.txt", "w"))
