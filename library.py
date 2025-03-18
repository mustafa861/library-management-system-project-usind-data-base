import sqlite3
from datetime import datetime, timedelta

class LibraryManagement:
    def __init__(self):
        self.conn = sqlite3.connect('library.db')
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Create Books table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                book_id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                isbn TEXT UNIQUE,
                quantity INTEGER,
                available INTEGER
            )
        ''')

        # Create Members table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS members (
                member_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                phone TEXT
            )
        ''')

        # Create Transactions table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INTEGER PRIMARY KEY,
                book_id INTEGER,
                member_id INTEGER,
                issue_date DATE,
                return_date DATE,
                returned BOOLEAN,
                FOREIGN KEY (book_id) REFERENCES books (book_id),
                FOREIGN KEY (member_id) REFERENCES members (member_id)
            )
        ''')
        self.conn.commit()

    def add_book(self, title, author, isbn, quantity):
        try:
            self.cursor.execute('''
                INSERT INTO books (title, author, isbn, quantity, available)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, author, isbn, quantity, quantity))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def add_member(self, name, email, phone):
        try:
            self.cursor.execute('''
                INSERT INTO members (name, email, phone)
                VALUES (?, ?, ?)
            ''', (name, email, phone))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def issue_book(self, book_id, member_id):
        # Check if book is available
        self.cursor.execute('SELECT available FROM books WHERE book_id = ?', (book_id,))
        available = self.cursor.fetchone()

        if available and available[0] > 0:
            issue_date = datetime.now().date()
            return_date = issue_date + timedelta(days=14)  # 14 days lending period
            
            # Create transaction
            self.cursor.execute('''
                INSERT INTO transactions (book_id, member_id, issue_date, return_date, returned)
                VALUES (?, ?, ?, ?, ?)
            ''', (book_id, member_id, issue_date, return_date, False))
            
            # Update available quantity
            self.cursor.execute('''
                UPDATE books SET available = available - 1
                WHERE book_id = ?
            ''', (book_id,))
            
            self.conn.commit()
            return True
        return False

    def return_book(self, book_id, member_id):
        try:
            # Update transaction
            self.cursor.execute('''
                UPDATE transactions 
                SET returned = True 
                WHERE book_id = ? AND member_id = ? AND returned = False
            ''', (book_id, member_id))
            
            # Update available quantity
            self.cursor.execute('''
                UPDATE books SET available = available + 1
                WHERE book_id = ?
            ''', (book_id,))
            
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def search_books(self, keyword):
        self.cursor.execute('''
            SELECT * FROM books 
            WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ?
        ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
        return self.cursor.fetchall()

    def get_member_books(self, member_id):
        self.cursor.execute('''
            SELECT books.title, transactions.issue_date, transactions.return_date 
            FROM books 
            JOIN transactions ON books.book_id = transactions.book_id 
            WHERE transactions.member_id = ? AND transactions.returned = False
        ''', (member_id,))
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()

# Example usage
if __name__ == "__main__":
    lib = LibraryManagement()
    
    while True:
        print("\n=== Library Management System ===")
        print("1. Add Book")
        print("2. Add Member")
        print("3. Search Books")
        print("4. Issue Book")
        print("5. Return Book")
        print("6. View Member's Books")
        print("7. Exit")
        
        choice = input("\nEnter your choice (1-7): ")
        
        if choice == '1':
            title = input("Enter book title: ")
            author = input("Enter author name: ")
            isbn = input("Enter ISBN: ")
            quantity = int(input("Enter quantity: "))
            if lib.add_book(title, author, isbn, quantity):
                print("Book added successfully!")
            else:
                print("Failed to add book. ISBN might be duplicate.")
                
        elif choice == '2':
            name = input("Enter member name: ")
            email = input("Enter email: ")
            phone = input("Enter phone: ")
            if lib.add_member(name, email, phone):
                print("Member added successfully!")
            else:
                print("Failed to add member. Email might be duplicate.")
                
        elif choice == '3':
            keyword = input("Enter search keyword: ")
            results = lib.search_books(keyword)
            if results:
                for book in results:
                    print(f"ID: {book[0]}, Title: {book[1]}, Author: {book[2]}, ISBN: {book[3]}, Quantity: {book[4]}, Available: {book[5]}")
            else:
                print("No books found.")
                
        elif choice == '4':
            book_id = int(input("Enter book ID: "))
            member_id = int(input("Enter member ID: "))
            if lib.issue_book(book_id, member_id):
                print("Book issued successfully!")
            else:
                print("Failed to issue book. Check availability and IDs.")
                
        elif choice == '5':
            book_id = int(input("Enter book ID: "))
            member_id = int(input("Enter member ID: "))
            if lib.return_book(book_id, member_id):
                print("Book returned successfully!")
            else:
                print("Failed to return book. Check IDs and if book was issued.")
                
        elif choice == '6':
            member_id = int(input("Enter member ID: "))
            books = lib.get_member_books(member_id)
            if books:
                for book in books:
                    print(f"Title: {book[0]}, Issue Date: {book[1]}, Return Date: {book[2]}")
            else:
                print("No books currently borrowed by this member.")
                
        elif choice == '7':
            print("Thank you for using the Library Management System!")
            lib.close()
            break
            
        else:
            print("Invalid choice! Please try again.")
 