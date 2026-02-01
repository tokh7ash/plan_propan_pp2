secret = 5

while True:
    guess = int(input())
    if guess == secret:
        print("Correct!")
        break  # Выходим, когда угадали
    else:
        print("Try again")