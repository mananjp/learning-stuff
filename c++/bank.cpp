#include <iostream>
#include <string>
using namespace std;

class BankAccount {
private:
    static int accountCount;  // Static member to count number of accounts
    int accountNumber;
    string accountHolderName;
    double balance;
    string password;  // Password for account

public:
    // Constructor to initialize a bank account
    BankAccount(string name, double initialBalance, string pwd) {
        accountCount++; // Increment the static counter whenever a new account is created
        accountNumber = accountCount;
        accountHolderName = name;
        balance = initialBalance;
        password = pwd;  // Set the password for the account
    }

    // Destructor
    ~BankAccount() {
        cout << "Account with number " << accountNumber << " is being closed.\n";
    }

    // Deposit money into the account
    void deposit(double amount) {
        if (amount > 0) {
            balance += amount;
            cout << "Deposited " << amount << ". New balance: " << balance << endl;
        } else {
            cout << "Amount must be positive to deposit.\n";
        }
    }

    // Withdraw money from the account
    void withdraw(double amount) {
        if (amount <= balance && amount > 0) {
            balance -= amount;
            cout << "Withdrew " << amount << ". New balance: " << balance << endl;
        } else if (amount <= 0) {
            cout << "Amount must be positive to withdraw.\n";
        } else {
            cout << "Insufficient funds to withdraw " << amount << endl;
        }
    }

    // Check password and display account details if valid
    bool checkPassword(const string& pwd) const {
        return password == pwd;
    }

    // Display account details
    void display() const {
        cout << "Account Number: " << accountNumber << endl;
        cout << "Account Holder: " << accountHolderName << endl;
        cout << "Balance: " << balance << endl;
    }

    // Overloading the << operator to display account details
    friend ostream& operator<<(ostream &out, const BankAccount &account) {
        out << "Account Number: " << account.accountNumber << endl;
        out << "Account Holder: " << account.accountHolderName << endl;
        out << "Balance: " << account.balance << endl;
        return out;
    }

    // Static function to get the total number of accounts
    static int getTotalAccounts() {
        return accountCount;
    }

    // Function to get account number
    int getAccountNumber() const {
        return accountNumber;
    }

    // Function to get current balance
    double getBalance() const {
        return balance;
    }
};

// Initialize the static member
int BankAccount::accountCount = 0;

void showAccountMenu() {
    cout << "\nBank Account Menu: \n";
    cout << "1. Deposit money\n";
    cout << "2. Withdraw money\n";
    cout << "3. Check balance\n";
    cout << "4. View account details\n";
    cout << "5. Logout\n";
    cout << "Choose an option (1-5): ";
}

int main() {
    string name, password;
    double initialBalance;
    bool continueCreating = true;
    BankAccount* accounts[100];  // Array to store account pointers
    int accountIndex = 0;

    // Account creation loop
    while (true) {
        cout << "\nWould you like to create a new account? (y/n): ";
        char createChoice;
        cin >> createChoice;
        cin.ignore();  // To ignore the newline left by cin >> createChoice

        if (createChoice == 'n' || createChoice == 'N') {
            break;  // Exit account creation loop if user doesn't want to create new account
        }

        cout << "\nEnter account holder's name: ";
        getline(cin, name);

        cout << "Enter initial balance: ";
        cin >> initialBalance;
        cin.ignore();  // To ignore the newline left by cin >> initialBalance

        cout << "Enter account password: ";
        getline(cin, password);

        // Create a new bank account and store it in the array
        accounts[accountIndex] = new BankAccount(name, initialBalance, password);
        cout << "Account created successfully with account number " << accounts[accountIndex]->getAccountNumber() << endl;
        accountIndex++;

        // Ask the user if they want to create another account
        char choice;
        cout << "Do you want to create another account? (y/n): ";
        cin >> choice;
        cin.ignore();  // To ignore the newline left by cin >> choice

        if (choice != 'y' && choice != 'Y') {
            break;  // Exit the account creation loop
        }
    }

    // Now, let the user access account details and perform bank operations
    while (true) {
        cout << "\nSelect an account to access details (1 to " << BankAccount::getTotalAccounts() << ", 0 to exit): ";
        int accNum;
        cin >> accNum;
        cin.ignore();  // To ignore the newline left by cin >> accNum

        if (accNum == 0) {
            break;
        }

        if (accNum < 1 || accNum > BankAccount::getTotalAccounts()) {
            cout << "Invalid account number.\n";
            continue;
        }

        // Ask for the password to access account details
        string inputPassword;
        cout << "Enter password to access account details: ";
        getline(cin, inputPassword);

        // Validate the password
        if (accounts[accNum - 1]->checkPassword(inputPassword)) {
            // If password is correct, show the bank menu
            while (true) {
                showAccountMenu();
                int choice;
                cin >> choice;
                cin.ignore();  // To ignore the newline left by cin >> choice

                if (choice == 1) {
                    // Deposit money
                    double depositAmount;
                    cout << "Enter amount to deposit: ";
                    cin >> depositAmount;
                    cin.ignore();
                    accounts[accNum - 1]->deposit(depositAmount);
                } else if (choice == 2) {
                    // Withdraw money
                    double withdrawAmount;
                    cout << "Enter amount to withdraw: ";
                    cin >> withdrawAmount;
                    cin.ignore();
                    accounts[accNum - 1]->withdraw(withdrawAmount);
                } else if (choice == 3) {
                    // Check balance
                    cout << "Current balance: " << accounts[accNum - 1]->getBalance() << endl;
                } else if (choice == 4) {
                    // View account details
                    accounts[accNum - 1]->display();
                } else if (choice == 5) {
                    // Logout
                    cout << "Logging out of account " << accNum << endl;
                    break;
                } else {
                    cout << "Invalid option. Please try again.\n";
                }
            }
        } else {
            cout << "Incorrect password. Access denied.\n";
        }
    }

    // Clean up dynamically allocated memory
    for (int i = 0; i < accountIndex; i++) {
        delete accounts[i];
    }

    return 0;
}