import json

with open("cars.json") as f:
    data = json.load(f)

print("Available cars:")
for item in data:
    print(f"{item['brand']} {item['model']} - ${item['price']}")

brand = input("\nEnter brand: ")
model = input("Enter model: ")

found = None
for item in data:
    if item["brand"].lower() == brand.lower() and item["model"].lower() == model.lower():
        found = item
        break

    
if not found:
    print("Sorry, this car does not exist.")
else:
    quantity = int(input("How many do you want to buy? "))
    order = {
        "brand": found["brand"],
        "model": found["model"],
        "quantity": quantity,
        "total": found["price"] * quantity
    }

    try:
        with open("orders.json") as f:
            orders = json.load(f)
    except:
        orders = []

    orders.append(order)

    with open("orders.json", "w") as f:
        json.dump(orders, f)

    print(f"{quantity} x {found['brand']} {found['model']} = ${order['total']}")

# consumer write brand and model check exist or not if exist print it if not exist soorry this 
#  покупает сколько хочет  добавить данные в новый оыщт файл 