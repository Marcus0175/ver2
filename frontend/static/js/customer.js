document.addEventListener('DOMContentLoaded', async function() {
    // Verify auth
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '../index.html';
        return;
    }
    
    try {
        const currentUser = await api.getCurrentUser();
        if (currentUser.role !== 'customer') {
            logout();
            return;
        }
    } catch (error) {
        console.error('Auth error:', error);
        logout();
        return;
    }
    
    // Initialize order page if we're on it
    if (window.location.pathname.includes('/customer/order.html')) {
        initOrderPage();
    }
    
    // Initialize order history page if we're on it
    if (window.location.pathname.includes('/customer/order-history.html')) {
        loadOrderHistory();
    }
});

// Initialize order page with map and restaurant selection
async function initOrderPage() {
    // Load restaurants
    try {
        const branches = await api.getBranches();
        const branchSelect = document.getElementById('branch-select');
        
        branches.forEach(branch => {
            const option = document.createElement('option');
            option.value = branch.id;
            option.textContent = branch.name;
            option.dataset.lat = branch.latitude;
            option.dataset.lng = branch.longitude;
            branchSelect.appendChild(option);
        });
        
        // Hide menu until restaurant is selected
        document.getElementById('menu-container').style.display = 'none';
        
        // Restaurant selection change
        branchSelect.addEventListener('change', async function() {
            if (this.value) {
                await loadMenuItems(this.value);
                document.getElementById('menu-container').style.display = 'flex';
                
                // Set restaurant location on map
                const selectedOption = this.options[this.selectedIndex];
                updateMap(selectedOption.dataset.lat, selectedOption.dataset.lng);
            }
        });
    } catch (error) {
        console.error('Error loading restaurants:', error);
    }
    
    // Initialize map
    initMap();
    
    // Initialize checkout button
    document.getElementById('checkout-btn').addEventListener('click', showCheckoutModal);
    
    // Initialize payment button
    document.getElementById('pay-btn').addEventListener('click', processPayment);
}

// Initialize map
function initMap() {
    // Default to a location in Ho Chi Minh City
    const map = L.map('map').setView([10.7769, 106.7009], 13);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    
    let marker;
    
    map.on('click', function(e) {
        const { lat, lng } = e.latlng;
        document.getElementById('latitude').value = lat;
        document.getElementById('longitude').value = lng;
        
        if (marker) {
            marker.setLatLng(e.latlng);
        } else {
            marker = L.marker(e.latlng).addTo(map);
        }
    });
    
    window.orderMap = map;
    window.orderMarker = marker;
}

// Update map with restaurant location
function updateMap(lat, lng) {
    const map = window.orderMap;
    map.setView([lat, lng], 13);
    
    // Add restaurant marker
    const restaurantIcon = L.icon({
        iconUrl: '../static/img/restaurant.png',
        iconSize: [32, 32],
        iconAnchor: [16, 32]
    });
    
    L.marker([lat, lng], { icon: restaurantIcon }).addTo(map);
}

// Load menu items for a restaurant
async function loadMenuItems(branchId) {
    try {
        const menuItems = await api.getMenuItems(branchId);
        const menuContainer = document.getElementById('menu-items');
        menuContainer.innerHTML = '';
        
        menuItems.forEach(item => {
            const menuItem = document.createElement('div');
            menuItem.className = 'col-md-6 mb-3';
            menuItem.innerHTML = `
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">${item.name}</h5>
                        <p class="card-text">${item.description || 'No description'}</p>
                        <p class="card-text">$${parseFloat(item.price).toFixed(2)}</p>
                        <button class="btn btn-sm btn-outline-primary add-to-cart" 
                            data-id="${item.id}" 
                            data-name="${item.name}" 
                            data-price="${item.price}">
                            Add to Cart
                        </button>
                    </div>
                </div>
            `;
            menuContainer.appendChild(menuItem);
        });
        
        // Add event listeners to "Add to Cart" buttons
        document.querySelectorAll('.add-to-cart').forEach(button => {
            button.addEventListener('click', addToCart);
        });
        
    } catch (error) {
        console.error('Error loading menu items:', error);
    }
}

// Cart management
let cart = [];

// Add item to cart
function addToCart(e) {
    const button = e.target;
    const id = button.dataset.id;
    const name = button.dataset.name;
    const price = parseFloat(button.dataset.price);
    
    // Check if item is already in cart
    const existingItem = cart.find(item => item.id === id);
    
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({
            id,
            name,
            price,
            quantity: 1
        });
    }
    
    updateCartDisplay();
}

// Update cart display
function updateCartDisplay() {
    const orderItems = document.getElementById('order-items');
    orderItems.innerHTML = '';
    
    let total = 0;
    
    cart.forEach(item => {
        const itemTotal = item.price * item.quantity;
        total += itemTotal;
        
        const li = document.createElement('li');
        li.className = 'list-group-item d-flex justify-content-between';
        li.innerHTML = `
            <div>
                <h6 class="my-0">${item.name}</h6>
                <small class="text-muted">$${item.price.toFixed(2)} x ${item.quantity}</small>
            </div>
            <span class="text-muted">$${itemTotal.toFixed(2)}</span>
            <button class="btn btn-sm btn-danger remove-item" data-id="${item.id}">&times;</button>
        `;
        orderItems.appendChild(li);
    });
    
    // Update total
    document.getElementById('total-amount').textContent = `$${total.toFixed(2)}`;
    
    // Add event listeners for remove buttons
    document.querySelectorAll('.remove-item').forEach(button => {
        button.addEventListener('click', removeFromCart);
    });
}

// Remove item from cart
function removeFromCart(e) {
    const id = e.target.dataset.id;
    cart = cart.filter(item => item.id !== id);
    updateCartDisplay();
}

// Show checkout modal
function showCheckoutModal() {
    // Validate that we have items in cart
    if (cart.length === 0) {
        alert('Please add items to your cart first');
        return;
    }
    
    // Validate delivery location is set
    const lat = document.getElementById('latitude').value;
    const lng = document.getElementById('longitude').value;
    
    if (!lat || !lng) {
        alert('Please select a delivery location on the map');
        return;
    }
    
    // Update summary in modal
    const summaryItems = document.getElementById('summary-items');
    summaryItems.innerHTML = '';
    
    let total = 0;
    
    cart.forEach(item => {
        const itemTotal = item.price * item.quantity;
        total += itemTotal;
        
        const li = document.createElement('li');
        li.className = 'list-group-item d-flex justify-content-between';
        li.innerHTML = `
            <div>
                <h6 class="my-0">${item.name}</h6>
                <small class="text-muted">$${item.price.toFixed(2)} x ${item.quantity}</small>
            </div>
            <span class="text-muted">$${itemTotal.toFixed(2)}</span>
        `;
        summaryItems.appendChild(li);
    });
    
    document.getElementById('modal-total').textContent = `$${total.toFixed(2)}`;
    
    // Show modal
    const paymentModal = new bootstrap.Modal(document.getElementById('paymentModal'));
    paymentModal.show();
}

// Process payment and create order
async function processPayment() {
    try {
        const branchId = document.getElementById('branch-select').value;
        const lat = document.getElementById('latitude').value;
        const lng = document.getElementById('longitude').value;
        const paymentMethod = document.getElementById('payment-method').value;
        
        // Create order items array for API
        const items = cart.map(item => ({
            menu_item_id: item.id,
            quanity: item.quantity
        }));
        
        // Create order
        const orderData = {
            branch_id: parseInt(branchId),
            items: items,
            dropoff_lat: parseFloat(lat),
            dropoff_lon: parseFloat(lng)
        };
        
        const order = await api.createOrder(orderData);
        
        // Process payment (in a real app, you'd redirect to a payment gateway)
        // For this demo, we'll simulate the payment with the checkout endpoint
        // This assumes the create order API returns payment info or you'd need to fetch it
        const payment = await api.checkout(order.payment_id, paymentMethod);
        
        // Hide modal
        const paymentModal = bootstrap.Modal.getInstance(document.getElementById('paymentModal'));
        paymentModal.hide();
        
        // Show success message
        alert('Order placed successfully! Your food is being prepared.');
        
        // Reset cart
        cart = [];
        updateCartDisplay();
        
        // Redirect to order history
        window.location.href = 'order-history.html';
        
    } catch (error) {
        console.error('Payment error:', error);
        alert('Payment failed. Please try again.');
    }
}

// Load order history
async function loadOrderHistory() {
    try {
        const orders = await api.getMyOrders();
        const orderHistoryContainer = document.getElementById('order-history');
        
        if (orders.length === 0) {
            orderHistoryContainer.innerHTML = '<div class="alert alert-info">You have no orders yet.</div>';
            return;
        }
        
        orders.forEach(order => {
            const orderCard = document.createElement('div');
            orderCard.className = 'card mb-3';
            
            let itemsHtml = '';
            order.order_items.forEach(item => {
                itemsHtml += `
                    <li class="list-group-item d-flex justify-content-between">
                        <div>
                            <h6 class="my-0">${item.menu_item_id}</h6> <!-- In a real app, fetch the actual menu item name -->
                            <small class="text-muted">$${parseFloat(item.price).toFixed(2)} x ${item.quantity}</small>
                        </div>
                        <span class="text-muted">$${(parseFloat(item.price) * item.quantity).toFixed(2)}</span>
                    </li>
                `;
            });
            
            let statusBadgeClass = 'bg-secondary';
            switch (order.status) {
                case 'pending':
                    statusBadgeClass = 'bg-warning';
                    break;
                case 'preparing':
                    statusBadgeClass = 'bg-info';
                    break;
                case 'ready_for_delivery':
                    statusBadgeClass = 'bg-primary';
                    break;
                case 'delivered':
                    statusBadgeClass = 'bg-success';
                    break;
                case 'canceled':
                    statusBadgeClass = 'bg-danger';
                    break;
            }
            
            orderCard.innerHTML = `
                <div class="card-header d-flex justify-content-between align-items-center">
                    <div>
                        <h5>Order #${order.id}</h5>
                        <small class="text-muted">${new Date(order.created_at).toLocaleString()}</small>
                    </div>
                    <span class="badge ${statusBadgeClass}">${order.status.replace('_', ' ').toUpperCase()}</span>
                </div>
                <div class="card-body">
                    <p class="card-text">Restaurant: ${order.branch_name}</p>
                    <h6>Items:</h6>
                    <ul class="list-group mb-3">
                        ${itemsHtml}
                    </ul>
                    <div class="d-flex justify-content-between">
                        <h5>Total:</h5>
                        <h5>$${parseFloat(order.total_amount).toFixed(2)}</h5>
                    </div>
                </div>
            `;
            
            orderHistoryContainer.appendChild(orderCard);
        });
    } catch (error) {
        console.error('Error loading order history:', error);
        document.getElementById('order-history').innerHTML = '<div class="alert alert-danger">Failed to load order history.</div>';
    }
}