"""Regenerate all public course artifacts from original synthetic lab sources."""
import subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parent
for script in ['build_retail_course.py']:
    subprocess.run([sys.executable,str(root/script)],check=True,cwd=root.parent)
print('Built ten connected retail lessons, matched technical continuations, and five course pages.')
