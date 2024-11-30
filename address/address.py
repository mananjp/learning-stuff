from tkinter import *
import sqlite3
from PIL import Image, ImageTk
from tkinter import ttk

root = Tk()
root.title("Address Book")
root.iconphoto(True, ImageTk.PhotoImage(Image.open('D:/git/learning-stuff/image_view/logo.png').resize((32, 32), Image.Resampling.LANCZOS)))

# Connect to the SQLite database
conn = sqlite3.connect('addressbook.db')
c = conn.cursor()

# Create the table if it does not exist
c.execute("""
CREATE TABLE IF NOT EXISTS addresses (
    fname text,
    lname text,
    address text,
    city text,
    state text,
    zip integer
)
""")
conn.commit()


# Function to delete a selected record
def delete():
    selected_item = tree.selection()  # Get the selected item in the Treeview
    if selected_item:  # Check if any item is selected
        # Get the values of the selected row
        selected_row = tree.item(selected_item)["values"]
        # The selected_row contains (fname, lname, address, city, state, zip),
        # we need to delete it from the database based on the primary key (oid)

        # Retrieve the database record's ID (assuming `oid` is the primary key)
        c.execute("SELECT rowid FROM addresses WHERE fname = ? AND lname = ? AND address = ?",
                  (selected_row[0], selected_row[1], selected_row[2]))
        record = c.fetchone()

        if record:
            rowid = record[0]  # Get the rowid (OID) of the selected record
            c.execute("DELETE FROM addresses WHERE rowid = ?", (rowid,))
            conn.commit()

        # Refresh the records in the Treeview
        refresh_records()


# Function to submit a new record
def submit():
    # Insert data into the database
    c.execute("INSERT INTO addresses (fname, lname, address, city, state, zip) VALUES (?, ?, ?, ?, ?, ?)",
              (f_name.get(), l_name.get(), address.get(), city.get(), state.get(), zip.get()))
    conn.commit()

    # Clear the input fields
    f_name.delete(0, END)
    l_name.delete(0, END)
    address.delete(0, END)
    city.delete(0, END)
    state.delete(0, END)
    zip.delete(0, END)

    # Refresh the records in the Treeview
    refresh_records()

# Function to refresh the records displayed in the Treeview
def refresh_records():
    # Clear the existing data in the Treeview
    for row in tree.get_children():
        tree.delete(row)

    # Fetch all records from the database
    c.execute("SELECT * FROM addresses")
    rows = c.fetchall()

    # Insert fetched records into the Treeview
    for row in rows:
        tree.insert("", "end", values=row)

def clear():
    f_name.delete(0, END)
    l_name.delete(0, END)
    address.delete(0, END)
    city.delete(0, END)
    state.delete(0, END)
    zip.delete(0, END)

# Define the input fields
f_name = Entry(root, width=40)
f_name.grid(row=0, column=1, padx=10, pady=10)

l_name = Entry(root, width=40)
l_name.grid(row=1, column=1, padx=10, pady=10)

address = Entry(root, width=40)
address.grid(row=2, column=1, padx=10, pady=10)

city = Entry(root, width=40)
city.grid(row=3, column=1, padx=10, pady=10)

state = Entry(root, width=40)
state.grid(row=4, column=1, padx=10, pady=10)

zip = Entry(root, width=40)
zip.grid(row=5, column=1, padx=10, pady=10)

# Labels for the input fields
f_name_label = Label(root, text="Enter First Name")
f_name_label.grid(row=0, column=0, padx=10, pady=10)

l_name_label = Label(root, text="Enter Last Name")
l_name_label.grid(row=1, column=0, padx=10, pady=10)

address_label = Label(root, text="Enter Address")
address_label.grid(row=2, column=0, padx=10, pady=10)

city_label = Label(root, text="Enter City")
city_label.grid(row=3, column=0, padx=10, pady=10)

state_label = Label(root, text="Enter State")
state_label.grid(row=4, column=0, padx=10, pady=10)

zip_label = Label(root, text="Enter Zip")
zip_label.grid(row=5, column=0, padx=10, pady=10)

# Submit button
submit_btn = Button(root, text="Submit", command=submit)
submit_btn.grid(row=6, column=0, padx=10, pady=10, ipady=10, ipadx=10)

quit = Button(root, text="Quit", command=root.quit)
quit.grid(row=6, column=1, padx=10, pady=10, ipadx=10)

clear = Button(root, text="Clear", command=clear)
clear.grid(row=7, column=1, padx=10, pady=10, ipadx=10)

Delete = Button(root, text="delete", command=delete)
Delete.grid(row=7, column=0, padx=10, pady=10, ipadx=10)

# Treeview widget to display records
tree = ttk.Treeview(root, columns=("fname", "lname", "address", "city", "state", "zip"), show="headings")
tree.grid(row=8, column=0, columnspan=2, padx=10, pady=10)

# Define the columns
tree.heading("fname", text="First Name")
tree.heading("lname", text="Last Name")
tree.heading("address", text="Address")
tree.heading("city", text="City")
tree.heading("state", text="State")
tree.heading("zip", text="Zip")

# Refresh the records when the application starts
refresh_records()

# Close the connection when the window is closed
def on_close():
    conn.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

# Start the Tkinter event loop
root.mainloop()
