thislist = ["apple", "banana", "cherry"]
thislist.append("orange")
print(thislist)


thislist1 = ["apple", "banana", "cherry"]
tropical = ["mango", "pineapple", "papaya"]
thislist1.extend(tropical)
print(thislist1)

thislist2 = ["apple", "banana", "cherry"]
thistuple = ("kiwi", "orange")
thislist2.extend(thistuple)
print(thislist2)


thislist3 = ["apple", "banana", "cherry", "banana", "kiwi"]
thislist3.remove("banana")
print(thislist3)

thislist4 = ["apple", "banana", "cherry"]
thislist4.pop(1)
print(thislist4)#by index

thislist5 = ["apple", "banana", "cherry"]
thislist5.pop()
print(thislist5)#If you do not specify the index, the pop() method removes the last item.

thislist6 = ["apple", "banana", "cherry"]
del thislist6[0]
print(thislist6)

thislist7 = ["apple", "banana", "cherry"]
thislist7.clear()
print(thislist7)


