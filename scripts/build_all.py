"""Regenerate all public course artifacts from original synthetic lab sources."""
import subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parent
for script in ['build_lessons_1_3.py','build_lessons_4_6.py','build_lessons_7_10.py','build_course_pages.py']:
    subprocess.run([sys.executable,str(root/script)],check=True,cwd=root.parent)
print('Built ten synthetic lessons and five course pages.')
