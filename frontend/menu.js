// Juice Cafe - Menu Page JavaScript

// State management
let menuItems = [];
let currentOrder = [];
let isSubmitting = false;

// DOM elements
let menuGrid;
let orderItemsContainer;
let orderTotalElement;
let placeOrderBtn;
let confirmationModal;
let confirmedOrderIdElement;
let closeModalBtn;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('Menu page loaded');
    
    // Get DOM elements
    menuGrid = document.getElementById('menu-grid');
    orderItemsContainer = document.getElementById('order-items');
    orderTotalElement = document.getElementById('order-total');
    placeOrderBtn = document.getElementById('place-order-btn');
    confirmationModal = document.getElementById('confirmation-modal');
    confirmedOrderIdElement = document.getElementById('confirmed-order-id');
    closeModalBtn = document.getElementById('close-modal-btn');
    
    // Set up event listeners
    placeOrderBtn.addEventListener('click', handlePlaceOrder);
    closeModalBtn.addEventListener('click', closeConfirmationModal);
    
    // Load menu items
    fetchMenuItems();
});

// Fetch menu items from API
async function fetchMenuItems() {
    try {
        menuGrid.innerHTML = '<div class="loading">Loading menu</div>';
        
        const response = await fetch('/api/menu');
        
        if (!response.ok) {
            throw new Error(`Failed to load menu: ${response.status}`);
        }
        
        menuItems = await response.json();
        renderMenuItems();
        
    } catch (error) {
        console.error('Error fetching menu:', error);
        menuGrid.innerHTML = `
            <div class="error-message">
                Failed to load menu. Please refresh the page to try again.
            </div>
        `;
    }
}

// Render menu items to the grid
function renderMenuItems() {
    if (!menuItems || menuItems.length === 0) {
        menuGrid.innerHTML = '<p>No menu items available</p>';
        return;
    }
    
    menuGrid.innerHTML = menuItems.map(item => `
        <div class="menu-item" data-item-id="${item.id}">
            <img src="${item.imageUrl}" alt="${item.name}" class="menu-item-image" 
                 onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22200%22 height=%22200%22%3E%3Crect fill=%22%23FF8C42%22 width=%22200%22 height=%22200%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 dominant-baseline=%22middle%22 text-anchor=%22middle%22 fill=%22white%22 font-size=%2220%22%3EJuice%3C/text%3E%3C/svg%3E'">
            <div class="menu-item-content">
                <div class="menu-item-category">${item.category}</div>
                <h3 class="menu-item-name">${item.name}</h3>
                <p class="menu-item-description">${item.description}</p>
                <div class="menu-item-footer">
                    <span class="menu-item-price">$${item.price.toFixed(2)}</span>
                </div>
                <button class="add-to-order-btn" onclick="addToOrder('${item.id}')">
                    Add to Order
                </button>
            </div>
        </div>
    `).join('');
}

// Add item to current order
function addToOrder(itemId) {
    const menuItem = menuItems.find(item => item.id === itemId);
    
    if (!menuItem) {
        console.error('Menu item not found:', itemId);
        return;
    }
    
    // Check if item already in order
    const existingItem = currentOrder.find(item => item.menuItemId === itemId);
    
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        currentOrder.push({
            menuItemId: menuItem.id,
            name: menuItem.name,
            price: menuItem.price,
            quantity: 1
        });
    }
    
    updateOrderDisplay();
}

// Remove item from order
function removeFromOrder(itemId) {
    const itemIndex = currentOrder.findIndex(item => item.menuItemId === itemId);
    
    if (itemIndex !== -1) {
        if (currentOrder[itemIndex].quantity > 1) {
            currentOrder[itemIndex].quantity -= 1;
        } else {
            currentOrder.splice(itemIndex, 1);
        }
    }
    
    updateOrderDisplay();
}

// Update order summary display
function updateOrderDisplay() {
    if (currentOrder.length === 0) {
        orderItemsContainer.innerHTML = '<p class="empty-order">No items yet</p>';
        orderTotalElement.textContent = '0.00';
        placeOrderBtn.disabled = true;
        return;
    }
    
    // Render order items
    orderItemsContainer.innerHTML = currentOrder.map(item => `
        <div class="order-item">
            <span class="order-item-name">${item.name}</span>
            <span class="order-item-quantity">x${item.quantity}</span>
            <span class="order-item-price">$${(item.price * item.quantity).toFixed(2)}</span>
            <button class="remove-item-btn" onclick="removeFromOrder('${item.menuItemId}')" 
                    title="Remove one">×</button>
        </div>
    `).join('');
    
    // Calculate and display total
    const total = currentOrder.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    orderTotalElement.textContent = total.toFixed(2);
    
    // Enable place order button
    placeOrderBtn.disabled = false;
}

// Handle order submission
async function handlePlaceOrder() {
    if (isSubmitting || currentOrder.length === 0) {
        return;
    }
    
    isSubmitting = true;
    placeOrderBtn.classList.add('loading');
    placeOrderBtn.disabled = true;
    
    try {
        // Prepare order data - expand items based on quantity
        const orderItems = [];
        currentOrder.forEach(item => {
            for (let i = 0; i < item.quantity; i++) {
                orderItems.push({
                    menuItemId: item.menuItemId,
                    name: item.name
                });
            }
        });
        
        const response = await fetch('/api/orders', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ items: orderItems })
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `Order failed: ${response.status}`);
        }
        
        const result = await response.json();
        
        // Show confirmation modal with Order ID
        showConfirmationModal(result.orderId);
        
        // Clear current order
        currentOrder = [];
        updateOrderDisplay();
        
    } catch (error) {
        console.error('Error placing order:', error);
        alert(`Failed to place order: ${error.message}\n\nPlease try again.`);
    } finally {
        isSubmitting = false;
        placeOrderBtn.classList.remove('loading');
        placeOrderBtn.disabled = currentOrder.length === 0;
    }
}

// Show confirmation modal
function showConfirmationModal(orderId) {
    confirmedOrderIdElement.textContent = orderId;
    confirmationModal.classList.add('active');
}

// Close confirmation modal
function closeConfirmationModal() {
    confirmationModal.classList.remove('active');
}
