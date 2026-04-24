import re
def exercise_9():
    strings = ["CamelCaseString", "HelloWorld", "PythonIsGreat"]
    print("\n9. Insert spaces between capital-letter words:")
    for s in strings:
        result = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", s)
        print(f"   '{s}' -> '{result}'")

exercise_9()
