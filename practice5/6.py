import re
def exercise_6():
    strings = ["one two,three.four", "hello world", "a,b.c d"]
    print("\n6. Replace space, comma, or dot with colon:")
    for s in strings:
        result = re.sub(r"[ ,.]", ":", s)
        print(f"   '{s}' -> '{result}'")

exercise_6()