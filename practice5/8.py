import re
def exercise_8():
    strings = ["CamelCaseString", "HelloWorld", "PythonRegEx"]
    print("\n8. Split string at uppercase letters:")
    for s in strings:
        result = re.split(r"(?=[A-Z])", s)
        result = [word for word in result if word]  # Remove empty strings
        print(f"   '{s}' -> {result}")

exercise_8()