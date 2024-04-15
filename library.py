import sqlite3
from datetime import datetime

def connect_database():
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS books (
                 book_id TEXT PRIMARY KEY,
                 title TEXT,
                 author TEXT,
                 issued INTEGER DEFAULT 0
              )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 user_id INTEGER PRIMARY KEY,
                 name TEXT
              )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
                 transaction_id INTEGER PRIMARY KEY,
                 user_id INTEGER,
                 book_id TEXT,
                 date_issued TEXT,
                 date_returned TEXT,
                 FOREIGN KEY (user_id) REFERENCES users(user_id),
                 FOREIGN KEY (book_id) REFERENCES books(book_id)
              )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS payments (
                 user_id INTEGER,
                 fine INTEGER,
                 FOREIGN KEY (user_id) REFERENCES users(user_id)
              )''')
    conn.commit()
    return conn

def add_user(conn, user_id, name):
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (user_id, name) VALUES (?, ?)", (user_id, name))
        conn.commit()
        print("User added successfully.")
    except sqlite3.IntegrityError:
        print("User ID already exists. Please choose a different ID.")

def add_book(conn, book_id, title, author):
    c = conn.cursor()
    try:
        c.execute("INSERT INTO books (book_id, title, author, issued) VALUES (?, ?, ?, 0)", (book_id, title, author))
        conn.commit()
        print("Book added successfully.")
    except sqlite3.IntegrityError:
        print("Book ID already exists. Please choose a different ID.")

def show_user(conn):
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    users = c.fetchall()
    if users:
        print("Users: ")
        for user in users:
            print(f"User ID: {user[0]}, Name: {user[1]}")
    else:
        print("No users found")

def issue_book(conn, user_id, book_id):
    c = conn.cursor()
    book = c.execute("SELECT * FROM books WHERE book_id=? AND issued=0", (book_id,)).fetchone()
    if book:
        c.execute("UPDATE books SET issued=1 WHERE book_id=?", (book_id,))
        current_date = datetime.now().strftime('%Y-%m-%d')
        c.execute("INSERT INTO transactions (user_id, book_id, date_issued) VALUES (?, ?, ?)", (user_id, book_id, current_date))
        conn.commit()
        print(f"Book {book_id} issued to User {user_id} successfully.")
    else:
        print("Book not available.")

def calculate_fine(transaction_date, return_date):
    transaction_date = datetime.strptime(transaction_date, '%Y-%m-%d')
    return_date = datetime.strptime(return_date, '%Y-%m-%d')
    days_overdue = (return_date - transaction_date).days
    if days_overdue > 0:
        return days_overdue * 10
    else:
        return 0

def return_book(conn, user_id, book_id):
    c = conn.cursor()
    c.execute("SELECT * FROM transactions WHERE user_id=? AND book_id=?", (user_id, book_id))
    transaction = c.fetchone()
    if transaction:
        c.execute("UPDATE books SET issued=0 WHERE book_id=?", (book_id,))
        current_date = datetime.now().strftime('%Y-%m-%d')
        c.execute("UPDATE transactions SET date_returned=? WHERE transaction_id=?", (current_date, transaction[0]))
        conn.commit()
        print("Book returned successfully.")
        fine_amount = calculate_fine(transaction[3], current_date)
        if fine_amount > 0:
            c.execute("INSERT INTO payments (user_id, fine) VALUES (?, ?)", (user_id, fine_amount))
            conn.commit()
            print(f"Fine of {fine_amount} added successfully.")
        else:
            print("No fine to add.")
    else:
        print("Book not borrowed by the user.")

def display_user_history(conn, user_id):
    c = conn.cursor()
    c.execute("SELECT transactions.book_id, books.title, transactions.date_issued, transactions.date_returned, payments.fine FROM transactions LEFT JOIN books ON transactions.book_id = books.book_id LEFT JOIN payments ON transactions.user_id = payments.user_id WHERE transactions.user_id=?", (user_id,))
    history = c.fetchall()
    if history:
        print(f"User {user_id} borrowing history: ")
        for item in history:
            print(f"Book ID: {item[0]}, Title: {item[1]}, Date Issued: {item[2]}, Date Returned: {item[3]}, Fine Paid: {'Rs.' + str(item[4]) if item[4] else 'No fine payment, returned ontime'}")
    else:
        print("No borrowing history found for the user.")

def main():
    conn = connect_database()
    while True:
        print("1. Issue Book")
        print("2. Return Book")
        print("3. Add User")
        print("4. Add Book")
        print("5. Show Users")
        print("6. User Borrowing History")
        print("7. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            user_id = input("Enter User ID: ")
            book_id = input("Enter book ID: ")
            issue_book(conn, user_id, book_id)
        elif choice == '2':
            user_id = input("Enter User ID: ")
            book_id = input("Enter book ID: ")
            return_book(conn, user_id, book_id)
        elif choice == '3':
            user_id = input("Enter User ID: ")
            name = input("Enter User Name: ")
            add_user(conn, user_id, name)
        elif choice == '4':
            book_id = input("Enter Book ID: ")
            title = input("Enter Title: ")
            author = input("Enter Author: ")
            add_book(conn, book_id, title, author)
        elif choice == '5':
            show_user(conn)
        elif choice == '6':
            user_id = input("Enter User ID: ")
            display_user_history(conn, user_id)
        elif choice == '7':
            print("Exiting")
            conn.close()
            break
        else:
            print("Invalid choice, please enter a valid number")

if __name__ == "__main__":
    main()
