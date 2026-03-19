# ============================================================
# Practice 6 | Built-in Functions — map, filter, reduce
# Topics: map(), filter(), reduce(), lambda, type conversions,
#         len(), sum(), min(), max(), sorted(), abs(), round()
# ============================================================

from functools import reduce

print("=" * 55)
print("BASIC AGGREGATION: len, sum, min, max")
print("=" * 55)
scores = [88, 74, 95, 61, 99, 82, 70]
print(f"Scores : {scores}")
print(f"len()  : {len(scores)}")
print(f"sum()  : {sum(scores)}")
print(f"min()  : {min(scores)}")
print(f"max()  : {max(scores)}")
print(f"avg    : {sum(scores) / len(scores):.2f}")

# Works on strings too
words = ["banana", "apple", "cherry", "date"]
print(f"\nWords      : {words}")
print(f"min(words) : {min(words)}  ← alphabetically first")
print(f"max(words) : {max(words)}  ← alphabetically last")

# ── map() ─────────────────────────────────────────────────────
print("\n" + "=" * 55)
print("map() — transform every element")
print("=" * 55)

# Example 1: square each number
numbers = [1, 2, 3, 4, 5]
squares = list(map(lambda x: x ** 2, numbers))
print(f"Original : {numbers}")
print(f"Squares  : {squares}")

# Example 2: convert strings to uppercase
names = ["alice", "bob", "carol"]
upper = list(map(str.upper, names))
print(f"\nNames  : {names}")
print(f"Upper  : {upper}")

# Example 3: convert strings to integers
str_nums = ["10", "20", "30", "40"]
int_nums = list(map(int, str_nums))
print(f"\nstr_nums : {str_nums}")
print(f"int_nums : {int_nums}  ← map(int, ...)")

# Example 4: map with two iterables
a = [1, 2, 3]
b = [10, 20, 30]
sums = list(map(lambda x, y: x + y, a, b))
print(f"\na + b element-wise: {sums}")

# ── filter() ──────────────────────────────────────────────────
print("\n" + "=" * 55)
print("filter() — keep elements that pass a test")
print("=" * 55)

# Example 1: keep even numbers
nums = list(range(1, 11))
evens = list(filter(lambda x: x % 2 == 0, nums))
print(f"1-10       : {nums}")
print(f"Evens only : {evens}")

# Example 2: filter out empty strings
items = ["apple", "", "banana", "  ", "cherry", ""]
non_empty = list(filter(None, items))           # filter(None,...) removes falsy
non_blank  = list(filter(str.strip, items))     # removes blank/whitespace strings
print(f"\nItems      : {items}")
print(f"filter(None): {non_empty}")
print(f"Non-blank  : {non_blank}")

# Example 3: students who passed
students = [("Alice", 88), ("Bob", 45), ("Carol", 72), ("Dave", 39)]
passed = list(filter(lambda s: s[1] >= 50, students))
print(f"\nAll students : {students}")
print(f"Passed (≥50) : {passed}")

# ── reduce() ──────────────────────────────────────────────────
print("\n" + "=" * 55)
print("reduce() — fold a list into a single value")
print("=" * 55)

# Example 1: product of all numbers
nums = [1, 2, 3, 4, 5]
product = reduce(lambda acc, x: acc * x, nums)
print(f"Product of {nums} = {product}")

# Example 2: find the maximum manually
maximum = reduce(lambda a, b: a if a > b else b, nums)
print(f"Max of {nums} via reduce = {maximum}")

# Example 3: concatenate strings
words = ["Python", "is", "awesome"]
sentence = reduce(lambda a, b: a + " " + b, words)
print(f"Joined: '{sentence}'")

# Example 4: running total with initial value
totals = reduce(lambda acc, x: acc + x, [10, 20, 30], 100)  # starts at 100
print(f"Sum with initial=100: {totals}")

# ── sorted() ──────────────────────────────────────────────────
print("\n" + "=" * 55)
print("sorted() — flexible sorting")
print("=" * 55)

data = [5, 2, 8, 1, 9, 3]
print(f"Original  : {data}")
print(f"Ascending : {sorted(data)}")
print(f"Descending: {sorted(data, reverse=True)}")

students = [("Alice", 88), ("Bob", 45), ("Carol", 72)]
by_score = sorted(students, key=lambda s: s[1], reverse=True)
print(f"\nBy score (desc): {by_score}")

# ── Type conversions ──────────────────────────────────────────
print("\n" + "=" * 55)
print("Type conversion functions")
print("=" * 55)
print(f"int('42')     = {int('42')!r}")
print(f"float('3.14') = {float('3.14')!r}")
print(f"str(100)      = {str(100)!r}")
print(f"bool(0)       = {bool(0)!r}")
print(f"bool(1)       = {bool(1)!r}")
print(f"list((1,2,3)) = {list((1,2,3))!r}")
print(f"tuple([1,2,3])= {tuple([1,2,3])!r}")
print(f"set([1,1,2,3])= {set([1,1,2,3])!r}")

# type checking
values = [42, 3.14, "hello", True, [1, 2]]
print("\ntype() checks:")
for v in values:
    print(f"  {str(v):10s}  → {type(v).__name__}")
