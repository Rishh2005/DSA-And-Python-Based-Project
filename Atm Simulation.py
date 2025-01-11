# ATM Machine Simulation
# Author: Rishabh Jain(Python Developer Intern)

class ATM:
    def __init__(self, initial_balance=0, pin="1234"):
        # Initialize ATM with default balance and PIN
        self.balance = initial_balance
        self.pin = pin
        self.transaction_history = []

    def check_pin(self, entered_pin):
        # Verify the entered PIN
        return entered_pin == self.pin

    def account_balance(self):
        # Get the current account balance
        return self.balance

    def cash_withdrawal(self, amount):
        # Process cash withdrawal
        if amount > self.balance:
            return "Insufficient balance!"
        elif amount <= 0:
            return "Enter a valid amount to withdraw!"
        else:
            self.balance -= amount
            self.transaction_history.append(f"Withdrawal: -${amount}")
            return f"Withdrawal successful! New balance: ${self.balance}"

    def cash_deposit(self, amount):
        # Process cash deposit
        if amount <= 0:
            return "Enter a valid amount to deposit!"
        else:
            self.balance += amount
            self.transaction_history.append(f"Deposit: +${amount}")
            return f"Deposit successful! New balance: ${self.balance}"

    def change_pin(self, old_pin, new_pin):
        # Change the PIN after verifying the old PIN
        if self.check_pin(old_pin):
            self.pin = new_pin
            self.transaction_history.append("PIN changed successfully.")
            return "PIN changed successfully!"
        else:
            return "Incorrect old PIN!"

    def view_transaction_history(self):
        # Display transaction history
        if not self.transaction_history:
            return "No transactions found."
        return "\n".join(self.transaction_history)

# Main program to simulate ATM functionality
def atm_simulation():
    atm = ATM(initial_balance=10000)  # Initialize ATM with a $5000 balance

    print("\nWelcome to the ATM Machine Simulation!")

    for _ in range(3):  # Allow 3 attempts to enter the PIN
        entered_pin = input("Enter your 4-digit PIN: ")
        if atm.check_pin(entered_pin):
            print("\nLogin successful!")
            break
        else:
            print("Incorrect PIN. Try again.")
    else:
        print("Too many incorrect attempts. Exiting.")
        return

    while True:
        print("\nSelect an option:")
        print("1. Check Account Balance")
        print("2. Withdraw Cash")
        print("3. Deposit Cash")
        print("4. Change PIN")
        print("5. View Transaction History")
        print("6. Exit")

        choice = input("Enter your choice (1-6): ")

        if choice == "1":
            print(f"\nYour current balance is: ${atm.account_balance()}")

        elif choice == "2":
            try:
                amount = float(input("Enter the amount to withdraw: $"))
                print(atm.cash_withdrawal(amount))
            except ValueError:
                print("Invalid input! Please enter a valid number.")

        elif choice == "3":
            try:
                amount = float(input("Enter the amount to deposit: $"))
                print(atm.cash_deposit(amount))
            except ValueError:
                print("Invalid input! Please enter a valid number.")

        elif choice == "4":
            old_pin = input("Enter your current PIN: ")
            new_pin = input("Enter your new PIN: ")
            print(atm.change_pin(old_pin, new_pin))

        elif choice == "5":
            print("\nTransaction History:")
            print(atm.view_transaction_history())

        elif choice == "6":
            print("\nThank you for using the ATM Machine Simulation. Have a great day!")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    atm_simulation()
