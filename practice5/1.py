import re
def exercise_1():
    patterns = ["ac", "abc", "abbc", "a", "ab"]
    print("1. 'a' followed by zero or more 'b's:")
    for p in patterns:
        match = re.match(r"ab*", p)
        print(f"   '{p}' -> {'Match: ' + match.group() if match else 'No match'}")

exercise_1()