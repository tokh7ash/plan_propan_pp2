import re
def exercise_4():
    strings = ["Hello", "World", "hEllo", "HELLO", "Python3"]
    print("\n4. One uppercase letter followed by lowercase letters:")
    for s in strings:
        matches = re.findall(r"[A-Z][a-z]+", s)
        print(f"   '{s}' -> {matches if matches else 'No match'}")
exercise_4()