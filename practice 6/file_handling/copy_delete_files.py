# ============================================================
# Practice 6 | File Handling — Copy, Backup & Delete Files
# Topics: shutil.copy(), shutil.copy2(), shutil.move(),
#         os.remove(), os.rename(), os.path helpers
# ============================================================

import os
import shutil

# ── Setup ─────────────────────────────────────────────────────
os.makedirs("backup", exist_ok=True)
original = "data.txt"

with open(original, "w") as f:
    f.write("Record 1: Alice, 85\n")
    f.write("Record 2: Bob,   92\n")
    f.write("Record 3: Carol, 78\n")

print("=" * 50)
print("1. shutil.copy()  — copy content only")
print("=" * 50)
shutil.copy(original, "data_copy.txt")
print("   data_copy.txt created")

print("=" * 50)
print("2. shutil.copy2() — copy content + metadata (timestamps)")
print("=" * 50)
shutil.copy2(original, "backup/data_backup.txt")
print("   backup/data_backup.txt created (with metadata)")

print("=" * 50)
print("3. shutil.move() — move / rename a file")
print("=" * 50)
shutil.copy(original, "temp.txt")
shutil.move("temp.txt", "backup/temp_moved.txt")
print("   temp.txt moved → backup/temp_moved.txt")

print("=" * 50)
print("4. os.rename() — rename in same directory")
print("=" * 50)
shutil.copy(original, "old_name.txt")
os.rename("old_name.txt", "new_name.txt")
print("   old_name.txt → new_name.txt")

print("=" * 50)
print("5. os.path helpers")
print("=" * 50)
for p in [original, "backup/data_backup.txt"]:
    print(f"\n  Path : {p}")
    print(f"  exists  : {os.path.exists(p)}")
    print(f"  isfile  : {os.path.isfile(p)}")
    print(f"  isdir   : {os.path.isdir(p)}")
    print(f"  basename: {os.path.basename(p)}")
    print(f"  dirname : {os.path.dirname(p)}")
    print(f"  abspath : {os.path.abspath(p)}")
    size = os.path.getsize(p)
    print(f"  size    : {size} bytes")

print("=" * 50)
print("6. Safe delete with os.remove()")
print("=" * 50)
to_delete = ["data_copy.txt", "new_name.txt"]
for p in to_delete:
    if os.path.exists(p):
        os.remove(p)
        print(f"   Deleted: {p}")
    else:
        print(f"   Not found (already gone): {p}")

print("=" * 50)
print("7. Delete entire directory tree with shutil.rmtree()")
print("=" * 50)
shutil.rmtree("backup")
print("   backup/ directory and all contents removed")

os.remove(original)
print(f"   {original} removed")
print("\n[Cleanup complete]")
