#1
def square_generator(N):
    for i in range(1, N + 1):
        yield i ** 2

gen = square_generator(5)

print(next(gen)) 
print(next(gen)) 
print(next(gen))  
for square in square_generator(5):
    print(square)


#2
def even_generator(n):
    for i in range(0, n + 1, 2):
        yield i

n = int(input("Enter n: "))

gen = iter(even_generator(n))

result = ""
while True:
    try:
        num = next(gen)
        result += str(num) + ", "
    except StopIteration:
        break

print(result.rstrip(", "))


#3
def divisible_generator(n):
    for i in range(0, n + 1):
        if i % 3 == 0 and i % 4 == 0:
            yield i

n = int(input("Enter n: "))

gen = iter(x for x in divisible_generator(n))

while True:
    try:
        print(next(gen))
    except StopIteration:
        break

#4
def squares(a, b):
    for i in range(a, b + 1):
        yield i ** 2

a = int(input("Enter a: "))
b = int(input("Enter b: "))

gen = iter(x for x in squares(a, b))

while True:
    try:
        print(next(gen))
    except StopIteration:
        break

#5
def countdown(n):
    for i in range(n, -1, -1):
        yield i

n = int(input("Enter n: "))

gen = iter(x for x in countdown(n))

while True:
    try:
        print(next(gen))
    except StopIteration:
        break