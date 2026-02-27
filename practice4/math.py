import math
import random

#1 
degree = float(input("Input degree: "))
radian = degree * (math.pi / 180)
print("Output radian:", round(radian, 6))

#2 
h = float(input("Height: "))
b1 = float(input("Base, first value: "))
b2 = float(input("Base, second value: "))
trapezoid_area = 0.5 * (b1 + b2) * h
print("Expected Output:", trapezoid_area)

#3
n = int(input("Input number of sides: "))
s = float(input("Input the length of a side: "))
polygon_area = (n * pow(s, 2)) / (4 * math.tan(math.pi / n))
print("The area of the polygon is:", round(polygon_area))

#4
base = float(input("Length of base: "))
height = float(input("Height of parallelogram: "))
parallelogram_area = base * height
print("Expected Output:", parallelogram_area)