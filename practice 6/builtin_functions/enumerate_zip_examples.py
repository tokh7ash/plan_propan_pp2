# ============================================================
# Practice 6 | Built-in Functions — enumerate & zip
# Topics: enumerate(), zip(), zip_longest(), unpacking,
#         paired iteration patterns
# ============================================================

from itertools import zip_longest

# ── enumerate() ───────────────────────────────────────────────
print("=" * 55)
print("enumerate() — loop with index + value")
print("=" * 55)

fruits = ["apple", "banana", "cherry", "date", "elderberry"]

# Without enumerate (old way)
print("\nWithout enumerate:")
for i in range(len(fruits)):
    print(f"  {i}: {fruits[i]}")

# With enumerate (Pythonic)
print("\nWith enumerate:")
for i, fruit in enumerate(fruits):
    print(f"  {i}: {fruit}")

# Custom start index
print("\nenumerate(start=1):")
for i, fruit in enumerate(fruits, start=1):
    print(f"  {i}. {fruit}")

# Practical: find index of items matching a condition
print("\nFind items with length > 5:")
long_fruits = [(i, f) for i, f in enumerate(fruits) if len(f) > 5]
print(f"  {long_fruits}")

# Practical: numbered menu
print("\nMenu:")
menu = ["New Game", "Load Game", "Settings", "Quit"]
for i, option in enumerate(menu, start=1):
    print(f"  [{i}] {option}")

# ── zip() ─────────────────────────────────────────────────────
print("\n" + "=" * 55)
print("zip() — pair elements from multiple iterables")
print("=" * 55)

names  = ["Alice", "Bob",   "Carol", "Dave"]
scores = [88,      74,      95,      61]
grades = ["B+",    "C",     "A",     "D+"]

print("\nBasic zip (names + scores):")
for name, score in zip(names, scores):
    print(f"  {name:8s} scored {score}")

print("\nTriple zip (names + scores + grades):")
for name, score, grade in zip(names, scores, grades):
    print(f"  {name:8s} → {score}  ({grade})")

# zip stops at shortest iterable
print("\nzip stops at shortest:")
short = [1, 2]
long  = ["a", "b", "c", "d"]
print(f"  zip result: {list(zip(short, long))}")  # only 2 pairs

# zip_longest pads with None (or fillvalue)
print("\nzip_longest pads missing values:")
padded = list(zip_longest(short, long, fillvalue="?"))
print(f"  {padded}")

# ── zip for creating dicts ────────────────────────────────────
print("\n" + "=" * 55)
print("zip → dict")
print("=" * 55)
keys   = ["name", "age", "city"]
values = ["Alice", 30, "Almaty"]
person = dict(zip(keys, values))
print(f"  {person}")

# ── Transposing a matrix with zip(*matrix) ────────────────────
print("\n" + "=" * 55)
print("zip(*matrix) — transpose rows ↔ columns")
print("=" * 55)
matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
]
print("Original:")
for row in matrix:
    print(f"  {row}")

transposed = list(map(list, zip(*matrix)))
print("Transposed:")
for row in transposed:
    print(f"  {row}")

# ── Combining enumerate + zip ─────────────────────────────────
print("\n" + "=" * 55)
print("enumerate + zip together")
print("=" * 55)
teams = ["Team A", "Team B", "Team C"]
wins  = [12, 9, 7]
losses = [3, 6, 8]

print("  #  Team     W   L")
print("  " + "-" * 25)
for i, (team, w, l) in enumerate(zip(teams, wins, losses), start=1):
    print(f"  {i}  {team:8s} {w:3d} {l:3d}")

# ── unzip with zip(*...) ──────────────────────────────────────
print("\n" + "=" * 55)
print("Unzipping paired data with zip(*...)")
print("=" * 55)
pairs = [(1, "one"), (2, "two"), (3, "three")]
numbers, words = zip(*pairs)
print(f"  pairs   : {pairs}")
print(f"  numbers : {numbers}")
print(f"  words   : {words}")
