document.addEventListener('DOMContentLoaded', function() {
    // Connect to WebSocket if user is logged in
    const token = localStorage.getItem('access_token');
    const userId = localStorage.getItem('user_id');
    
    if (token && userId) {
        connectWebSocket(userId);
    }
});

// Connect to WebSocket
function connectWebSocket(userId) {
    // Get hostname from current URL
    const host = window.location.hostname;
    const port = '8000'; // Your backend port
    
    const socket = new WebSocket(`ws://${host}:${port}/ws/${userId}`);
    
    socket.onopen = function(e) {
        console.log('WebSocket connection established');
    };
    
    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
    };
    
    socket.onclose = function(event) {
        if (event.wasClean) {
            console.log(`WebSocket connection closed cleanly, code=${event.code}, reason=${event.reason}`);
        } else {
            console.log('WebSocket connection died');
            // Try to reconnect after a delay
            setTimeout(() => connectWebSocket(userId), 5000);
        }
    };
    
    socket.onerror = function(error) {
        console.error(`WebSocket error: ${error.message}`);
    };
    
    // Store socket in window for global access
    window.socket = socket;
}

// Handle incoming WebSocket messages
function handleWebSocketMessage(data) {
    console.log('Received WebSocket message:', data);
    
    const userRole = localStorage.getItem('user_role');
    
    switch (data.event) {
        case 'delivery_request_active':
            // For drivers, update the available deliveries
            if (userRole === 'driver') {
                if (typeof loadAvailableDeliveries === 'function') {
                    loadAvailableDeliveries();
                }
                
                // Show notification
                showNotification('New Delivery Request', 'A new delivery request is available.');
            }
            break;
        
        case 'delivery_request_assigned':
            // For drivers, update current delivery
            if (userRole === 'driver') {
                if (typeof loadCurrentDelivery === 'function') {
                    loadCurrentDelivery();
                }
                
                // Show notification
                showNotification('Delivery Assigned', 'You have been assigned a new delivery.');
            }
            break;
        
        case 'order_item_assigned':
            // For kitchen staff, update orders that need to be prepared
            if (userRole === 'kitchen_staff') {
                if (typeof loadAssignedOrders === 'function') {
                    loadAssignedOrders();
                }
                
                // Show notification
                showNotification('New Order Item', 'You have been assigned a new order item to prepare.');
            }
            break;
        
        case 'delivery_request_delivered':
            // For customers, update order status
            if (userRole === 'customer') {
                // Show notification
                showNotification('Order Delivered', 'Your order has been delivered! Please confirm receipt.');
                
                // Reload order history if on that page
                if (window.location.pathname.includes('/customer/order-history.html')) {
                    loadOrderHistory();
                }
            }
            break;
    }
}

// Show browser notification
function showNotification(title, body) {
    // Check if the browser supports notifications
    if (!("Notification" in window)) {
        console.log("This browser does not support desktop notification");
        return;
    }
    
    // Check if permission is already granted
    if (Notification.permission === "granted") {
        const notification = new Notification(title, { body });
    }
    // Otherwise, request permission
    else if (Notification.permission !== "denied") {
        Notification.requestPermission().then(function (permission) {
            if (permission === "granted") {
                const notification = new Notification(title, { body });
            }
        });
    }
}