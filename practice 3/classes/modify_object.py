class Car:
    def __init__(self, brand):
        self.brand = brand

c = Car("BMW")
c.brand = "Toyota"
print(c.brand)
