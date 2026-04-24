import re
def exercise_2():
    patterns = ["ab", "abb", "abbb", "abbbb"]
    print("\n2. 'a' followed by two to three 'b's:")
    for p in patterns:
        match = re.match(r"ab{2,3}", p)
        print(f"   '{p}' -> {'Match: ' + match.group() if match else 'No match'}")

exercise_2()