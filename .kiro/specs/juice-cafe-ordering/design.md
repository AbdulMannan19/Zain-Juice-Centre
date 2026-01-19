# Design Document: Juice Cafe Ordering System

## Overview

The Juice Cafe Ordering System is a lightweight, real-time web application consisting of two distinct pages: a customer-facing menu interface and a kitchen display system. The application emphasizes modern, vibrant UI design with a juice theme while maintaining simplicity through in-memory data storage and real-time order synchronization.

The system architecture follows a client-server model where the server maintains order state in memory and pushes updates to connected clients using Server-Sent Events (SSE) for unidirectional server-to-client communication. This approach is ideal for our use case where the kitchen display needs to receive order updates but doesn't need to send data back to the server.

## Architecture

### System Components

```
┌─────────────────┐         ┌─────────────────┐
│   Menu Page     │         │ Kitchen Display │
│   (Customer)    │         │    (Staff)      │
└────────┬────────┘         └────────┬────────┘
         │                           │
         │ HTTP POST                 │ SSE Stream
         │ (Place Order)             │ (Receive Orders)
         │                           │
         └───────────┬───────────────┘
                     │
              ┌──────▼──────┐
              │   Server    │
              │             │
              │ ┌─────────┐ │
              │ │In-Memory│ │
              │ │  Store  │ │
              │ └─────────┘ │
              └─────────────┘
```

### Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla or lightweight framework)
- **Backend**: Node.js with Express.js
- **Real-time Communication**: Server-Sent Events (SSE)
- **Data Storage**: In-memory JavaScript objects/arrays
- **Styling**: Modern CSS with CSS Grid/Flexbox for responsive layouts

### Communication Flow

1. **Order Placement**: Customer submits order via HTTP POST from Menu Page
2. **Order Storage**: Server stores order in memory and generates unique Order_ID
3. **Real-time Broadcast**: Server pushes order to all connected Kitchen Display clients via SSE
4. **Display Update**: Kitchen Display receives event and updates UI without refresh

## Components and Interfaces

### 1. Menu Page Component

**Purpose**: Customer-facing interface for browsing menu and placing orders

**Key Elements**:
- Header with cafe logo and branding
- Menu grid displaying juice items with images, names, descriptions, and prices
- Shopping cart/order summary section
- Order submission button
- Order confirmation modal with Order_ID

**State Management**:
```javascript
{
  menuItems: Array<MenuItem>,
  currentOrder: Array<OrderItem>,
  isSubmitting: boolean
}
```

**User Interactions**:
- Browse menu items
- Add items to order
- Remove items from order
- Submit order
- View order confirmation

### 2. Kitchen Display Component

**Purpose**: Staff-facing interface for viewing incoming orders in real-time

**Key Elements**:
- Header with cafe branding
- Order list displaying pending orders
- Each order card shows Order_ID and items
- Visual indicators for new orders
- Auto-scroll to newest orders

**State Management**:
```javascript
{
  orders: Array<Order>,
  connectionStatus: 'connected' | 'disconnected'
}
```

**SSE Connection**:
```javascript
const eventSource = new EventSource('/api/orders/stream');
eventSource.onmessage = (event) => {
  const order = JSON.parse(event.data);
  addOrderToDisplay(order);
};
```

### 3. Server Component

**Purpose**: Handle order processing, storage, and real-time broadcasting

**API Endpoints**:

- `GET /` - Serve Menu Page
- `GET /kitchen` - Serve Kitchen Display Page
- `POST /api/orders` - Accept new order submission
- `GET /api/orders/stream` - SSE endpoint for real-time order updates
- `GET /api/menu` - Retrieve menu items

**Order Processing Logic**:
```javascript
function createOrder(items) {
  const orderId = generateOrderId();
  const order = {
    id: orderId,
    items: items,
    timestamp: Date.now()
  };
  
  // Store in memory
  orders.push(order);
  
  // Broadcast to all SSE clients
  broadcastOrder(order);
  
  return orderId;
}
```

## Data Models

### MenuItem

```javascript
{
  id: string,           // Unique identifier
  name: string,         // Juice name
  description: string,  // Brief description
  price: number,        // Price in currency units
  imageUrl: string,     // Path to juice image
  category: string      // e.g., "Citrus", "Berry", "Green"
}
```

### OrderItem

```javascript
{
  menuItemId: string,   // Reference to MenuItem
  name: string,         // Item name (denormalized for display)
  quantity: number      // Number of this item
}
```

### Order

```javascript
{
  id: string,           // Unique Order_ID (e.g., "ORD-1234")
  items: Array<OrderItem>,
  timestamp: number,    // Unix timestamp
  status: string        // "pending", "completed" (future use)
}
```

### In-Memory Store Structure

```javascript
{
  menuItems: Array<MenuItem>,
  orders: Array<Order>,
  sseClients: Array<Response>  // Connected SSE clients
}
```

## Correctness Properties


*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Menu Item Selection Adds to Order

*For any* menu item in the available menu, when a customer selects that item, the current order state should contain that item.

**Validates: Requirements 2.1**

### Property 2: Order ID Uniqueness

*For any* set of orders created by the system, all Order_IDs should be distinct from one another.

**Validates: Requirements 2.2, 5.1**

### Property 3: Current Order Display Synchronization

*For any* order state with items, the displayed order summary should show all items currently in that order.

**Validates: Requirements 2.5**

### Property 4: Real-Time Order Updates

*For any* order submitted through the menu page, the kitchen display should receive and display that order without requiring a page refresh.

**Validates: Requirements 3.1, 3.4**

### Property 5: Kitchen Display Shows Complete Order Information

*For any* order displayed on the kitchen display, the rendered output should contain both the Order_ID and the names of all items in that order.

**Validates: Requirements 3.2**

### Property 6: Chronological Order Display

*For any* set of orders with different timestamps, the kitchen display should present them sorted by timestamp in ascending order (oldest first).

**Validates: Requirements 3.3**

### Property 7: In-Memory Storage Persistence

*For any* order placed through the system, querying the in-memory store immediately after placement should return that order with all its data intact.

**Validates: Requirements 4.1**

### Property 8: Data Consistency Across Pages

*For any* order submitted from the menu page, the order data received by the kitchen display should be identical to the order data stored in memory.

**Validates: Requirements 4.2, 4.3**

### Property 9: Multiple Items Share Order ID

*For any* order containing multiple items, all items in that order should be associated with the same Order_ID.

**Validates: Requirements 5.3**

### Property 10: Order ID Displayed in Both Locations

*For any* order, the Order_ID should appear in both the menu page confirmation and the kitchen display.

**Validates: Requirements 5.2**

## Error Handling

### Client-Side Error Handling

**Network Failures**:
- Display user-friendly error messages when order submission fails
- Implement retry mechanism with exponential backoff
- Preserve order data in browser session storage for recovery

**SSE Connection Loss**:
- Detect disconnection on kitchen display
- Show connection status indicator
- Automatically attempt reconnection
- Display warning when connection is lost

**Invalid Input**:
- Validate order contains at least one item before submission
- Prevent submission of empty orders
- Show validation errors inline

### Server-Side Error Handling

**Invalid Order Data**:
- Validate incoming order structure
- Return 400 Bad Request with descriptive error message
- Log validation failures for debugging

**SSE Client Management**:
- Handle client disconnections gracefully
- Clean up closed connections from client list
- Implement heartbeat mechanism to detect stale connections

**Memory Management**:
- Implement order limit to prevent memory overflow
- Optional: Archive old orders after threshold (e.g., 1000 orders)
- Monitor memory usage and log warnings

## Testing Strategy

### Overview

The testing strategy employs a dual approach combining unit tests for specific scenarios and property-based tests for universal correctness properties. This ensures both concrete functionality and general system behavior are validated.

### Property-Based Testing

**Framework**: fast-check (for JavaScript/TypeScript)

**Configuration**:
- Minimum 100 iterations per property test
- Each test tagged with format: **Feature: juice-cafe-ordering, Property {N}: {property_text}**

**Test Coverage**:
- Property 1: Menu item selection (generate random menu items and verify addition)
- Property 2: Order ID uniqueness (generate multiple orders and verify no duplicates)
- Property 3: Order display sync (generate random order states and verify display)
- Property 4: Real-time updates (simulate order submission and verify SSE delivery)
- Property 5: Complete order info (generate random orders and verify display contains all data)
- Property 6: Chronological ordering (generate orders with random timestamps and verify sort)
- Property 7: In-memory persistence (generate random orders and verify storage)
- Property 8: Data consistency (generate orders and verify identical data across components)
- Property 9: Shared Order ID (generate orders with multiple items and verify ID consistency)
- Property 10: Order ID display (generate orders and verify presence in both locations)

### Unit Testing

**Framework**: Jest or Mocha

**Test Categories**:

1. **Component Tests**:
   - Menu page renders all menu items correctly
   - Kitchen display renders order cards correctly
   - Order confirmation modal displays Order_ID
   - Logo appears on menu page

2. **API Tests**:
   - POST /api/orders returns Order_ID on success
   - POST /api/orders returns 400 for invalid data
   - GET /api/orders/stream establishes SSE connection
   - GET /api/menu returns menu items

3. **Edge Cases**:
   - Empty order list on application restart
   - Single item orders
   - Orders with many items (stress test)
   - Rapid successive order submissions
   - SSE reconnection after disconnect

4. **Integration Tests**:
   - End-to-end order flow from menu to kitchen display
   - Multiple concurrent SSE clients receive same order
   - Order submission with network delay simulation

### Manual Testing

**Visual Design Verification**:
- Verify modern juice-themed design aesthetics
- Confirm logo placement and branding
- Test responsive layout on various devices
- Validate color scheme and visual appeal

**Usability Testing**:
- Test touch interactions on mobile devices
- Verify smooth animations and transitions
- Confirm readability across screen sizes

## UI Design Specifications

### Color Palette

Based on modern juice bar design trends ([content rephrased for compliance](https://www.gotable.com/blog/juice-bar-design-ideas/)), the application should use vibrant, fresh colors:

- **Primary**: Bright citrus orange (#FF8C42) or lime green (#A8E063)
- **Secondary**: Berry purple (#9B59B6) or tropical yellow (#F7DC6F)
- **Accent**: Fresh mint (#1ABC9C)
- **Background**: Clean white (#FFFFFF) or light cream (#FFF8E7)
- **Text**: Dark charcoal (#2C3E50) for readability

### Typography

- **Headings**: Modern sans-serif (e.g., Poppins, Montserrat) - bold, friendly
- **Body**: Clean sans-serif (e.g., Inter, Open Sans) - readable, professional
- **Sizes**: Responsive scaling with CSS clamp() for fluid typography

### Layout Structure

**Menu Page**:
```
┌─────────────────────────────────────┐
│  [Logo]    Cafe Name                │
├─────────────────────────────────────┤
│                                     │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐      │
│  │Img │ │Img │ │Img │ │Img │      │
│  │Name│ │Name│ │Name│ │Name│      │
│  │$5  │ │$6  │ │$7  │ │$5  │      │
│  └────┘ └────┘ └────┘ └────┘      │
│                                     │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐      │
│  │Img │ │Img │ │Img │ │Img │      │
│  └────┘ └────┘ └────┘ └────┘      │
│                                     │
├─────────────────────────────────────┤
│  Current Order:                     │
│  • Item 1                           │
│  • Item 2                           │
│  [Place Order Button]               │
└─────────────────────────────────────┘
```

**Kitchen Display**:
```
┌─────────────────────────────────────┐
│  [Logo]    Kitchen Orders           │
├─────────────────────────────────────┤
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Order #ORD-1234             │   │
│  │ • Orange Juice              │   │
│  │ • Green Smoothie            │   │
│  │ Time: 10:23 AM              │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Order #ORD-1235             │   │
│  │ • Berry Blast               │   │
│  │ Time: 10:25 AM              │   │
│  └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

### Responsive Breakpoints

- **Mobile**: < 768px (single column, stacked layout)
- **Tablet**: 768px - 1024px (2-column grid)
- **Desktop**: > 1024px (4-column grid)

### Animation and Feedback

- Smooth transitions on hover (200ms ease)
- Button press feedback with scale transform
- New order pulse animation on kitchen display
- Loading spinner during order submission
- Success checkmark animation on confirmation

## Implementation Notes

### Order ID Generation

Use a combination of timestamp and random string for uniqueness:
```javascript
function generateOrderId() {
  const timestamp = Date.now();
  const random = Math.random().toString(36).substring(2, 6).toUpperCase();
  return `ORD-${timestamp}-${random}`;
}
```

### SSE Implementation

**Server**:
```javascript
app.get('/api/orders/stream', (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  
  // Add client to list
  sseClients.push(res);
  
  // Remove on disconnect
  req.on('close', () => {
    sseClients = sseClients.filter(client => client !== res);
  });
});

function broadcastOrder(order) {
  const data = `data: ${JSON.stringify(order)}\n\n`;
  sseClients.forEach(client => client.write(data));
}
```

**Client**:
```javascript
const eventSource = new EventSource('/api/orders/stream');

eventSource.onmessage = (event) => {
  const order = JSON.parse(event.data);
  displayOrder(order);
};

eventSource.onerror = () => {
  showConnectionError();
  // Attempt reconnection
  setTimeout(() => {
    eventSource.close();
    connectToOrderStream();
  }, 5000);
};
```

### Menu Data Structure

Store menu items in a JavaScript file or JSON:
```javascript
const menuItems = [
  {
    id: 'juice-001',
    name: 'Fresh Orange Juice',
    description: 'Freshly squeezed oranges',
    price: 5.99,
    imageUrl: '/images/orange-juice.jpg',
    category: 'Citrus'
  },
  // ... more items
];
```

### Performance Considerations

- Limit order history to prevent memory bloat (e.g., keep last 100 orders)
- Implement pagination on kitchen display for many orders
- Optimize images (WebP format, lazy loading)
- Minimize JavaScript bundle size
- Use CSS animations over JavaScript for better performance
