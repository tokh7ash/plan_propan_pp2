import re
def exercise_10():
    strings = ["camelCaseString", "helloWorld", "pythonIsGreat"]
    print("\n10. Camel case to snake case:")
    for s in strings:
        result = re.sub(r"([A-Z])", lambda m: "_" + m.group(1).lower(), s)
        print(f"   '{s}' -> '{result}'")

exercise_10()