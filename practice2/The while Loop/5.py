n = int(input())
i = 1

while i <= n:
    if i % 3 == 0:  # Если делится на 3
        i += 1
        continue  # Пропускаем
    print(i, end=" ")
    i += 1