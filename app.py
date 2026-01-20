# Juice Cafe Ordering System - Backend
from flask import Flask, jsonify, request, Response, send_from_directory
from flask_cors import CORS
import json
import time
import queue
import os
import sys

# Add backend directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from menu_data import menu_items
from order_storage import order_storage, generate_order_id, Order, OrderItem

app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)

# SSE clients for real-time updates
sse_clients = []


def broadcast_order(order):
    """
    Broadcast order to all connected SSE clients
    Sends order data as JSON in SSE format
    """
    # Convert order to dictionary for JSON serialization
    order_dict = {
        'id': order.id,
        'items': [
            {
                'menuItemId': item.menu_item_id,
                'name': item.name,
                'quantity': item.quantity
            }
            for item in order.items
        ],
        'timestamp': order.timestamp,
        'status': order.status
    }
    
    # Format as SSE message
    message = f"data: {json.dumps(order_dict)}\n\n"
    
    # Send to all connected clients
    clients_to_remove = []
    for client in sse_clients:
        try:
            client.put(message)
        except:
            # Mark client for removal if sending fails
            clients_to_remove.append(client)
    
    # Remove disconnected clients
    for client in clients_to_remove:
        sse_clients.remove(client)


# API Routes
@app.route('/api/menu', methods=['GET'])
def get_menu():
    """Serve menu items as JSON"""
    return jsonify(menu_items)


@app.route('/api/orders', methods=['POST'])
def create_order():
    """
    Accept new order submission
    Validates order data, generates Order_ID, stores in memory, and returns Order_ID
    Requirements: 2.2, 2.4, 4.1
    """
    try:
        # Get order data from request
        order_data = request.get_json()
        
        # Validate request has items
        if not order_data or 'items' not in order_data:
            return jsonify({'error': 'Order must contain items'}), 400
        
        items_data = order_data['items']
        
        # Validate order contains at least one item
        if not items_data or len(items_data) == 0:
            return jsonify({'error': 'Order must contain at least one item'}), 400
        
        # Generate unique Order_ID
        order_id = generate_order_id()
        
        # Create OrderItem objects from request data
        order_items = []
        for item_data in items_data:
            # Validate item structure
            if 'menuItemId' not in item_data or 'name' not in item_data:
                return jsonify({'error': 'Invalid item structure'}), 400
            
            order_item = OrderItem(
                menu_item_id=item_data['menuItemId'],
                name=item_data['name'],
                quantity=item_data.get('quantity', 1)
            )
            order_items.append(order_item)
        
        # Create Order object
        order = Order(
            id=order_id,
            items=order_items,
            timestamp=time.time(),
            status='pending'
        )
        
        # Store order in memory
        order_storage.add_order(order)
        
        # Broadcast order to all connected SSE clients
        broadcast_order(order)
        
        # Return Order_ID in response
        return jsonify({
            'orderId': order_id,
            'message': 'Order placed successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Failed to process order: {str(e)}'}), 500


@app.route('/api/orders/stream', methods=['GET'])
def stream_orders():
    """
    Server-Sent Events endpoint for real-time order updates
    Maintains connection and pushes new orders to kitchen display
    Requirements: 3.1, 3.4
    """
    def event_stream():
        # Create a queue for this client
        client_queue = queue.Queue()
        sse_clients.append(client_queue)
        
        try:
            # Keep connection alive and send messages
            while True:
                try:
                    # Wait for message with timeout to allow checking connection
                    message = client_queue.get(timeout=30)
                    yield message
                except queue.Empty:
                    # Send heartbeat comment to keep connection alive
                    yield ": heartbeat\n\n"
        except GeneratorExit:
            # Client disconnected
            if client_queue in sse_clients:
                sse_clients.remove(client_queue)
    
    # Set SSE headers
    return Response(
        event_stream(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'  # Disable buffering for nginx
        }
    )


@app.route('/')
def serve_menu_page():
    """Serve the menu page (index.html)"""
    return app.send_static_file('index.html')


@app.route('/kitchen')
def serve_kitchen_page():
    """Serve the kitchen display page"""
    return app.send_static_file('kitchen.html')


@app.route('/assets/<path:filename>')
def serve_assets(filename):
    """Serve static assets (images, etc.)"""
    assets_dir = os.path.join(app.static_folder, 'assets')
    return send_from_directory(assets_dir, filename)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
