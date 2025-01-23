import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime


class FinancialApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Financial Management System")
        self.root.geometry("800x600")

        self.frames = {}
        self.user_id = None

        self.frames["login"] = self.create_login_page()
        self.frames["register"] = self.create_register_page()
        self.frames["transaction_dashboard"] = self.create_transaction_dashboard()
        self.frames["financial_summary"] = self.create_summary_page()
        self.frames["financial_literacy"] = self.create_financial_literacy_page()

        self.show_frame("login")

    def show_frame(self, frame_name):
        for frame in self.frames.values():
            frame.place_forget()
        self.frames[frame_name].place(relwidth=1, relheight=1)

    def create_login_page(self):
        frame = tk.Frame(self.root)

        tk.Label(frame, text="Login", font=("Arial", 20)).pack(pady=20)

        tk.Label(frame, text="Username:").pack()
        self.login_username_entry = tk.Entry(frame)
        self.login_username_entry.pack()

        tk.Label(frame, text="Password:").pack()
        self.login_password_entry = tk.Entry(frame, show="*")
        self.login_password_entry.pack()

        tk.Button(frame, text="Login", command=self.login).pack(pady=10)
        tk.Button(frame, text="Register", command=lambda: self.show_frame("register")).pack(pady=10)

        return frame

    def create_register_page(self):
        frame = tk.Frame(self.root)

        tk.Label(frame, text="Register", font=("Arial", 20)).pack(pady=20)

        tk.Label(frame, text="Username:").pack()
        self.register_username_entry = tk.Entry(frame)
        self.register_username_entry.pack()

        tk.Label(frame, text="Password:").pack()
        self.register_password_entry = tk.Entry(frame, show="*")
        self.register_password_entry.pack()

        tk.Button(frame, text="Register", command=self.register).pack(pady=10)
        tk.Button(frame, text="Back to Login", command=lambda: self.show_frame("login")).pack(pady=10)

        return frame

    def create_transaction_dashboard(self):
        frame = tk.Frame(self.root)

        tk.Label(frame, text="Transaction Dashboard", font=("Arial", 20)).pack(pady=10)

        tk.Label(frame, text="Transaction Class:").pack()
        self.transaction_class_entry = tk.Entry(frame)
        self.transaction_class_entry.pack()

        tk.Label(frame, text="Amount:").pack()
        self.transaction_amount_entry = tk.Entry(frame)
        self.transaction_amount_entry.pack()

        tk.Label(frame, text="Transaction Type:").pack()
        self.transaction_type_var = tk.StringVar(value="Credit")
        tk.Radiobutton(frame, text="Credit", variable=self.transaction_type_var, value="Credit").pack()
        tk.Radiobutton(frame, text="Debit", variable=self.transaction_type_var, value="Debit").pack()

        tk.Button(frame, text="Add Transaction", command=self.add_transaction).pack(pady=10)
        tk.Button(frame, text="View Summary",
                  command=lambda: [self.update_summary_page(), self.show_frame("financial_summary")]).pack(pady=10)
        tk.Button(frame, text="Financial Literacy", command=lambda: self.show_frame("financial_literacy")).pack(pady=10)
        tk.Button(frame, text="Logout", command=lambda: self.show_frame("login")).pack(pady=10)
        tk.Button(frame, text="Quit", command=self.root.quit).pack(pady=10)

        return frame

    def create_summary_page(self):
        frame = tk.Frame(self.root)

        tk.Label(frame, text="Financial Summary", font=("Arial", 20)).pack(pady=10)

        tree_frame = tk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(tree_frame, yscrollcommand=scrollbar.set, show="headings")
        self.tree["columns"] = ("ID", "Class", "Amount", "GST", "Income Tax", "Total", "Transaction Type", "Timestamp")

        self.tree.heading("ID", text="ID")
        self.tree.heading("Class", text="Transaction Class")
        self.tree.heading("Amount", text="Amount")
        self.tree.heading("GST", text="GST")
        self.tree.heading("Income Tax", text="Income Tax")
        self.tree.heading("Total", text="Total")
        self.tree.heading("Transaction Type", text="Type")
        self.tree.heading("Timestamp", text="Timestamp")

        self.tree.column("ID", width=50)
        self.tree.column("Class", width=150)
        self.tree.column("Amount", width=100)
        self.tree.column("GST", width=100)
        self.tree.column("Income Tax", width=100)
        self.tree.column("Total", width=100)
        self.tree.column("Transaction Type", width=150)
        self.tree.column("Timestamp", width=200)

        self.tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)

        self.total_gst_label = tk.Label(frame, text="Total GST: ₹0.00", font=("Arial", 14))
        self.total_gst_label.pack(pady=5)

        self.total_income_tax_label = tk.Label(frame, text="Total Income Tax: ₹0.00", font=("Arial", 14))
        self.total_income_tax_label.pack(pady=5)

        tk.Button(frame, text="Show Pie Charts of Credit and Debit", command=self.show_pie_charts).pack(pady=10)
        tk.Button(frame, text="Delete Selected Transaction", command=self.delete_transaction).pack(pady=10)
        tk.Button(frame, text="Back to Transaction Dashboard", command=lambda: self.show_frame("transaction_dashboard")).pack(pady=10)

        return frame

    def create_financial_literacy_page(self):
        frame = tk.Frame(self.root)

        tk.Label(frame, text="Financial Literacy", font=("Arial", 20)).pack(pady=10)

        literacy_text = """
        Financial Literacy:
        Income tax slabs (FY-24/25)(Rs)          Income tax rate (%)
        From 0 to 3,00,000                                      0
        From 3,00,001 to 7,00,000                         5
        From 7,00,001 to 10,00,000                      10
        From 10,00,001 to 12,00,000                    15
        From 12,00,001 to 15,00,000                    20
        From 15,00,001 and above                        30
        
        
The primary GST slabs for regular taxpayers are currently 0% (nil-rated), 5%, 12%, 18%, and 28%. 
There are a few GST rates that are less commonly used, such as 3% and 0.25%.

Furthermore, the taxable composition persons are required to pay General Service Tax at lower or nominal rates such as 1.5%, 5%, or 6% on their turnover. 
TDS and TCS are also concepts under GST, with rates of 2% and 1%, respectively.

These are the total IGST rates for interstate supplies or the sum of CGST and SGST for intrastate supplies.
To calculate the GST amounts on a tax invoice, multiply the GST rates by the assessable value of the supply.

Furthermore, in addition to the above GST rates, the GST law imposes a cess on the sale of certain items such as cigarettes, tobacco,
aerated water, gasoline, and motor vehicles, with rates ranging from 1% to 204%.
        
        """

        tk.Label(frame, text=literacy_text, font=("Arial", 12), justify="left").pack(pady=10)
        tk.Button(frame, text="Back to Dashboard", command=lambda: self.show_frame("transaction_dashboard")).pack(pady=20)

        return frame

    def show_pie_charts(self):
        conn = sqlite3.connect("transactions.db")
        cursor = conn.cursor()
        cursor.execute("SELECT class, amount FROM transactions WHERE user_id=?", (self.user_id,))
        transactions = cursor.fetchall()
        conn.close()

        if not transactions:
            messagebox.showerror("Error", "No transactions available to display pie charts.")
            return

        credit_data = {}
        debit_data = {}

        for transaction in transactions:
            transaction_class, amount = transaction
            if amount >= 0:
                credit_data[transaction_class] = credit_data.get(transaction_class, 0) + amount
            else:
                debit_data[transaction_class] = debit_data.get(transaction_class, 0) + abs(amount)

        credit_labels = list(credit_data.keys())
        credit_values = list(credit_data.values())
        debit_labels = list(debit_data.keys())
        debit_values = list(debit_data.values())

        pie_window = tk.Toplevel(self.root)
        pie_window.title("Pie Charts of Credit and Debit Activities")
        pie_window.geometry("800x400")

        fig, axs = plt.subplots(1, 2, figsize=(8, 4))

        axs[0].pie(credit_values, labels=credit_labels, autopct="%1.1f%%", startangle=140)
        axs[0].set_title("Credit Distribution")

        axs[1].pie(debit_values, labels=debit_labels, autopct="%1.1f%%", startangle=140)
        axs[1].set_title("Debit Distribution")

        canvas = FigureCanvasTkAgg(fig, master=pie_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        plt.tight_layout()

    def login(self):
        username = self.login_username_entry.get()
        password = self.login_password_entry.get()

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            self.user_id = username
            self.show_frame("transaction_dashboard")
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def register(self):
        username = self.register_username_entry.get()
        password = self.register_password_entry.get()

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            messagebox.showinfo("Success", "Registration successful. Please log in.")
            self.show_frame("login")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists.")
        finally:
            conn.close()

    def add_transaction(self):
        transaction_class = self.transaction_class_entry.get()
        amount = float(self.transaction_amount_entry.get())
        transaction_type = self.transaction_type_var.get()

        # Apply GST calculation based on transaction class
        gst = abs(amount) * 0.18
        if transaction_class.lower() == "food":
            gst = abs(amount) * 0.12
        elif transaction_class.lower() == "groceries":
            gst = abs(amount) * 0.05
        elif transaction_class.lower() == "medical":
            gst = abs(amount) * 0.12
        elif transaction_class.lower() == "alcohol" or transaction_class.lower() == "drinks":
            gst = abs(amount) * 0.18
        elif transaction_class.lower() == "electronics":
            gst = abs(amount) * 0.18

        # Income tax calculation based on the income tax slabs
        income_tax = 0
        if amount <= 300000:
            income_tax = 0
        elif amount <= 700000:
            income_tax = (amount - 300000) * 0.05
        elif amount <= 1000000:
            income_tax = (amount - 700000) * 0.10 + (700000 - 300000) * 0.05
        elif amount <= 1200000:
            income_tax = (amount - 1000000) * 0.15 + (300000) * 0.10 + (700000 - 300000) * 0.05
        elif amount <= 1500000:
            income_tax = (amount - 1200000) * 0.20 + (200000) * 0.15 + (300000) * 0.10 + (700000 - 300000) * 0.05
        else:
            income_tax = (amount - 1500000) * 0.30 + (300000) * 0.20 + (200000) * 0.15 + (300000) * 0.10 + (
                        700000 - 300000) * 0.05

        # Calculate the total amount including GST and Income Tax
        total = amount + gst + income_tax
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect("transactions.db")
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS transactions (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id TEXT,
                            class TEXT,
                            amount REAL,
                            gst REAL,
                            income_tax REAL,
                            total REAL,
                            transaction_type TEXT,
                            timestamp TEXT)""")
        cursor.execute("""INSERT INTO transactions (user_id, class, amount, gst, income_tax, total, transaction_type, timestamp)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                       (self.user_id, transaction_class, amount, gst, income_tax, total, transaction_type, timestamp))
        conn.commit()
        conn.close()

        self.transaction_class_entry.delete(0, tk.END)
        self.transaction_amount_entry.delete(0, tk.END)

        messagebox.showinfo("Success", "Transaction added successfully.")

    def update_summary_page(self):
        conn = sqlite3.connect("transactions.db")
        cursor = conn.cursor()
        cursor.execute("""SELECT id, class, amount, gst, income_tax, total, transaction_type, timestamp
                          FROM transactions WHERE user_id=?""", (self.user_id,))
        transactions = cursor.fetchall()
        conn.close()

        for item in self.tree.get_children():
            self.tree.delete(item)

        total_gst = total_income_tax = 0

        for transaction in transactions:
            self.tree.insert("", tk.END, values=transaction)
            total_gst += transaction[3]
            total_income_tax += transaction[4]

        self.total_gst_label.config(text=f"Total GST: ₹{total_gst:.2f}")
        self.total_income_tax_label.config(text=f"Total Income Tax: ₹{total_income_tax:.2f}")

    def delete_transaction(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a transaction to delete.")
            return

        transaction_id = self.tree.item(selected_item)["values"][0]

        conn = sqlite3.connect("transactions.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id=?", (transaction_id,))
        conn.commit()
        conn.close()

        self.tree.delete(selected_item)
        messagebox.showinfo("Success", "Transaction deleted successfully.")


if __name__ == "__main__":
    root = tk.Tk()
    app = FinancialApp(root)
    root.mainloop()
