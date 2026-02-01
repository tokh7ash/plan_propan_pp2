list1 = ["apple", "banana", "cherry"]
list2 = [1, 5, 7, 9, 3]
list3 = [True, False, False]

mylist = ["apple", "banana", "cherry"]
print(type(mylist))

thislist1 = list(("apple", "banana", "cherry"))
print(thislist1)

thislist2 = ["apple", "banana", "cherry"]
if "apple" in thislist2:
  print("Yes, 'apple' is in the fruits list")

thislist3 = ["apple", "banana", "cherry", "orange", "kiwi", "melon", "mango"]
print(thislist3[2:5])  #The search will start at index 2 (included) and end at index 5 (not included).
print(thislist3[:4])#This example returns the items from the beginning to, but NOT including, "kiwi":
print(thislist3[2:])#This example returns the items from "cherry" to the end:
print(thislist3[-4:-1])#This example returns the items from "orange" (-4) to, but NOT including "mango" (-1):


thislist = ["apple", "banana", "cherry", "orange", "kiwi", "mango"]
thislist[1:3] = ["blackcurrant", "watermelon"] #3 не берется
print(thislist)

thislist5 = ["apple", "banana", "cherry"]
thislist5.insert(2, "watermelon")
print(thislist5)
