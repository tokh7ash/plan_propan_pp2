#  divice brand model divice info  smartphone additional atribute like storage   laptope os ram 
class Device:
    def _init_(self,brand,model):
       self.brand = brand
       self.model = model

    def info(self):
       print(f"{self.brand},{self.model}")

class Smartphone(Device):
    def __init__(self, brand, model, storage):
        super()._init_(brand, model)
        self.storage = storage

    def info(self):
        print(f"smartphone: {self.brand} {self.model}, storage: {self.storage}gb")
    

class Laptop(Device):
    def __init__(self, brand, model, os, ram):
        super()._init_(brand, model)
        self.os = os
        self.ram = ram

    def info(self):
        print(f"Laptop: {self.brand} {self.model}, OS: {self.os},RAM: {self.ram}gb")

phone = Smartphone("Samsung", "Galaxy S24", 256)
phone.info()

laptop = Laptop("Apple", "MacBook Pro", "macOS", 16)
laptop.info()