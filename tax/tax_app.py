import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


class FinancialApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Financial Management System")
        self.root.geometry("800x600")

        self.frames = {}
        self.user_id = None

        self.setup_database()

        self.frames["login"] = self.create_login_page()
        self.frames["register"] = self.create_register_page()
        self.frames["transaction_dashboard"] = self.create_transaction_dashboard()
        self.frames["financial_summary"] = self.create_summary_page()
        self.frames["financial_literacy"] = self.create_financial_literacy_page()

        self.show_frame("login")

    def setup_database(self):
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT
            )
        """)
        conn.commit()
        conn.close()

        conn = sqlite3.connect("transactions.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                class TEXT,
                amount REAL,
                gst REAL,
                income_tax REAL,
                total REAL,
                transaction_type TEXT,
                timestamp TEXT
            )
        """)
        conn.commit()
        conn.close()

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

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.W, width=120)

        self.tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)

        self.total_gst_label = tk.Label(frame, text="Total GST: ₹0.00", font=("Arial", 14))
        self.total_gst_label.pack(pady=5)

        self.total_income_tax_label = tk.Label(frame, text="Total Income Tax: ₹0.00", font=("Arial", 14))
        self.total_income_tax_label.pack(pady=5)

        tk.Button(frame, text="Show Pie Charts of Credit and Debit", command=self.show_pie_charts).pack(pady=10)
        tk.Button(frame, text="Delete Selected Transaction", command=self.delete_transaction).pack(pady=10)
        tk.Button(frame, text="Back to Transaction Dashboard",
                  command=lambda: self.show_frame("transaction_dashboard")).pack(pady=10)

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
        """
        tk.Label(frame, text=literacy_text, font=("Arial", 12), justify="left").pack(pady=10)
        tk.Button(frame, text="Back to Dashboard", command=lambda: self.show_frame("transaction_dashboard")).pack(
            pady=20)

        return frame

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

        if not username or not password:
            messagebox.showerror("Error", "Username and password cannot be empty.")
            return

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
        amount = self.transaction_amount_entry.get()
        transaction_type = self.transaction_type_var.get()

        if not transaction_class or not amount:
            messagebox.showerror("Error", "Transaction class and amount cannot be empty.")
            return

        try:
            amount = float(amount)
            gst = round(amount * 0.18, 2)
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

            income_tax = self.calculate_income_tax(amount)
            total = amount + gst - income_tax if transaction_type == "Credit" else amount + gst + income_tax

            # Convert datetime to string format
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            conn = sqlite3.connect("transactions.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transactions (user_id, class, amount, gst, income_tax, total, transaction_type, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (self.user_id, transaction_class, amount, gst, income_tax, total, transaction_type, timestamp))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Transaction added successfully.")
        except ValueError:
            messagebox.showerror("Error", "Amount must be a valid number.")

    def calculate_income_tax(self, amount):
        if amount <= 300000:
            return 0
        elif amount <= 700000:
            return (amount - 300000) * 0.05
        elif amount <= 1000000:
            return (700000 - 300000) * 0.05 + (amount - 700000) * 0.1
        elif amount <= 1200000:
            return (700000 - 300000) * 0.05 + (1000000 - 700000) * 0.1 + (amount - 1000000) * 0.15
        elif amount <= 1500000:
            return (700000 - 300000) * 0.05 + (1000000 - 700000) * 0.1 + (1200000 - 1000000) * 0.15 + (
                    amount - 1200000) * 0.2
        else:
            return (700000 - 300000) * 0.05 + (1000000 - 700000) * 0.1 + (1200000 - 1000000) * 0.15 + (
                    1500000 - 1200000) * 0.2 + (amount - 1500000) * 0.3

    def update_summary_page(self):
        conn = sqlite3.connect("transactions.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM transactions WHERE user_id=?", (self.user_id,))
        transactions = cursor.fetchall()
        conn.close()

        # Clear the treeview before populating
        for row in self.tree.get_children():
            self.tree.delete(row)

        total_gst = 0
        total_income_tax = 0

        for transaction in transactions:
            try:
                # Try parsing with microseconds
                formatted_timestamp = datetime.strptime(transaction[8], "%Y-%m-%d %H:%M:%S.%f").strftime(
                    "%d-%m-%Y %H:%M")
            except ValueError:
                # If it fails, parse without microseconds
                formatted_timestamp = datetime.strptime(transaction[8], "%Y-%m-%d %H:%M:%S").strftime("%d-%m-%Y %H:%M")

            self.tree.insert("", "end", values=(
                transaction[0],  # ID
                transaction[2],  # Class
                f"₹{transaction[3]:.2f}",  # Amount
                f"₹{transaction[4]:.2f}",  # GST
                f"₹{transaction[5]:.2f}",  # Income Tax
                f"₹{transaction[6]:.2f}",  # Total
                transaction[7],  # Transaction Type
                formatted_timestamp,  # Formatted Timestamp
            ))
            total_gst += transaction[4]
            total_income_tax += transaction[5]

        # Update total labels
        self.total_gst_label.config(text=f"Total GST: ₹{total_gst:.2f}")
        self.total_income_tax_label.config(text=f"Total Income Tax: ₹{total_income_tax:.2f}")

    def delete_transaction(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "No transaction selected.")
            return

        # Get the ID of the selected transaction
        transaction_id = self.tree.item(selected_item, "values")[0]

        conn = sqlite3.connect("transactions.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id=?", (transaction_id,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Transaction deleted successfully.")
        self.update_summary_page()

    def show_pie_charts(self):
        conn = sqlite3.connect("transactions.db")
        cursor = conn.cursor()
        cursor.execute("SELECT class, amount, transaction_type FROM transactions WHERE user_id=?", (self.user_id,))
        transactions = cursor.fetchall()
        conn.close()

        if not transactions:
            messagebox.showerror("Error", "No transactions available to display pie charts.")
            return

        credit_data = {}
        debit_data = {}

        for transaction in transactions:
            transaction_class, amount, transaction_type = transaction
            if transaction_type == "Credit":
                credit_data[transaction_class] = credit_data.get(transaction_class, 0) + amount
            else:
                debit_data[transaction_class] = debit_data.get(transaction_class, 0) + abs(amount)

        # Prepare labels and values for pie charts
        credit_labels = list(credit_data.keys())
        credit_values = list(credit_data.values())
        debit_labels = list(debit_data.keys())
        debit_values = list(debit_data.values())

        pie_window = tk.Toplevel(self.root)
        pie_window.title("Pie Charts of Credit and Debit Activities")
        pie_window.geometry("800x400")

        fig, axs = plt.subplots(1, 2, figsize=(8, 4))

        if credit_values:
            axs[0].pie(credit_values, labels=credit_labels, autopct="%1.1f%%", startangle=140)
            axs[0].set_title("Credit Distribution")
        else:
            axs[0].text(0.5, 0.5, 'No Credit Transactions', ha='center', va='center', fontsize=12)

        if debit_values:
            axs[1].pie(debit_values, labels=debit_labels, autopct="%1.1f%%", startangle=140)
            axs[1].set_title("Debit Distribution")
        else:
            axs[1].text(0.5, 0.5, 'No Debit Transactions', ha='center', va='center', fontsize=12)

        canvas = FigureCanvasTkAgg(fig, master=pie_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        plt.tight_layout()


if __name__ == "__main__":
    root = tk.Tk()
    app = FinancialApp(root)
    root.mainloop()
