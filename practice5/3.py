import re
def exercise_3():
    strings = ["hello_world", "foo_bar_baz", "Hello_World", "abc", "abc_DEF"]
    print("\n3. Sequences of lowercase letters joined with underscore:")
    for s in strings:
        match = re.match(r"[a-z]+(_[a-z]+)*$", s)
        print(f"   '{s}' -> {'Match: ' + match.group() if match else 'No match'}")

exercise_3()