class User:
    def __init__(self, id, first_name, last_name, email, contact_number, is_admin=False):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.contact_number = contact_number
        self.is_admin = is_admin
    
    @staticmethod
    def from_db_row(row):
        return User(
            id=row[0],
            first_name=row[1],
            last_name=row[2],
            email=row[3],
            contact_number=row[4],
            is_admin=bool(row[6])
        )

class Coffee:
    def __init__(self, id, name, description, price, category, is_available=True):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.category = category
        self.is_available = is_available
    
    @staticmethod
    def from_db_row(row):
        return Coffee(
            id=row[0],
            name=row[1],
            description=row[2],
            price=row[3],
            category=row[4],
            is_available=bool(row[5])
        )

class Order:
    def __init__(self, id, user_id, total_amount, status, created_at):
        self.id = id
        self.user_id = user_id
        self.total_amount = total_amount
        self.status = status
        self.created_at = created_at
    
    @staticmethod
    def from_db_row(row):
        return Order(
            id=row[0],
            user_id=row[1],
            total_amount=row[2],
            status=row[3],
            created_at=row[4]
        )

class OrderItem:
    def __init__(self, id, order_id, coffee_id, quantity, price):
        self.id = id
        self.order_id = order_id
        self.coffee_id = coffee_id
        self.quantity = quantity
        self.price = price
    
    @staticmethod
    def from_db_row(row):
        return OrderItem(
            id=row[0],
            order_id=row[1],
            coffee_id=row[2],
            quantity=row[3],
            price=row[4]
        )