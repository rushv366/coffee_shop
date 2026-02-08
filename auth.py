import sqlite3
from database import create_connection
from models import User

class AuthSystem:
    def __init__(self):
        self.conn = create_connection()
        self.current_user = None
    
    def register_user(self, first_name, last_name, email, contact_number, password, is_admin=False):
        """Register a new user"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
            INSERT INTO users (first_name, last_name, email, contact_number, password, is_admin)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (first_name, last_name, email, contact_number, password, 1 if is_admin else 0))
            self.conn.commit()
            print(f"✓ User {email} registered successfully!")
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            print("✗ Email already exists!")
            return None
        except Exception as e:
            print(f"✗ Registration error: {e}")
            return None
    
    def login(self, email, password):
        """Login user"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
            SELECT * FROM users WHERE email = ? AND password = ?
            ''', (email, password))
            
            row = cursor.fetchone()
            if row:
                user = User.from_db_row(row)
                user_type = "Admin" if user.is_admin else "Customer"
                print(f"✓ Login successful! Welcome, {user.first_name} ({user_type})")
                return user
            else:
                print("✗ Invalid email or password!")
                return None
        except Exception as e:
            print(f"✗ Login error: {e}")
            return None
    
    def get_user_by_email(self, email):
        """Get user by email"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            row = cursor.fetchone()
            if row:
                return User.from_db_row(row)
            return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def logout(self):
        """Logout current user"""
        if self.current_user:
            print(f"✓ Goodbye, {self.current_user.first_name}!")
            self.current_user = None
        else:
            print("No user is logged in!")
    
    def get_current_user(self):
        """Get currently logged in user"""
        return self.current_user
    
    def is_admin(self):
        """Check if current user is admin"""
        return self.current_user and self.current_user.is_admin
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()