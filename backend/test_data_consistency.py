"""
Property-Based Tests for Data Consistency
Tests data consistency validation across the juice cafe ordering system
"""
import pytest
from hypothesis import given, strategies as st, settings
from hypothesis.strategies import composite
import json
from order_storage import Order, OrderItem, OrderStorage, generate_order_id
from app import broadcast_order
import queue


# Strategies for generating test data
@composite
def order_item_strategy(draw):
    """Generate a random OrderItem"""
    menu_item_id = draw(st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pd'))))
    name = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Zs'))))
    quantity = draw(st.integers(min_value=1, max_value=10))
    return OrderItem(menu_item_id=menu_item_id, name=name, quantity=quantity)


@composite
def order_strategy(draw):
    """Generate a random Order"""
    order_id = generate_order_id()
    items = draw(st.lists(order_item_strategy(), min_size=1, max_size=10))
    timestamp = draw(st.floats(min_value=1000000000, max_value=2000000000))
    status = draw(st.sampled_from(['pending', 'completed']))
    return Order(id=order_id, items=items, timestamp=timestamp, status=status)


class TestDataConsistency:
    """
    Property-Based Tests for Data Consistency (Task 8)
    Feature: juice-cafe-ordering
    """
    
    @settings(max_examples=100)
    @given(order=order_strategy())
    def test_property_8_data_consistency_across_pages(self, order):
        """
        Property 8: Data Consistency Across Pages
        For any order submitted from the menu page, the order data received by 
        the kitchen display should be identical to the order data stored in memory.
        
        Feature: juice-cafe-ordering, Property 8: Data Consistency Across Pages
        Validates: Requirements 4.2, 4.3
        """
        # Create a fresh storage instance for this test
        storage = OrderStorage()
        
        # Store the order in memory (simulating menu page submission)
        storage.add_order(order)
        
        # Retrieve the order from storage (simulating what kitchen display would query)
        retrieved_order = storage.get_order_by_id(order.id)
        
        # Verify the order exists
        assert retrieved_order is not None, "Order should be retrievable from storage"
        
        # Verify all order data is identical
        assert retrieved_order.id == order.id, "Order ID should match"
        assert retrieved_order.timestamp == order.timestamp, "Timestamp should match"
        assert retrieved_order.status == order.status, "Status should match"
        assert len(retrieved_order.items) == len(order.items), "Number of items should match"
        
        # Verify each item is identical
        for i, (retrieved_item, original_item) in enumerate(zip(retrieved_order.items, order.items)):
            assert retrieved_item.menu_item_id == original_item.menu_item_id, \
                f"Item {i} menu_item_id should match"
            assert retrieved_item.name == original_item.name, \
                f"Item {i} name should match"
            assert retrieved_item.quantity == original_item.quantity, \
                f"Item {i} quantity should match"
        
        # Simulate SSE broadcast (what kitchen display receives)
        # Create a mock SSE client queue
        client_queue = queue.Queue()
        
        # Temporarily add to global sse_clients for broadcast
        from app import sse_clients
        sse_clients.append(client_queue)
        
        try:
            # Broadcast the order
            broadcast_order(order)
            
            # Get the broadcasted message
            message = client_queue.get(timeout=1)
            
            # Parse the SSE message format (data: {json}\n\n)
            assert message.startswith("data: "), "SSE message should start with 'data: '"
            json_str = message[6:].strip()  # Remove "data: " prefix and whitespace
            broadcasted_data = json.loads(json_str)
            
            # Verify broadcasted data matches original order
            assert broadcasted_data['id'] == order.id, "Broadcasted Order ID should match"
            assert broadcasted_data['timestamp'] == order.timestamp, "Broadcasted timestamp should match"
            assert broadcasted_data['status'] == order.status, "Broadcasted status should match"
            assert len(broadcasted_data['items']) == len(order.items), \
                "Broadcasted items count should match"
            
            # Verify each broadcasted item matches original
            for i, (broadcasted_item, original_item) in enumerate(zip(broadcasted_data['items'], order.items)):
                assert broadcasted_item['menuItemId'] == original_item.menu_item_id, \
                    f"Broadcasted item {i} menuItemId should match"
                assert broadcasted_item['name'] == original_item.name, \
                    f"Broadcasted item {i} name should match"
                assert broadcasted_item['quantity'] == original_item.quantity, \
                    f"Broadcasted item {i} quantity should match"
        
        finally:
            # Clean up
            if client_queue in sse_clients:
                sse_clients.remove(client_queue)
    
    @settings(max_examples=100)
    @given(order=order_strategy())
    def test_property_9_multiple_items_share_order_id(self, order):
        """
        Property 9: Multiple Items Share Order ID
        For any order containing multiple items, all items in that order should 
        be associated with the same Order_ID.
        
        Feature: juice-cafe-ordering, Property 9: Multiple Items Share Order ID
        Validates: Requirements 5.3
        """
        # Ensure the order has multiple items for this test
        # (The strategy already generates orders with 1-10 items)
        
        # All items should be part of the same order object with the same ID
        order_id = order.id
        
        # Verify all items are associated with this order
        for item in order.items:
            # Items don't store order_id directly, but they're part of the order
            # The association is maintained by the Order object containing them
            assert item in order.items, "Item should be part of the order"
        
        # Store the order and verify retrieval maintains the association
        storage = OrderStorage()
        storage.add_order(order)
        
        retrieved_order = storage.get_order_by_id(order_id)
        assert retrieved_order is not None, "Order should be retrievable"
        assert retrieved_order.id == order_id, "Retrieved order should have same ID"
        
        # Verify all items are still associated with the same order ID
        assert len(retrieved_order.items) == len(order.items), \
            "All items should be associated with the order"
        
        for original_item, retrieved_item in zip(order.items, retrieved_order.items):
            assert retrieved_item.menu_item_id == original_item.menu_item_id, \
                "Items should maintain their identity within the order"
            assert retrieved_item.name == original_item.name, \
                "Items should maintain their data within the order"
    
    @settings(max_examples=100)
    @given(order=order_strategy())
    def test_property_10_order_id_displayed_in_both_locations(self, order):
        """
        Property 10: Order ID Displayed in Both Locations
        For any order, the Order_ID should appear in both the menu page 
        confirmation and the kitchen display.
        
        Feature: juice-cafe-ordering, Property 10: Order ID Displayed in Both Locations
        Validates: Requirements 5.2
        """
        # Store the order (simulating successful submission from menu page)
        storage = OrderStorage()
        storage.add_order(order)
        
        # Verify Order_ID is available for menu page confirmation
        # (In the actual API, this is returned in the response)
        order_id_for_confirmation = order.id
        assert order_id_for_confirmation is not None, \
            "Order ID should be available for menu page confirmation"
        assert len(order_id_for_confirmation) > 0, \
            "Order ID should not be empty"
        assert order_id_for_confirmation.startswith("ORD-"), \
            "Order ID should follow the expected format"
        
        # Verify Order_ID is available in storage for kitchen display
        retrieved_order = storage.get_order_by_id(order.id)
        assert retrieved_order is not None, \
            "Order should be retrievable for kitchen display"
        order_id_for_kitchen = retrieved_order.id
        assert order_id_for_kitchen is not None, \
            "Order ID should be available for kitchen display"
        
        # Verify both locations have the same Order_ID
        assert order_id_for_confirmation == order_id_for_kitchen, \
            "Order ID should be identical in both menu confirmation and kitchen display"
        
        # Verify Order_ID is included in SSE broadcast to kitchen display
        client_queue = queue.Queue()
        from app import sse_clients
        sse_clients.append(client_queue)
        
        try:
            broadcast_order(order)
            message = client_queue.get(timeout=1)
            
            # Parse SSE message
            json_str = message[6:].strip()  # Remove "data: " prefix
            broadcasted_data = json.loads(json_str)
            
            # Verify Order_ID is in the broadcasted data
            assert 'id' in broadcasted_data, \
                "Broadcasted data should contain Order ID"
            assert broadcasted_data['id'] == order.id, \
                "Broadcasted Order ID should match the original"
        
        finally:
            if client_queue in sse_clients:
                sse_clients.remove(client_queue)
