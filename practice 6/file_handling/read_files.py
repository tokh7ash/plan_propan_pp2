# ============================================================
# Practice 6 | File Handling — Reading Files
# Topics: open(), read(), readline(), readlines(), with statement
# ============================================================

import os

# ── Setup: create a sample file to read ──────────────────────
sample_path = "sample.txt"

with open(sample_path, "w") as f:
    f.write("Line 1: Hello, Python!\n")
    f.write("Line 2: File handling is powerful.\n")
    f.write("Line 3: Always close your files.\n")
    f.write("Line 4: Or better yet, use 'with'.\n")
    f.write("Line 5: The end.\n")

print("=" * 50)
print("1. read() — entire file as one string")
print("=" * 50)
with open(sample_path, "r") as f:
    content = f.read()
    print(content)

print("=" * 50)
print("2. readline() — one line at a time")
print("=" * 50)
with open(sample_path, "r") as f:
    line = f.readline()
    while line:
        print(repr(line))   # repr shows the \n
        line = f.readline()

print("=" * 50)
print("3. readlines() — list of all lines")
print("=" * 50)
with open(sample_path, "r") as f:
    lines = f.readlines()
    for i, line in enumerate(lines, start=1):
        print(f"  [{i}] {line.strip()}")

print("=" * 50)
print("4. Iterating directly over file object")
print("=" * 50)
with open(sample_path, "r") as f:
    for line in f:
        print(" >", line.strip())

print("=" * 50)
print("5. read(n) — read only first N characters")
print("=" * 50)
with open(sample_path, "r") as f:
    chunk = f.read(20)
    print(f"First 20 chars: {chunk!r}")

# ── File modes quick reference ────────────────────────────────
print("\n── File Mode Reference ──")
modes = {
    "r":  "Read  (default) — error if file does not exist",
    "w":  "Write — creates or overwrites file",
    "a":  "Append — creates or adds to end of file",
    "x":  "Create — error if file already exists",
    "r+": "Read + Write",
    "b":  "Binary mode suffix (e.g. 'rb', 'wb')",
}
for mode, desc in modes.items():
    print(f"  '{mode}' → {desc}")

# Cleanup
os.remove(sample_path)
print("\n[sample.txt removed after demo]")
