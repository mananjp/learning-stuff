import math
from tkinter import *
import math as m
root = Tk()

root.title("Calculator")

e1  = Entry(root)
e1.insert(0, "enter no 1")
e = Entry(root)
e.insert(0, "give operator")
e2 = Entry(root)
e2.insert(0, "enter no 2")
er = Entry(root)
e.grid(row=2, column=1, padx=10, pady=10)
e1.grid(row=0, column=1, padx=10, pady=10)
e2.grid(row=4, column=1, padx=10, pady=10)
er.grid(row=6, column=1, padx=10, pady=10)
def calc():
    E1 = e1.get()
    E2 = e2.get()
    op = e.get()
    if op == "+":
        return er.insert(1, int(E1) + int(E2))
    elif op == "-":
        return er.insert(1, int(E1) - int(E2))
    elif op == "x":
        return er.insert(1, int(E1) * int(E2))
    elif op == "/":
        return er.insert(1, int(E1) / int(E2))
    elif op == "%":
        return er.insert(1, int(E1) % int(E2))

def clear():
    e1.delete(0, END)
    e2.delete(0, END)
    er.delete(0, END)
    e.delete(0, END)
def sqrt():
    return er.insert(1, float(math.sqrt(int(e1.get()))))
calculate = Button(root, text="Calculate", command=calc)
clear = Button(root, text="Clear", command=clear)
calculate.grid(row=8, column=1, padx=10, pady=10)
clear.grid(row=8, column=0, padx=10, pady=10)
sqrt = Button(root, text="Square root", command=sqrt)
sqrt.grid(row=9, column=1, padx=10, pady=10)
root.mainloop()