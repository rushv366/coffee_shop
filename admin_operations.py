import sqlite3
from database import create_connection
from models import Coffee

class AdminOperations:
    def __init__(self, conn):
        self.conn = conn
    
    def add_coffee(self, name, description, price, category):
        """Add a new coffee to the menu"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
            INSERT INTO coffees (name, description, price, category)
            VALUES (?, ?, ?, ?)
            ''', (name, description, price, category))
            self.conn.commit()
            print(f"Coffee '{name}' added successfully!")
            return True
        except Exception as e:
            print(f"Error adding coffee: {e}")
            return False
    
    def update_coffee(self, coffee_id, name=None, description=None, price=None, category=None, is_available=None):
        """Update coffee details"""
        try:
            cursor = self.conn.cursor()
            updates = []
            values = []
            
            if name:
                updates.append("name = ?")
                values.append(name)
            if description:
                updates.append("description = ?")
                values.append(description)
            if price:
                updates.append("price = ?")
                values.append(price)
            if category:
                updates.append("category = ?")
                values.append(category)
            if is_available is not None:
                updates.append("is_available = ?")
                values.append(is_available)
            
            values.append(coffee_id)
            
            if updates:
                query = f"UPDATE coffees SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(query, values)
                self.conn.commit()
                print(f"Coffee ID {coffee_id} updated successfully!")
                return True
            else:
                print("No updates provided!")
                return False
        except Exception as e:
            print(f"Error updating coffee: {e}")
            return False
    
    def delete_coffee(self, coffee_id):
        """Delete a coffee from the menu"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM coffees WHERE id = ?", (coffee_id,))
            self.conn.commit()
            print(f"Coffee ID {coffee_id} deleted successfully!")
            return True
        except Exception as e:
            print(f"Error deleting coffee: {e}")
            return False
    
    def view_all_coffees(self):
        """View all coffees in the menu"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM coffees ORDER BY id")
            coffees = [Coffee.from_db_row(row) for row in cursor.fetchall()]
            
            print("\n" + "="*60)
            print("COFFEE MENU")
            print("="*60)
            for coffee in coffees:
                status = "✓ Available" if coffee.is_available else "✗ Not Available"
                print(f"ID: {coffee.id}")
                print(f"Name: {coffee.name}")
                print(f"Description: {coffee.description}")
                print(f"Price: ${coffee.price:.2f}")
                print(f"Category: {coffee.category}")
                print(f"Status: {status}")
                print("-" * 40)
            
            return coffees
        except Exception as e:
            print(f"Error viewing coffees: {e}")
            return []
    
    def view_all_orders(self):
        """View all orders"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
            SELECT o.*, u.first_name, u.last_name, u.email 
            FROM orders o 
            JOIN users u ON o.user_id = u.id 
            ORDER BY o.created_at DESC
            ''')
            
            orders = cursor.fetchall()
            
            print("\n" + "="*60)
            print("ALL ORDERS")
            print("="*60)
            
            for order in orders:
                print(f"Order ID: {order[0]}")
                print(f"Customer: {order[5]} {order[6]} ({order[7]})")
                print(f"Total: ${order[2]:.2f}")
                print(f"Status: {order[3]}")
                print(f"Date: {order[4]}")
                
                # Get order items
                cursor.execute('''
                SELECT c.name, oi.quantity, oi.price 
                FROM order_items oi 
                JOIN coffees c ON oi.coffee_id = c.id 
                WHERE oi.order_id = ?
                ''', (order[0],))
                
                items = cursor.fetchall()
                for item in items:
                    print(f"  - {item[0]} x{item[1]}: ${item[2]:.2f}")
                
                print("-" * 40)
            
            return orders
        except Exception as e:
            print(f"Error viewing orders: {e}")
            return []
    
    def update_order_status(self, order_id, status):
        """Update order status"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
            UPDATE orders SET status = ? WHERE id = ?
            ''', (status, order_id))
            self.conn.commit()
            print(f"Order ID {order_id} status updated to '{status}'!")
            return True
        except Exception as e:
            print(f"Error updating order status: {e}")
            return False