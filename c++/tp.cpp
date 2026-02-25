#include <iostream>
#include <string>
#include <vector>
#include <unordered_set>
using namespace std;

/*class BestBook {
    virtual void bb()=0;
};*/

class Library {
public:
    int bno;
    string book;
    string Auth;
    int issue[100];

    Library(string name, string auth, int no) {
        bno = no;
        book = name;
        Auth = auth;
    }

    void printbook() const {
        cout << "Name of book is: " << book << endl;
        cout << "Author of book is: " << Auth << endl;
        cout << "Book number is: " << bno << endl;
        cout << endl;
    }
    /*void bb()
    {
        if(book=="manan")
        {
            cout << book << " is the best book" << endl;
        }
        else
        {
            cout << book << " not good book" << endl;
        }

    }*/
};

int main() {
    int choice, num;
    string name, au;
    vector<Library> books;
    unordered_set<int> issuedBookNumbers;


    do {
        cout << "Do you want to issue a book? 1-> Yes, 0-> No: ";
        cin >> choice;

        if (choice == 1) {

            cout << "Give name of book: ";
            cin >> name;

            cout << "Give book number: ";
            cin >> num;


            if (issuedBookNumbers.find(num) != issuedBookNumbers.end()) {
                cout << "This book has already been issued. Cannot issue again." << endl;
            }
            else {
                cout << "Give author name: ";
                cin >> au;

                Library book1(name, au, num);

                books.push_back(book1);

                issuedBookNumbers.insert(num);


            }
        }
        else {
            cout << "No book issued." << endl;
        }

        if (choice == 1) {
            cout << "Do you want to issue another book? 1-> Yes, 0-> No: ";
            cin >> choice;
        }

    } while (choice == 1);


    cout << "Books issued: " << endl;
    for (const auto& book : books) {
        book.printbook();

    }
    return 0;
}
