# ============================================================
# Practice 6 | Directory Management
# Topics: os.mkdir, os.makedirs, os.listdir, os.getcwd,
#         os.chdir, os.rmdir, os.walk, pathlib.Path
# ============================================================

import os
import shutil
from pathlib import Path

print("=" * 50)
print("1. os.getcwd() — current working directory")
print("=" * 50)
print(f"   CWD: {os.getcwd()}")

print("=" * 50)
print("2. os.mkdir() — create a single directory")
print("=" * 50)
os.mkdir("projects")
print("   projects/ created")

print("=" * 50)
print("3. os.makedirs() — create nested directories at once")
print("=" * 50)
os.makedirs("projects/2024/python/week6", exist_ok=True)
os.makedirs("projects/2024/python/week7", exist_ok=True)
os.makedirs("projects/2024/web/html",     exist_ok=True)
print("   Nested structure created under projects/")

# Add sample files
for fname in ["main.py", "utils.py", "README.md"]:
    Path(f"projects/2024/python/week6/{fname}").write_text(f"# {fname}\n")
for fname in ["index.html", "style.css"]:
    Path(f"projects/2024/web/html/{fname}").write_text(f"<!-- {fname} -->\n")

print("=" * 50)
print("4. os.listdir() — list contents of a directory")
print("=" * 50)
for entry in os.listdir("projects/2024/python/week6"):
    full = os.path.join("projects/2024/python/week6", entry)
    kind = "DIR " if os.path.isdir(full) else "FILE"
    print(f"   [{kind}] {entry}")

print("=" * 50)
print("5. os.walk() — recursive directory traversal")
print("=" * 50)
for root, dirs, files in os.walk("projects"):
    level = root.replace("projects", "").count(os.sep)
    indent = "  " * level
    print(f"{indent}{os.path.basename(root)}/")
    for file in files:
        print(f"{indent}  {file}")

print("=" * 50)
print("6. Find files by extension (.py files only)")
print("=" * 50)
py_files = []
for root, dirs, files in os.walk("projects"):
    for f in files:
        if f.endswith(".py"):
            py_files.append(os.path.join(root, f))
for p in py_files:
    print(f"   {p}")

print("=" * 50)
print("7. pathlib.Path — modern, object-oriented paths")
print("=" * 50)
base = Path("projects")
print(f"   exists : {base.exists()}")
print(f"   is_dir : {base.is_dir()}")

# Glob for all .html files
html_files = list(base.rglob("*.html"))
print(f"   .html files found: {[str(p) for p in html_files]}")

# Path joining
week6 = base / "2024" / "python" / "week6"
print(f"   Joined path: {week6}")
print(f"   Parent     : {week6.parent}")

print("=" * 50)
print("8. os.rmdir() — remove empty directory")
print("=" * 50)
os.makedirs("empty_dir/subdir", exist_ok=True)
os.rmdir("empty_dir/subdir")   # must be empty
os.rmdir("empty_dir")
print("   empty_dir/ removed (it was empty)")
print("   Note: os.rmdir() fails if directory is not empty")

# Cleanup
shutil.rmtree("projects")
print("\n[projects/ tree removed — cleanup complete]")
