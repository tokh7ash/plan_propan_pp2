# ============================================================
# Practice 6 | Directory Management — Move & Copy Files
# Topics: shutil.move(), shutil.copytree(), os.scandir(),
#         organizing files by extension
# ============================================================

import os
import shutil
from pathlib import Path

# ── Setup: create a messy folder ─────────────────────────────
os.makedirs("messy", exist_ok=True)
sample_files = [
    ("report.pdf",   "PDF content"),
    ("photo1.jpg",   "JPEG data"),
    ("photo2.jpg",   "JPEG data"),
    ("notes.txt",    "Some notes"),
    ("data.csv",     "a,b,c\n1,2,3\n"),
    ("script.py",    "print('hello')"),
    ("archive.zip",  "ZIP data"),
    ("readme.txt",   "Read me!"),
]
for name, content in sample_files:
    Path(f"messy/{name}").write_text(content)

print("Initial messy/ contents:")
for f in os.listdir("messy"):
    print(f"  {f}")

# ── 1. Organize files by extension ───────────────────────────
print("\n1. Organizing files by extension into sorted/")
ext_map = {
    ".pdf":  "sorted/documents",
    ".jpg":  "sorted/images",
    ".jpeg": "sorted/images",
    ".png":  "sorted/images",
    ".txt":  "sorted/text",
    ".csv":  "sorted/data",
    ".py":   "sorted/scripts",
    ".zip":  "sorted/archives",
}

for filename in os.listdir("messy"):
    src = os.path.join("messy", filename)
    if not os.path.isfile(src):
        continue
    ext = os.path.splitext(filename)[1].lower()
    dest_dir = ext_map.get(ext, "sorted/other")
    os.makedirs(dest_dir, exist_ok=True)
    shutil.move(src, os.path.join(dest_dir, filename))
    print(f"   Moved {filename} → {dest_dir}/")

# ── 2. List final sorted structure ───────────────────────────
print("\n2. Final sorted/ structure:")
for root, dirs, files in os.walk("sorted"):
    level = root.replace("sorted", "").count(os.sep)
    indent = "  " * level
    print(f"{indent}{os.path.basename(root)}/")
    for f in files:
        print(f"{indent}  {f}")

# ── 3. shutil.copytree() — copy entire directory tree ────────
print("\n3. shutil.copytree() — duplicate full sorted/ tree")
shutil.copytree("sorted", "sorted_backup")
print("   sorted_backup/ created")
py_backup = list(Path("sorted_backup").rglob("*.py"))
print(f"   .py files in backup: {[str(p) for p in py_backup]}")

# ── 4. os.scandir() — efficient directory scanning ───────────
print("\n4. os.scandir() on sorted/images/")
images_dir = "sorted/images"
if os.path.exists(images_dir):
    with os.scandir(images_dir) as entries:
        for entry in entries:
            stat = entry.stat()
            print(f"   {entry.name:15s}  isfile={entry.is_file()}  size={stat.st_size}B")

# ── 5. Move back and rename ───────────────────────────────────
print("\n5. Moving a file and renaming it simultaneously")
src  = "sorted/text/notes.txt"
dest = "sorted/text/notes_renamed.txt"
if os.path.exists(src):
    shutil.move(src, dest)
    print(f"   notes.txt → notes_renamed.txt")

# Cleanup
shutil.rmtree("messy",          ignore_errors=True)
shutil.rmtree("sorted",         ignore_errors=True)
shutil.rmtree("sorted_backup",  ignore_errors=True)
print("\n[All demo directories removed — cleanup complete]")
