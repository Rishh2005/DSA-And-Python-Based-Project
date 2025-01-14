import tkinter as tk
from tkinter import messagebox
import sqlite3

# Create a database to store transactions
conn = sqlite3.connect("money_manager.db")
c = conn.cursor()

# Create table for transactions if it doesn't exist
c.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    amount REAL NOT NULL,
    description TEXT
)
""")
conn.commit()

# Function to update balance and show transaction history
def update_balance():
    c.execute("SELECT SUM(amount) FROM transactions WHERE type = 'Income'")
    income = c.fetchone()[0] or 0
    c.execute("SELECT SUM(amount) FROM transactions WHERE type = 'Expense'")
    expense = c.fetchone()[0] or 0
    balance = income - expense
    balance_label.config(text=f"Balance: ${balance:.2f}")

    # Update transaction history
    display_transactions()

# Function to add a new transaction
def add_transaction():
    transaction_type = transaction_type_var.get()
    amount = amount_entry.get()
    description = description_entry.get()

    if not amount or not transaction_type:
        messagebox.showwarning("Input Error", "Please fill in all fields")
        return

    try:
        amount = float(amount)
    except ValueError:
        messagebox.showwarning("Input Error", "Amount should be a number")
        return

    # Insert the transaction into the database
    c.execute("INSERT INTO transactions (type, amount, description) VALUES (?, ?, ?)",
              (transaction_type, amount, description))
    conn.commit()

    # Clear the entry fields and update the balance
    amount_entry.delete(0, tk.END)
    description_entry.delete(0, tk.END)
    update_balance()

# Function to display the transaction history
def display_transactions():
    for widget in transaction_frame.winfo_children():
        widget.destroy()

    c.execute("SELECT * FROM transactions")
    transactions = c.fetchall()

    for i, transaction in enumerate(transactions):
        transaction_text = f"{transaction[1]}: ${transaction[2]:.2f} - {transaction[3]}"
        label = tk.Label(transaction_frame, text=transaction_text, bg="black", fg="white", font=("Arial", 10), anchor="w")
        label.grid(row=i, column=0, padx=5, pady=5, sticky="w")

# Set up the root window
root = tk.Tk()
root.title("Money Manager")
root.geometry("600x700")
root.configure(bg="#2e2e2e")

# Set up the labels and entries for the inputs
heading_label = tk.Label(root, text="Money Keeper", font=("Arial", 24, "bold"), fg="#ffd700", bg="#2e2e2e")
heading_label.pack(pady=20)

transaction_type_var = tk.StringVar()
income_radio = tk.Radiobutton(root, text="Income", variable=transaction_type_var, value="Income", fg="#00ff00", bg="#2e2e2e", font=("Arial", 14), selectcolor="#3e3e3e")
income_radio.pack()

expense_radio = tk.Radiobutton(root, text="Expense", variable=transaction_type_var, value="Expense", fg="#ff4500", bg="#2e2e2e", font=("Arial", 14), selectcolor="#3e3e3e")
expense_radio.pack()

amount_label = tk.Label(root, text="Amount:", fg="#ffd700", bg="#2e2e2e", font=("Arial", 14))
amount_label.pack(pady=5)
amount_entry = tk.Entry(root, font=("Arial", 14), fg="#ffd700", bg="#1e1e1e", insertbackground="white")
amount_entry.pack(pady=5)

description_label = tk.Label(root, text="Description:", fg="#ffd700", bg="#2e2e2e", font=("Arial", 14))
description_label.pack(pady=5)
description_entry = tk.Entry(root, font=("Arial", 14), fg="#ffd700", bg="#1e1e1e", insertbackground="white")
description_entry.pack(pady=5)

add_button = tk.Button(root, text="Add Transaction", font=("Arial", 16, "bold"), fg="#2e2e2e", bg="#ffd700", command=add_transaction, relief="raised", bd=3)
add_button.pack(pady=20)

# Display balance
balance_label = tk.Label(root, text="Balance: $0.00", fg="#32cd32", bg="#2e2e2e", font=("Arial", 16, "bold"))
balance_label.pack(pady=10)

# Transaction history frame
transaction_frame = tk.Frame(root, bg="#1e1e1e", relief="sunken", bd=3)
transaction_frame.pack(pady=10, fill=tk.BOTH, expand=True)

# Initial update of balance and transaction history
update_balance()

# Start the Tkinter event loop
root.mainloop()

# Close the database connection when the app is closed
conn.close()
