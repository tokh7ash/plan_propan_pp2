# ============================================================
# Practice 6 | File Handling — Writing & Appending Files
# Topics: write(), writelines(), append mode, 'x' mode
# ============================================================

import os

path = "journal.txt"

# ── 1. Write mode 'w' — creates or overwrites ────────────────
print("1. Writing with mode 'w'")
with open(path, "w") as f:
    f.write("Day 1: Started learning Python.\n")
    f.write("Day 2: Learned about lists and dicts.\n")
print("   File created.\n")

# ── 2. Append mode 'a' — adds to end ─────────────────────────
print("2. Appending with mode 'a'")
with open(path, "a") as f:
    f.write("Day 3: Mastered file handling!\n")
    f.write("Day 4: Now writing clean, Pythonic code.\n")

# Verify
with open(path, "r") as f:
    print("   Contents after append:")
    for line in f:
        print("  ", line.strip())
print()

# ── 3. writelines() — write a list of strings ────────────────
print("3. writelines() with a list")
notes = [
    "Note A: Always use 'with' for files.\n",
    "Note B: 'writelines' does NOT add newlines automatically.\n",
    "Note C: You must include \\n yourself.\n",
]
notes_path = "notes.txt"
with open(notes_path, "w") as f:
    f.writelines(notes)

with open(notes_path, "r") as f:
    print("   notes.txt contents:")
    print(f.read())

# ── 4. Exclusive creation mode 'x' ───────────────────────────
print("4. Exclusive create mode 'x'")
new_path = "new_file.txt"
try:
    with open(new_path, "x") as f:
        f.write("This file was just created fresh.\n")
    print("   new_file.txt created successfully.")
except FileExistsError:
    print("   FileExistsError: file already exists!")

# Try 'x' again — should raise error
try:
    with open(new_path, "x") as f:
        f.write("This won't work.\n")
except FileExistsError as e:
    print(f"   Caught expected error: {e}\n")

# ── 5. Writing numbers / non-strings ─────────────────────────
print("5. Writing non-string data (must convert)")
data_path = "numbers.txt"
numbers = [10, 20, 30, 40, 50]
with open(data_path, "w") as f:
    for n in numbers:
        f.write(str(n) + "\n")     # must convert int → str

with open(data_path, "r") as f:
    read_back = [int(line.strip()) for line in f]
print(f"   Written then read back: {read_back}")

# Cleanup
for p in [path, notes_path, new_path, data_path]:
    if os.path.exists(p):
        os.remove(p)
print("\n[All demo files removed]")
