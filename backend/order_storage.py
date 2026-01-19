"""
Order Storage Module
Handles in-memory order storage with Order and OrderItem data classes
"""
import time
import random
import string
from dataclasses import dataclass, field
from typing import List


@dataclass
class OrderItem:
    """Represents a single item within an order"""
    menu_item_id: str
    name: str
    quantity: int = 1


@dataclass
class Order:
    """Represents a complete order with unique ID"""
    id: str
    items: List[OrderItem]
    timestamp: float
    status: str = "pending"


class OrderStorage:
    """In-memory storage for orders"""
    
    def __init__(self):
        self.orders: List[Order] = []
        self.order_counter: int = 0
    
    def add_order(self, order: Order) -> None:
        """Add an order to storage"""
        self.orders.append(order)
        self.order_counter += 1
    
    def get_all_orders(self) -> List[Order]:
        """Retrieve all orders"""
        return self.orders
    
    def get_order_by_id(self, order_id: str) -> Order | None:
        """Retrieve a specific order by ID"""
        for order in self.orders:
            if order.id == order_id:
                return order
        return None
    
    def clear_orders(self) -> None:
        """Clear all orders (useful for testing or restart)"""
        self.orders = []
        self.order_counter = 0
    
    def get_next_order_number(self) -> int:
        """Get the next order number"""
        return self.order_counter + 1


def generate_order_id() -> str:
    """
    Generate a unique Order ID using simple sequential numbering
    Format: {number}
    Example: 1, 2, 3, etc.
    """
    next_number = order_storage.get_next_order_number()
    return str(next_number)


# Global order storage instance
order_storage = OrderStorage()
