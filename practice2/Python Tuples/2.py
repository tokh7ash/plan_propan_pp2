#in Python, 
# we are also allowed to extract the values back into variables. This is called "unpacking":
fruits = ("apple", "banana", "cherry")

(green, yellow, red) = fruits

print(green)
print(yellow)
print(red)

fruits = ("apple", "banana", "cherry", "strawberry", "raspberry")

(green, yellow, *red) = fruits#If the number of variables is less than the number of values, you can add an * to the variable name and the values will be assigned to the variable as a list:

print(green)
print(yellow)
print(red)

