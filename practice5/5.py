import re
def exercise_5():
    strings = ["aXYZb", "ab", "acb", "a123b", "abc"]
    print("\n5. 'a' followed by anything, ending in 'b':")
    for s in strings:
        match = re.match(r"a.*b$", s)
        print(f"   '{s}' -> {'Match: ' + match.group() if match else 'No match'}")
        
exercise_5()