import logging

# Set up logging
logging.basicConfig(filename='atm_simulation.log', level=logging.INFO, format='%(asctime)s - %(message)s')

class Account:
    def __init__(self, initial_balance=0, pin="1234"):
        self.balance = initial_balance
        self.pin = pin
        self.transaction_history = []

    def check_pin(self, entered_pin):
        return entered_pin == self.pin

    def account_balance(self):
        return self.balance

    def cash_withdrawal(self, amount):
        if amount > self.balance:
            return "Insufficient balance!"
        elif amount <= 0:
            return "Enter a valid amount to withdraw!"
        else:
            self.balance -= amount
            self.transaction_history.append(f"Withdrawal: -${amount}")
            logging.info(f"Withdrawal of ${amount} made. New balance: ${self.balance}")
            return f"Withdrawal successful! New balance: ${self.balance}"

    def cash_deposit(self, amount):
        if amount <= 0:
            return "Enter a valid amount to deposit!"
        else:
            self.balance += amount
            self.transaction_history.append(f"Deposit: +${amount}")
            logging.info(f"Deposit of ${amount} made. New balance: ${self.balance}")
            return f"Deposit successful! New balance: ${self.balance}"

    def change_pin(self, old_pin, new_pin):
        if self.check_pin(old_pin):
            self.pin = new_pin
            self.transaction_history.append("PIN changed successfully.")
            logging.info("PIN changed successfully.")
            return "PIN changed successfully!"
        else:
            return "Incorrect old PIN!"

    def view_transaction_history(self):
        if not self.transaction_history:
            return "No transactions found."
        return "\n".join(self.transaction_history)

class ATM:
    def __init__(self):
        self.accounts = {}
        self.current_account = None

    def create_account(self, pin, initial_balance=0):
        if pin in self.accounts:
            return "Account with this PIN already exists!"
        self.accounts[pin] = Account(initial_balance, pin)
        return "Account created successfully!"

    def login(self, pin):
        if pin in self.accounts:
            self.current_account = self.accounts[pin]
            return True
        return False

    def logout(self):
        self.current_account = None

# Main program to simulate ATM functionality
def atm_simulation():
    atm = ATM()
    atm.create_account("1234", 10000)  # Create a default account for testing

    print("\nWelcome to the ATM Machine Simulation!")

    while True:
        print("\nSelect an option:")
        print("1. Login")
        print("2. Create Account")
        print("3. Exit")

        choice = input("Enter your choice (1-3): ")

        if choice == "1":
            entered_pin = input("Enter your 4-digit PIN: ")
            if atm.login(entered_pin):
                print("\nLogin successful!")
                while True:
                    print("\nSelect an option:")
                    print("1. Check Account Balance")
                    print("2. Withdraw Cash")
                    print("3. Deposit Cash")
                    print("4. Change PIN")
                    print("5. View Transaction History")
                    print("6. Logout")

                    choice = input("Enter your choice (1-6): ")

                    if choice == "1":
                        print(f"\nYour current balance is: ${atm.current_account.account_balance()}")

                    elif choice == "2":
                        try:
                            amount = float(input("Enter the amount to withdraw: $"))
                            print(atm.current_account.cash_withdrawal(amount))
                        except ValueError:
                            print("Invalid input! Please enter a valid number.")

                    elif choice == "3":
                        try:
                            amount = float(input("Enter the amount to deposit: $"))
                            print(atm.current_account.cash_deposit(amount))
                        except ValueError:
                            print("Invalid input! Please enter a valid number.")

                    elif choice == "4":
                        old_pin = input("Enter your current PIN: ")
                        new_pin = input("Enter your new PIN: ")
                        print(atm.current_account.change_pin(old_pin, new_pin))

                    elif choice == "5":
                        print("\nTransaction History:")
                        print(atm.current_account.view_transaction_history())

                    elif choice == "6":
                        atm.logout()
                        print("\nLogged out successfully.")
                        break

                    else:
                        print("Invalid choice. Please try again.")
            else:
                print("Incorrect PIN. Try again.")

        elif choice == "2":
            new_pin = input("Enter a new 4-digit PIN: ")
            try:
                initial_balance = float(input("Enter initial balance: $"))
                print(atm.create_account(new_pin, initial_balance))
            except ValueError:
                print("Invalid input! Please enter a valid number.")

        elif choice == "3":
            print("\nThank you for using the ATM Machine Simulation. Have a great day!")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    atm_simulation()
