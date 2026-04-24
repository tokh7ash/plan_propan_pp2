import re
def exercise_7():
    strings = ["hello_world", "foo_bar_baz", "python_is_great"]
    print("\n7. Snake case to camel case:")
    for s in strings:
        result = re.sub(r"_([a-z])", lambda m: m.group(1).upper(), s)
        print(f"   '{s}' -> '{result}'")

exercise_7()