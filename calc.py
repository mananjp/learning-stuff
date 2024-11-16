import math
from tkinter import *


root = Tk()
root.title("Calculator")

e1 = Entry(root)
e1.insert(0, "Enter number 1")
e = Entry(root)
e.insert(0, "Operator (+, -, x, /, %, sqrt, ln)")
e2 = Entry(root)
e2.insert(0, "Enter number 2 (if needed)")
er = Entry(root)
er.insert(0, "Result will be shown here")


e1.grid(row=0, column=1, padx=15, pady=10)
e.grid(row=2, column=1, padx=15, pady=10)
e2.grid(row=4, column=1, padx=15, pady=10)
er.grid(row=6, column=1, padx=15, pady=10)


# Calculation function
def calc():
    try:
        E1 = e1.get()
        E2 = e2.get()
        op = e.get()

        num1 = float(E1) if E1 else 0
        num2 = float(E2) if E2 else 0

        if op == "+":
            result = num1 + num2
        elif op == "-":
            result = num1 - num2
        elif op == "x":
            result = num1 * num2
        elif op == "/":
            if num2 == 0:
                result = "Error: Division by Zero"
            else:
                result = num1 / num2
        elif op == "%":
            result = num1 % num2
        elif op == "sqrt":

            result = math.sqrt(num1)

        elif op == "ln":
            if num1 <= 0:
                result = "Error: Invalid input for ln"
            else:

                result = math.log(num1)

        elif op == "pow":
             a = 1
             for i in range(0, int(num2)):
                 a = a*num1
             result = a
        else:
            result = "Invalid operator"



        er.delete(0, END)
        er.insert(1, result)

    except ValueError:
        er.delete(0, END)
        er.insert(1, "Error: Invalid input")



def clear():
    e1.delete(0, END)
    e2.delete(0, END)
    er.delete(0, END)
    e.delete(0, END)
    e1.insert(0, "Enter number 1")
    e2.insert(0, "Enter number 2 (if needed)")
    e.insert(0, "Operator (+, -, x, /, %, sqrt, ln, pow)")



calculate = Button(root, text="Calculate", command=calc)
clear_button = Button(root, text="Clear", command=clear)
calculate.grid(row=8, column=1, padx=10, pady=10)
clear_button.grid(row=8, column=0, padx=10, pady=10)



root.mainloop()
