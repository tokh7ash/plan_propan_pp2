class Animal:
    def sound(self):
        print("Sound")

class Cat(Animal):
    def sound(self):
        print("Meow")

Cat().sound()
