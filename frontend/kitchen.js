// Juice Cafe - Kitchen Display JavaScript

// State management
let orders = [];
let eventSource = null;
let connectionStatus = 'disconnected';

// DOM elements
let ordersContainer;
let noOrdersMessage;
let statusIndicator;
let statusText;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('Kitchen display loaded');
    
    // Get DOM elements
    ordersContainer = document.getElementById('orders-container');
    noOrdersMessage = document.getElementById('no-orders');
    statusIndicator = document.getElementById('status-indicator');
    statusText = document.getElementById('status-text');
    
    // Connect to SSE stream
    connectToOrderStream();
});

/**
 * Establish SSE connection to receive real-time order updates
 */
function connectToOrderStream() {
    try {
        // Close existing connection if any
        if (eventSource) {
            eventSource.close();
        }
        
        // Create new SSE connection
        eventSource = new EventSource('http://localhost:5000/api/orders/stream');
        
        // Handle successful connection
        eventSource.onopen = () => {
            console.log('SSE connection established');
            updateConnectionStatus('connected');
        };
        
        // Handle incoming order messages
        eventSource.onmessage = (event) => {
            console.log('Received order:', event.data);
            try {
                const order = JSON.parse(event.data);
                addOrderToDisplay(order);
            } catch (error) {
                console.error('Error parsing order data:', error);
            }
        };
        
        // Handle connection errors
        eventSource.onerror = (error) => {
            console.error('SSE connection error:', error);
            updateConnectionStatus('disconnected');
            
            // Close the connection
            if (eventSource) {
                eventSource.close();
            }
            
            // Attempt reconnection after 5 seconds
            setTimeout(() => {
                console.log('Attempting to reconnect...');
                connectToOrderStream();
            }, 5000);
        };
        
    } catch (error) {
        console.error('Error establishing SSE connection:', error);
        updateConnectionStatus('disconnected');
        
        // Retry connection after 5 seconds
        setTimeout(() => {
            connectToOrderStream();
        }, 5000);
    }
}

/**
 * Update connection status indicator
 * @param {string} status - 'connected' or 'disconnected'
 */
function updateConnectionStatus(status) {
    connectionStatus = status;
    
    if (status === 'connected') {
        statusIndicator.classList.remove('disconnected');
        statusText.textContent = 'Connected';
    } else {
        statusIndicator.classList.add('disconnected');
        statusText.textContent = 'Disconnected';
    }
}

/**
 * Add a new order to the display
 * @param {Object} order - Order object with id, items, and timestamp
 */
function addOrderToDisplay(order) {
    // Add order to state array
    orders.push(order);
    
    // Sort orders chronologically (oldest first)
    orders.sort((a, b) => a.timestamp - b.timestamp);
    
    // Re-render all orders
    renderOrders();
    
    // Auto-scroll to the newest order
    setTimeout(() => {
        scrollToNewestOrder();
    }, 100);
}

/**
 * Render all orders in the display
 */
function renderOrders() {
    // Clear container
    ordersContainer.innerHTML = '';
    
    if (orders.length === 0) {
        // Show "no orders" message
        ordersContainer.innerHTML = '<p class="no-orders" id="no-orders">Waiting for orders...</p>';
        return;
    }
    
    // Render each order
    orders.forEach((order, index) => {
        const orderCard = createOrderCard(order, index === orders.length - 1);
        ordersContainer.appendChild(orderCard);
    });
}

/**
 * Create an order card element
 * @param {Object} order - Order object
 * @param {boolean} isNewest - Whether this is the newest order
 * @returns {HTMLElement} Order card element
 */
function createOrderCard(order, isNewest) {
    const card = document.createElement('div');
    card.className = 'order-card';
    card.id = `order-${order.id}`;
    
    // Add animation class for new orders
    if (isNewest) {
        card.classList.add('new-order');
        // Remove animation class after it completes
        setTimeout(() => {
            card.classList.remove('new-order');
        }, 2000);
    }
    
    // Create order header with ID and time
    const header = document.createElement('div');
    header.className = 'order-header';
    
    const orderId = document.createElement('div');
    orderId.className = 'order-id-display';
    orderId.textContent = order.id;
    
    const orderTime = document.createElement('div');
    orderTime.className = 'order-time';
    orderTime.textContent = formatTimestamp(order.timestamp);
    
    header.appendChild(orderId);
    header.appendChild(orderTime);
    
    // Create items list
    const itemsList = document.createElement('ul');
    itemsList.className = 'order-items-list';
    
    order.items.forEach(item => {
        const itemElement = document.createElement('li');
        itemElement.className = 'order-item-display';
        
        const bullet = document.createElement('span');
        bullet.className = 'order-item-bullet';
        
        const itemName = document.createElement('span');
        itemName.className = 'order-item-name-display';
        itemName.textContent = item.name;
        
        const itemQuantity = document.createElement('span');
        itemQuantity.className = 'order-item-quantity-display';
        itemQuantity.textContent = `x${item.quantity}`;
        
        itemElement.appendChild(bullet);
        itemElement.appendChild(itemName);
        itemElement.appendChild(itemQuantity);
        
        itemsList.appendChild(itemElement);
    });
    
    // Assemble card
    card.appendChild(header);
    card.appendChild(itemsList);
    
    return card;
}

/**
 * Format timestamp to readable time
 * @param {number} timestamp - Unix timestamp
 * @returns {string} Formatted time string
 */
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    const seconds = date.getSeconds().toString().padStart(2, '0');
    return `${hours}:${minutes}:${seconds}`;
}

/**
 * Auto-scroll to the newest order
 */
function scrollToNewestOrder() {
    if (orders.length > 0) {
        const newestOrderId = orders[orders.length - 1].id;
        const newestOrderElement = document.getElementById(`order-${newestOrderId}`);
        
        if (newestOrderElement) {
            newestOrderElement.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'end' 
            });
        }
    }
}

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    if (eventSource) {
        eventSource.close();
    }
});

