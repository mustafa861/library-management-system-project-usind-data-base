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
    
    # Add some books
    lib.add_book("Python Programming", "John Smith", "ISBN123", 5)
    lib.add_book("Data Structures", "Jane Doe", "ISBN456", 3)
    
    # Add a member
    lib.add_member("Alice Brown", "alice@email.com", "1234567890")
    
    # Search for books
    results = lib.search_books("Python")
    for book in results:
        print(book)
    
    # Close the connection
    lib.close()
