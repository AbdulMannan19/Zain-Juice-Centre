"""
End-to-End Manual Testing Script
Tests the complete order flow for the Juice Cafe Ordering System
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_menu_endpoint():
    """Test 1: Verify menu page displays correctly"""
    print("\n=== Test 1: Menu Endpoint ===")
    response = requests.get(f"{BASE_URL}/api/menu")
    assert response.status_code == 200, "Menu endpoint should return 200"
    
    menu_items = response.json()
    assert len(menu_items) >= 8, "Should have at least 8 menu items"
    
    # Verify menu item structure
    for item in menu_items:
        assert 'id' in item, "Menu item should have id"
        assert 'name' in item, "Menu item should have name"
        assert 'description' in item, "Menu item should have description"
        assert 'price' in item, "Menu item should have price"
        assert 'imageUrl' in item, "Menu item should have imageUrl"
        assert 'category' in item, "Menu item should have category"
    
    print(f"✓ Menu endpoint works correctly with {len(menu_items)} items")
    return menu_items

def test_place_order(menu_items):
    """Test 2: Place test orders and verify they appear"""
    print("\n=== Test 2: Place Orders ===")
    
    # Test Order 1: Single item
    order1_data = {
        "items": [
            {
                "menuItemId": menu_items[0]['id'],
                "name": menu_items[0]['name'],
                "quantity": 1
            }
        ]
    }
    
    response1 = requests.post(
        f"{BASE_URL}/api/orders",
        json=order1_data,
        headers={"Content-Type": "application/json"}
    )
    
    assert response1.status_code == 201, "Order should be created successfully"
    result1 = response1.json()
    assert 'orderId' in result1, "Response should contain orderId"
    assert result1['orderId'].startswith('ORD-'), "Order ID should have correct format"
    
    print(f"✓ Order 1 placed successfully: {result1['orderId']}")
    
    # Test Order 2: Multiple items
    order2_data = {
        "items": [
            {
                "menuItemId": menu_items[1]['id'],
                "name": menu_items[1]['name'],
                "quantity": 2
            },
            {
                "menuItemId": menu_items[2]['id'],
                "name": menu_items[2]['name'],
                "quantity": 1
            }
        ]
    }
    
    response2 = requests.post(
        f"{BASE_URL}/api/orders",
        json=order2_data,
        headers={"Content-Type": "application/json"}
    )
    
    assert response2.status_code == 201, "Order should be created successfully"
    result2 = response2.json()
    assert 'orderId' in result2, "Response should contain orderId"
    
    print(f"✓ Order 2 placed successfully: {result2['orderId']}")
    
    return [result1['orderId'], result2['orderId']]

def test_error_handling():
    """Test 3: Test error handling with invalid orders"""
    print("\n=== Test 3: Error Handling ===")
    
    # Test empty order
    response = requests.post(
        f"{BASE_URL}/api/orders",
        json={"items": []},
        headers={"Content-Type": "application/json"}
    )
    
    assert response.status_code == 400, "Empty order should return 400"
    error_data = response.json()
    assert 'error' in error_data, "Error response should contain error message"
    
    print(f"✓ Empty order rejected correctly: {error_data['error']}")
    
    # Test missing items field
    response2 = requests.post(
        f"{BASE_URL}/api/orders",
        json={},
        headers={"Content-Type": "application/json"}
    )
    
    assert response2.status_code == 400, "Missing items should return 400"
    
    print("✓ Invalid order data rejected correctly")

def test_pages_accessible():
    """Test 4: Verify both pages are accessible"""
    print("\n=== Test 4: Page Accessibility ===")
    
    # Test menu page
    response1 = requests.get(f"{BASE_URL}/")
    assert response1.status_code == 200, "Menu page should be accessible"
    assert 'Juice Cafe' in response1.text, "Menu page should contain title"
    
    print("✓ Menu page accessible")
    
    # Test kitchen display
    response2 = requests.get(f"{BASE_URL}/kitchen")
    assert response2.status_code == 200, "Kitchen display should be accessible"
    assert 'Kitchen Orders' in response2.text, "Kitchen page should contain title"
    
    print("✓ Kitchen display accessible")
    
    # Test static assets
    response3 = requests.get(f"{BASE_URL}/styles.css")
    assert response3.status_code == 200, "CSS should be accessible"
    
    response4 = requests.get(f"{BASE_URL}/menu.js")
    assert response4.status_code == 200, "Menu JS should be accessible"
    
    response5 = requests.get(f"{BASE_URL}/kitchen.js")
    assert response5.status_code == 200, "Kitchen JS should be accessible"
    
    response6 = requests.get(f"{BASE_URL}/assets/logo.svg")
    assert response6.status_code == 200, "Logo should be accessible"
    
    print("✓ All static assets accessible")

def test_responsive_design():
    """Test 5: Verify responsive design CSS is present"""
    print("\n=== Test 5: Responsive Design ===")
    
    response = requests.get(f"{BASE_URL}/styles.css")
    css_content = response.text
    
    # Check for media queries
    assert '@media' in css_content, "CSS should contain media queries"
    assert 'min-width: 768px' in css_content, "Should have tablet breakpoint"
    assert 'min-width: 1024px' in css_content, "Should have desktop breakpoint"
    assert 'max-width: 767px' in css_content, "Should have mobile breakpoint"
    
    print("✓ Responsive design breakpoints present")
    print("  - Mobile: < 768px")
    print("  - Tablet: 768px - 1024px")
    print("  - Desktop: > 1024px")

def run_all_tests():
    """Run all end-to-end tests"""
    print("=" * 60)
    print("JUICE CAFE ORDERING SYSTEM - END-TO-END TESTS")
    print("=" * 60)
    
    try:
        # Test 1: Menu endpoint
        menu_items = test_menu_endpoint()
        
        # Test 2: Place orders
        order_ids = test_place_order(menu_items)
        
        # Test 3: Error handling
        test_error_handling()
        
        # Test 4: Pages accessible
        test_pages_accessible()
        
        # Test 5: Responsive design
        test_responsive_design()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        print("\nSummary:")
        print(f"- Menu items loaded: {len(menu_items)}")
        print(f"- Test orders placed: {len(order_ids)}")
        print(f"- Order IDs: {', '.join(order_ids)}")
        print("\nManual verification needed:")
        print("1. Open http://localhost:5000/ in browser")
        print("2. Verify menu displays with images and styling")
        print("3. Add items to order and place order")
        print("4. Open http://localhost:5000/kitchen in another tab")
        print("5. Verify orders appear in real-time on kitchen display")
        print("6. Test responsive design by resizing browser window")
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        return False
    
    return True

if __name__ == "__main__":
    run_all_tests()
