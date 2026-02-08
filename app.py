from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'coffee-shop-secret-key-2024'

# Create database
def init_db():
    conn = sqlite3.connect('coffee.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        contact_number TEXT,
        is_admin BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS coffees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        category TEXT,
        is_available BOOLEAN DEFAULT 1,
        image_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Add admin if not exists
    cursor.execute("SELECT * FROM users WHERE email='admin@coffee.com'")
    if not cursor.fetchone():
        cursor.execute('''
        INSERT INTO users (first_name, last_name, email, password, contact_number, is_admin)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', ('Admin', 'User', 'admin@coffee.com', 'admin123', '1234567890', 1))
    
    # Add sample coffees
    cursor.execute("SELECT COUNT(*) FROM coffees")
    if cursor.fetchone()[0] == 0:
        coffees = [
            ('Espresso', 'Strong and concentrated coffee', 3.50, 'Hot', '☕'),
            ('Cappuccino', 'Espresso with steamed milk foam', 4.50, 'Hot', '🥛'),
            ('Latte', 'Espresso with steamed milk', 4.75, 'Hot', '🥛'),
            ('Americano', 'Espresso with hot water', 3.75, 'Hot', '☕'),
            ('Mocha', 'Chocolate-flavored latte', 5.00, 'Hot', '🍫'),
            ('Macchiato', 'Espresso with a dash of milk', 4.25, 'Hot', '🥛'),
            ('Iced Coffee', 'Chilled coffee with ice', 4.00, 'Cold', '❄️'),
            ('Cold Brew', 'Slow-steeped cold coffee', 4.50, 'Cold', '❄️')
        ]
        cursor.executemany('''
        INSERT INTO coffees (name, description, price, category, image_url)
        VALUES (?, ?, ?, ?, ?)
        ''', coffees)
    
    conn.commit()
    conn.close()
    print("✓ Database initialized successfully!")

# Initialize database
init_db()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        if not email or not password:
            flash('Please fill in all fields!', 'error')
            return redirect('/login')
        
        conn = sqlite3.connect('coffee.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            session['first_name'] = user[1] or 'User'
            session['email'] = user[3]
            session['is_admin'] = bool(user[6])
            flash(f'Welcome back, {session["first_name"]}!', 'success')
            
            if session['is_admin']:
                return redirect('/admin')
            else:
                return redirect('/menu')
        else:
            flash('Invalid email or password!', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        contact = request.form.get('contact', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        # Validation
        if not all([first_name, last_name, email, contact, password, confirm_password]):
            flash('Please fill in all fields!', 'error')
            return redirect('/register')
        
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect('/register')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters!', 'error')
            return redirect('/register')
        
        try:
            conn = sqlite3.connect('coffee.db')
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO users (first_name, last_name, email, contact_number, password)
            VALUES (?, ?, ?, ?, ?)
            ''', (first_name, last_name, email, contact, password))
            conn.commit()
            conn.close()
            flash('Registration successful! Please login.', 'success')
            return redirect('/login')
        except sqlite3.IntegrityError:
            flash('Email already exists!', 'error')
        except Exception as e:
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'info')
    return redirect('/')

@app.route('/menu')
def menu():
    if 'user_id' not in session:
        flash('Please login first!', 'error')
        return redirect('/login')
    
    conn = sqlite3.connect('coffee.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM coffees WHERE is_available=1 ORDER BY category, name")
    coffees = cursor.fetchall()
    conn.close()
    
    # Group by category
    coffee_by_category = {}
    for coffee in coffees:
        category = coffee[4]  # category is at index 4
        if category not in coffee_by_category:
            coffee_by_category[category] = []
        coffee_by_category[category].append(coffee)
    
    return render_template('menu.html', 
                         coffee_by_category=coffee_by_category,
                         cart=session.get('cart', {}))

@app.route('/admin')
def admin():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Admin access required!', 'error')
        return redirect('/login')
    
    return render_template('admin_dashboard.html')

@app.route('/admin/coffees')
def admin_coffees():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Admin access required!', 'error')
        return redirect('/login')
    
    conn = sqlite3.connect('coffee.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM coffees ORDER BY id")
    coffees = cursor.fetchall()
    conn.close()
    
    return render_template('admin_coffees.html', coffees=coffees)

@app.route('/admin/add-coffee', methods=['GET', 'POST'])
def add_coffee():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Admin access required!', 'error')
        return redirect('/login')
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        price = request.form.get('price', '').strip()
        category = request.form.get('category', 'Hot').strip()
        
        if not all([name, description, price]):
            flash('Please fill in all required fields!', 'error')
            return redirect('/admin/add-coffee')
        
        try:
            price = float(price)
            conn = sqlite3.connect('coffee.db')
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO coffees (name, description, price, category)
            VALUES (?, ?, ?, ?)
            ''', (name, description, price, category))
            conn.commit()
            conn.close()
            flash('Coffee added successfully!', 'success')
            return redirect('/admin/coffees')
        except ValueError:
            flash('Invalid price format!', 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    return render_template('add_coffee.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    # Create templates directory if not exists
    os.makedirs('templates', exist_ok=True)
    
    print("="*60)
    print("COFFEE SHOP APPLICATION")
    print("="*60)
    print("Starting server...")
    print("Open your browser and visit: http://localhost:5000")
    print("\nDefault Admin Login:")
    print("Email: admin@coffee.com")
    print("Password: admin123")
    print("\nPress Ctrl+C to stop the server")
    print("="*60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)