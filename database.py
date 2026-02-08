import sqlite3
from sqlite3 import Error
import os

def create_connection():
    """Create a database connection to SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect('coffee_shop.db', check_same_thread=False)
        conn.row_factory = sqlite3.Row
        print(f"SQLite connection established (version {sqlite3.sqlite_version})")
        return conn
    except Error as e:
        print(f"Database connection error: {e}")
    return conn

def create_tables(conn):
    """Create all necessary tables"""
    try:
        cursor = conn.cursor()
        
        # Users table (for both customers and admins)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            contact_number TEXT NOT NULL,
            password TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Coffees table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS coffees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            category TEXT,
            is_available BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Orders table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            total_amount REAL NOT NULL,
            status TEXT DEFAULT 'pending', -- pending, preparing, ready, completed, cancelled
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Order items table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            coffee_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (coffee_id) REFERENCES coffees (id)
        )
        ''')
        
        conn.commit()
        print("✓ Tables created successfully!")
        
    except Error as e:
        print(f"✗ Error creating tables: {e}")

def create_default_admin(conn):
    """Create default admin user if not exists"""
    try:
        cursor = conn.cursor()
        
        # Check if admin exists
        cursor.execute("SELECT * FROM users WHERE email = 'admin@coffee.com'")
        if not cursor.fetchone():
            # Using plain password for testing (admin123)
            admin_password = "admin123"
            cursor.execute('''
            INSERT INTO users (first_name, last_name, email, contact_number, password, is_admin)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', ('Admin', 'User', 'admin@coffee.com', '1234567890', admin_password, 1))
            
            print("✓ Default admin user created!")
            print(f"  Email: admin@coffee.com")
            print(f"  Password: admin123")
        else:
            print("✓ Admin user already exists")
        
        conn.commit()
        
    except Error as e:
        print(f"✗ Error creating admin: {e}")

def add_sample_coffees(conn):
    """Add sample coffee data"""
    try:
        cursor = conn.cursor()
        
        # Check if coffees exist
        cursor.execute("SELECT COUNT(*) FROM coffees")
        count = cursor.fetchone()[0]
        
        if count == 0:
            sample_coffees = [
                ('Espresso', 'Strong and concentrated coffee', 3.50, 'Hot'),
                ('Cappuccino', 'Espresso with steamed milk foam', 4.50, 'Hot'),
                ('Latte', 'Espresso with steamed milk', 4.75, 'Hot'),
                ('Americano', 'Espresso with hot water', 3.75, 'Hot'),
                ('Iced Coffee', 'Chilled coffee with ice', 4.00, 'Cold'),
                ('Mocha', 'Chocolate-flavored latte', 5.00, 'Hot'),
                ('Macchiato', 'Espresso with a dash of milk', 4.25, 'Hot')
            ]
            
            cursor.executemany('''
            INSERT INTO coffees (name, description, price, category)
            VALUES (?, ?, ?, ?)
            ''', sample_coffees)
            
            conn.commit()
            print(f"✓ {len(sample_coffees)} sample coffees added!")
        else:
            print(f"✓ Database already has {count} coffee items")
        
    except Error as e:
        print(f"✗ Error adding sample coffees: {e}")

def init_database():
    """Initialize database with all required data"""
    print("\n" + "="*50)
    print("Initializing Coffee Shop Database")
    print("="*50)
    
    # Delete existing database if you want a fresh start
    # if os.path.exists('coffee_shop.db'):
    #     os.remove('coffee_shop.db')
    #     print("Old database removed")
    
    conn = create_connection()
    if conn:
        try:
            create_tables(conn)
            create_default_admin(conn)
            add_sample_coffees(conn)
            print("\n✓ Database initialization complete!")
            print("="*50)
        except Exception as e:
            print(f"✗ Error during initialization: {e}")
        finally:
            conn.close()
    else:
        print("✗ Failed to initialize database!")