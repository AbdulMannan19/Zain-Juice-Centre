# Implementation Plan: Juice Cafe Ordering System

## Overview

This implementation plan breaks down the juice cafe ordering system into incremental coding tasks. The system will use Python (Flask/FastAPI) for the backend with Server-Sent Events for real-time updates, and vanilla JavaScript for the frontend. Each task builds on previous work to create a complete, functional ordering system.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create project directory structure (backend, frontend, static assets)
  - Set up Python virtual environment
  - Install Flask, flask-cors for backend
  - Create requirements.txt
  - Set up basic HTML/CSS/JS file structure
  - _Requirements: All_

- [x] 2. Create menu data and API endpoint
  - [x] 2.1 Define menu items data structure in Python
    - Create menu_data.py with list of juice items (id, name, description, price, imageUrl, category)
    - Include at least 8-10 diverse juice items
    - _Requirements: 1.1_
  
  - [x] 2.2 Implement GET /api/menu endpoint
    - Create Flask route to serve menu items as JSON
    - _Requirements: 1.1_
  
  - [ ]* 2.3 Write unit tests for menu endpoint
    - Test endpoint returns correct JSON structure
    - Test all menu items are included
    - _Requirements: 1.1_

- [x] 3. Implement in-memory order storage
  - [x] 3.1 Create order storage module
    - Implement in-memory list to store orders
    - Create Order and OrderItem data classes
    - Implement generateOrderId() function using timestamp and random string
    - _Requirements: 4.1, 5.1_
  
  - [ ]* 3.2 Write property test for Order ID uniqueness
    - **Property 2: Order ID Uniqueness**
    - **Validates: Requirements 2.2, 5.1**
  
  - [ ]* 3.3 Write unit test for in-memory storage
    - Test orders are stored and retrievable
    - Test empty order list on initialization
    - _Requirements: 4.1, 4.4_

- [x] 4. Implement order submission endpoint
  - [x] 4.1 Create POST /api/orders endpoint
    - Accept order data (list of items) as JSON
    - Validate order contains at least one item
    - Generate Order_ID and create order object
    - Store order in memory
    - Return Order_ID in response
    - _Requirements: 2.2, 2.4, 4.1_
  
  - [ ]* 4.2 Write property test for in-memory storage persistence
    - **Property 7: In-Memory Storage Persistence**
    - **Validates: Requirements 4.1**
  
  - [ ]* 4.3 Write unit tests for order submission
    - Test successful order creation returns Order_ID
    - Test empty order returns 400 error
    - Test invalid data returns 400 error
    - _Requirements: 2.2, 2.4_

- [x] 5. Implement Server-Sent Events for real-time updates
  - [x] 5.1 Create GET /api/orders/stream SSE endpoint
    - Set up SSE headers (Content-Type: text/event-stream)
    - Maintain list of connected SSE clients
    - Handle client disconnections
    - Implement broadcast function to send orders to all clients
    - _Requirements: 3.1, 3.4_
  
  - [x] 5.2 Integrate SSE broadcast with order submission
    - Call broadcast function when new order is created
    - Send order data as JSON in SSE format
    - _Requirements: 3.1, 3.4_
  
  - [ ]* 5.3 Write property test for real-time updates
    - **Property 4: Real-Time Order Updates**
    - **Validates: Requirements 3.1, 3.4**

- [x] 6. Build menu page frontend
  - [x] 6.1 Create HTML structure for menu page
    - Create index.html with header, menu grid, and order summary sections
    - Add logo placeholder in header
    - Create order confirmation modal structure
    - _Requirements: 1.1, 2.5, 7.1_
  
  - [x] 6.2 Implement CSS styling for menu page
    - Apply modern juice-themed color palette (oranges, greens, yellows)
    - Style menu grid with CSS Grid (responsive: 1/2/4 columns)
    - Style juice item cards with images, names, descriptions, prices
    - Add hover effects and animations
    - Implement responsive design with media queries
    - Style order summary section
    - Style confirmation modal
    - _Requirements: 1.2, 1.3, 6.1, 7.2, 7.3, 7.4_
  
  - [x] 6.3 Implement menu page JavaScript functionality
    - Fetch menu items from /api/menu on page load
    - Render menu items dynamically
    - Implement add-to-order functionality
    - Update order summary display when items added
    - Implement order submission via POST /api/orders
    - Show confirmation modal with Order_ID on success
    - Handle errors and show user-friendly messages
    - _Requirements: 1.1, 2.1, 2.4, 2.5_
  
  - [ ]* 6.4 Write property test for menu item selection
    - **Property 1: Menu Item Selection Adds to Order**
    - **Validates: Requirements 2.1**
  
  - [ ]* 6.5 Write property test for order display synchronization
    - **Property 3: Current Order Display Synchronization**
    - **Validates: Requirements 2.5**

- [x] 7. Build kitchen display frontend
  - [x] 7.1 Create HTML structure for kitchen display
    - Create kitchen.html with header and order list container
    - Add logo in header
    - Add connection status indicator
    - _Requirements: 3.2, 7.1_
  
  - [x] 7.2 Implement CSS styling for kitchen display
    - Apply consistent juice-themed styling
    - Style order cards with Order_ID and items list
    - Add new order animation/highlight
    - Style connection status indicator
    - _Requirements: 3.2, 7.2, 7.4_
  
  - [x] 7.3 Implement kitchen display JavaScript functionality
    - Establish SSE connection to /api/orders/stream
    - Listen for new order events
    - Render order cards dynamically when orders arrive
    - Display Order_ID and all items for each order
    - Sort orders chronologically (oldest first)
    - Auto-scroll to newest orders
    - Handle connection errors and show status
    - Implement reconnection logic
    - _Requirements: 3.1, 3.2, 3.3, 3.4_
  
  - [ ]* 7.4 Write property test for kitchen display order information
    - **Property 5: Kitchen Display Shows Complete Order Information**
    - **Validates: Requirements 3.2**
  
  - [ ]* 7.5 Write property test for chronological ordering
    - **Property 6: Chronological Order Display**
    - **Validates: Requirements 3.3**

- [x] 8. Implement data consistency validation
  - [x]* 8.1 Write property test for data consistency across pages
    - **Property 8: Data Consistency Across Pages**
    - **Validates: Requirements 4.2, 4.3**
  
  - [x]* 8.2 Write property test for multiple items sharing Order ID
    - **Property 9: Multiple Items Share Order ID**
    - **Validates: Requirements 5.3**
  
  - [x]* 8.3 Write property test for Order ID display in both locations
    - **Property 10: Order ID Displayed in Both Locations**
    - **Validates: Requirements 5.2**

- [x] 9. Add logo and visual assets
  - [x] 9.1 Integrate cafe logo into both pages
    - Add logo image file to static assets
    - Update HTML to reference logo
    - Ensure logo displays prominently
    - _Requirements: 7.1_
  
  - [x] 9.2 Add placeholder juice images
    - Create or source juice images for menu items
    - Optimize images for web (WebP format if possible)
    - Update menu_data.py with correct image paths
    - _Requirements: 1.1, 7.3_

- [x] 10. Checkpoint - Test end-to-end functionality
  - Run the application and test complete order flow
  - Verify menu page displays correctly
  - Place test orders and verify they appear on kitchen display
  - Test real-time updates with multiple orders
  - Test responsive design on different screen sizes
  - Ensure all tests pass
  - Ask the user if questions arise

- [ ] 11. Add error handling and edge cases
  - [ ] 11.1 Implement client-side error handling
    - Add try-catch blocks for API calls
    - Show user-friendly error messages
    - Implement retry logic for failed submissions
    - Add loading states during API calls
    - _Requirements: 2.4_
  
  - [ ] 11.2 Implement server-side validation
    - Validate order structure and data types
    - Return appropriate HTTP status codes
    - Add error logging
    - _Requirements: 2.2, 4.1_
  
  - [ ]* 11.3 Write unit tests for error cases
    - Test network failure handling
    - Test invalid input validation
    - Test SSE reconnection logic
    - _Requirements: 2.4, 4.1_

- [ ] 12. Final polish and optimization
  - [ ] 12.1 Optimize performance
    - Implement order history limit (keep last 100 orders)
    - Add lazy loading for images
    - Minify CSS/JS if needed
    - _Requirements: 4.1_
  
  - [ ] 12.2 Final visual refinements
    - Fine-tune colors and spacing
    - Add smooth transitions and animations
    - Ensure consistent styling across pages
    - Test on multiple browsers
    - _Requirements: 7.2, 7.3, 7.4, 7.5_

- [ ] 13. Final checkpoint - Complete testing
  - Run all unit tests and property tests
  - Perform manual testing of all features
  - Test with multiple concurrent users
  - Verify responsive design works correctly
  - Ensure all requirements are met
  - Ask the user if questions arise

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties using a Python property testing library (e.g., Hypothesis)
- Unit tests validate specific examples and edge cases using pytest
- The implementation uses Python/Flask for backend and vanilla JavaScript for frontend
- Server-Sent Events (SSE) provide real-time updates from server to kitchen display
- All data is stored in-memory and will be lost on application restart
