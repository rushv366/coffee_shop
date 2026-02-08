import sqlite3
from models import Coffee, Order, OrderItem

class UserOperations:
    def __init__(self, conn):
        self.conn = conn
    
    def view_available_coffees(self):
        """View available coffees"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM coffees WHERE is_available = 1 ORDER BY category, name")
            coffees = [Coffee.from_db_row(row) for row in cursor.fetchall()]
            
            print("\n" + "="*60)
            print("AVAILABLE COFFEES")
            print("="*60)
            
            current_category = None
            for coffee in coffees:
                if coffee.category != current_category:
                    current_category = coffee.category
                    print(f"\n{current_category.upper()} COFFEES:")
                    print("-" * 40)
                
                print(f"ID: {coffee.id}")
                print(f"Name: {coffee.name}")
                print(f"Description: {coffee.description}")
                print(f"Price: ${coffee.price:.2f}")
                print("-" * 40)
            
            return coffees
        except Exception as e:
            print(f"Error viewing coffees: {e}")
            return []
    
    def place_order(self, user_id, coffee_quantities):
        """Place a new order"""
        try:
            cursor = self.conn.cursor()
            
            # Calculate total amount
            total_amount = 0
            order_items = []
            
            for coffee_id, quantity in coffee_quantities.items():
                cursor.execute("SELECT price FROM coffees WHERE id = ? AND is_available = 1", (coffee_id,))
                result = cursor.fetchone()
                
                if result:
                    price = result[0]
                    total_amount += price * quantity
                    order_items.append((coffee_id, quantity, price))
            
            if not order_items:
                print("No valid items in order!")
                return None
            
            # Create order
            cursor.execute('''
            INSERT INTO orders (user_id, total_amount, status)
            VALUES (?, ?, ?)
            ''', (user_id, total_amount, 'pending'))
            
            order_id = cursor.lastrowid
            
            # Add order items
            for coffee_id, quantity, price in order_items:
                cursor.execute('''
                INSERT INTO order_items (order_id, coffee_id, quantity, price)
                VALUES (?, ?, ?, ?)
                ''', (order_id, coffee_id, quantity, price))
            
            self.conn.commit()
            
            # Get coffee names for display
            cursor.execute('''
            SELECT c.name, oi.quantity, oi.price 
            FROM order_items oi 
            JOIN coffees c ON oi.coffee_id = c.id 
            WHERE oi.order_id = ?
            ''', (order_id,))
            
            items = cursor.fetchall()
            
            print("\n" + "="*60)
            print("ORDER CONFIRMED!")
            print("="*60)
            print(f"Order ID: {order_id}")
            print("\nItems:")
            for item in items:
                print(f"  - {item[0]} x{item[1]}: ${item[2]:.2f}")
            print(f"\nTotal Amount: ${total_amount:.2f}")
            print("Status: Pending")
            print("="*60)
            
            return order_id
        except Exception as e:
            print(f"Error placing order: {e}")
            return None
    
    def view_my_orders(self, user_id):
        """View user's orders"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
            SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC
            ''', (user_id,))
            
            orders = [Order.from_db_row(row) for row in cursor.fetchall()]
            
            print("\n" + "="*60)
            print("MY ORDERS")
            print("="*60)
            
            for order in orders:
                print(f"Order ID: {order.id}")
                print(f"Total: ${order.total_amount:.2f}")
                print(f"Status: {order.status}")
                print(f"Date: {order.created_at}")
                
                # Get order items
                cursor.execute('''
                SELECT c.name, oi.quantity, oi.price 
                FROM order_items oi 
                JOIN coffees c ON oi.coffee_id = c.id 
                WHERE oi.order_id = ?
                ''', (order.id,))
                
                items = cursor.fetchall()
                for item in items:
                    print(f"  - {item[0]} x{item[1]}: ${item[2]:.2f}")
                
                print("-" * 40)
            
            return orders
        except Exception as e:
            print(f"Error viewing orders: {e}")
            return []