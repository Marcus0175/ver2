document.addEventListener('DOMContentLoaded', async function() {
    // Verify auth
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '../index.html';
        return;
    }
    
    try {
        const currentUser = await api.getCurrentUser();
        if (currentUser.role !== 'driver') {
            logout();
            return;
        }
    } catch (error) {
        console.error('Auth error:', error);
        logout();
        return;
    }
    
    // Initialize driver dashboard if we're on it
    if (window.location.pathname.includes('/driver/dashboard.html')) {
        initDriverDashboard();
    }
    
    // Initialize deliveries page if we're on it
    if (window.location.pathname.includes('/driver/deliveries.html')) {
        loadMyDeliveries();
    }
});

// Initialize driver dashboard
async function initDriverDashboard() {
    // Load available deliveries
    await loadAvailableDeliveries();
    
    // Load current delivery
    await loadCurrentDelivery();
    
    // Initialize map
    initDeliveryMap();
}

// Load available deliveries
async function loadAvailableDeliveries() {
    const availableDeliveriesContainer = document.getElementById('available-deliveries');
    
    try {
        const deliveries = await api.getNotAcceptedDeliveryRequests();
        
        if (deliveries.length === 0) {
            availableDeliveriesContainer.innerHTML = '<div class="alert alert-info">No delivery requests available at the moment.</div>';
            return;
        }
        
        let deliveriesHtml = '';
        
        deliveries.forEach(delivery => {
            deliveriesHtml += `
                <div class="card mb-2">
                    <div class="card-body">
                        <h5 class="card-title">Order #${delivery.order_id}</h5>
                        <p class="card-text">Distance: ${parseFloat(delivery.distance_km).toFixed(2)} km</p>
                        <p class="card-text">Fee: $${parseFloat(delivery.shipping_fee).toFixed(2)}</p>
                        <button class="btn btn-primary accept-delivery" data-id="${delivery.id}">
                            Accept Delivery
                        </button>
                    </div>
                </div>
            `;
        });
        
        availableDeliveriesContainer.innerHTML = deliveriesHtml;
        
        // Add event listeners to accept buttons
        document.querySelectorAll('.accept-delivery').forEach(button => {
            button.addEventListener('click', async function() {
                const deliveryId = this.dataset.id;
                await acceptDelivery(deliveryId);
            });
        });
        
    } catch (error) {
        console.error('Error loading available deliveries:', error);
        availableDeliveriesContainer.innerHTML = '<div class="alert alert-danger">Failed to load available deliveries.</div>';
    }
}

// Accept a delivery
async function acceptDelivery(deliveryId) {
    try {
        await api.acceptDeliveryRequest(deliveryId);
        
        // Reload available deliveries
        await loadAvailableDeliveries();
        
        // Load current delivery
        await loadCurrentDelivery();
        
    } catch (error) {
        console.error('Error accepting delivery:', error);
        alert('Failed to accept delivery. It may have been accepted by another driver.');
    }
}

// Load current delivery
async function loadCurrentDelivery() {
    const currentDeliveryContainer = document.getElementById('current-delivery');
    
    try {
        const myDeliveries = await api.getMyDeliveryRequests();
        
        // Find active delivery (not delivered)
        const activeDelivery = myDeliveries.find(delivery => 
            delivery.status !== 'delivered'
        );
        
        if (!activeDelivery) {
            currentDeliveryContainer.innerHTML = '<div class="alert alert-info">No active delivery.</div>';
            return;
        }
        
        let statusBadgeClass = 'bg-secondary';
        let actionButton = '';
        
        switch (activeDelivery.status) {
            case 'pending':
                statusBadgeClass = 'bg-warning';
                actionButton = `
                    <button class="btn btn-primary start-delivery" data-id="${activeDelivery.id}">
                        Start Delivery
                    </button>
                `;
                break;
            case 'delivering':
                statusBadgeClass = 'bg-primary';
                actionButton = `
                    <button class="btn btn-success complete-delivery" data-id="${activeDelivery.id}">
                        Mark as Delivered
                    </button>
                `;
                break;
        }
        
        currentDeliveryContainer.innerHTML = `
            <div class="card">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h5>Order #${activeDelivery.order_id}</h5>
                    <span class="badge ${statusBadgeClass}">${activeDelivery.status.toUpperCase()}</span>
                </div>
                <div class="card-body">
                    <p>Distance: ${parseFloat(activeDelivery.distance_km).toFixed(2)} km</p>
                    <p>Fee: $${parseFloat(activeDelivery.shipping_fee).toFixed(2)}</p>
                    ${actionButton}
                </div>
            </div>
        `;
        
        // Add event listeners
        const startButton = document.querySelector('.start-delivery');
        if (startButton) {
            startButton.addEventListener('click', async function() {
                const deliveryId = this.dataset.id;
                await startDelivery(deliveryId);
            });
        }
        
        const completeButton = document.querySelector('.complete-delivery');
        if (completeButton) {
            completeButton.addEventListener('click', async function() {
                const deliveryId = this.dataset.id;
                await completeDelivery(deliveryId);
            });
        }
        
        // Update map with delivery info
        updateDeliveryMap(activeDelivery);
        
    } catch (error) {
        console.error('Error loading current delivery:', error);
        currentDeliveryContainer.innerHTML = '<div class="alert alert-danger">Failed to load current delivery.</div>';
    }
}

// Start delivery (change status to delivering)
async function startDelivery(deliveryId) {
    try {
        await api.deliveringDeliveryRequest(deliveryId);
        await loadCurrentDelivery();
    } catch (error) {
        console.error('Error starting delivery:', error);
        alert('Failed to start delivery.');
    }
}

// Complete delivery (mark as delivered)
async function completeDelivery(deliveryId) {
    try {
        await api.deliveredDeliveryRequest(deliveryId);
        await loadCurrentDelivery();
    } catch (error) {
        console.error('Error completing delivery:', error);
        alert('Failed to complete delivery.');
    }
}

// Initialize delivery map
function initDeliveryMap() {
    // Default to a location in Ho Chi Minh City
    const map = L.map('delivery-map').setView([10.7769, 106.7009], 13);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    
    window.deliveryMap = map;
}

// Update delivery map with delivery info
function updateDeliveryMap(delivery) {
    const map = window.deliveryMap;
    
    // Clear existing markers
    map.eachLayer(layer => {
        if (layer instanceof L.Marker) {
            map.removeLayer(layer);
        }
    });
    
    // Add restaurant marker (this would need branch data - for demo let's use a hardcoded location)
    // In a real app, fetch the branch location
    const restaurantLat = 10.7769;
    const restaurantLng = 106.7009;
    
    const restaurantIcon = L.icon({
        iconUrl: '../static/img/restaurant.png',
        iconSize: [32, 32],
        iconAnchor: [16, 32]
    });
    
    const restaurantMarker = L.marker([restaurantLat, restaurantLng], { icon: restaurantIcon })
        .addTo(map)
        .bindPopup('Restaurant');
        
    // Add delivery location marker
    const deliveryLat = parseFloat(delivery.dropoff_lat);
    const deliveryLng = parseFloat(delivery.dropoff_lon);
    
    const deliveryIcon = L.icon({
        iconUrl: '../static/img/delivery.png',
        iconSize: [32, 32],
        iconAnchor: [16, 32]
    });
    
    const deliveryMarker = L.marker([deliveryLat, deliveryLng], { icon: deliveryIcon })
        .addTo(map)
        .bindPopup('Delivery Location');
        
    // Draw route line (in a real app, you'd use a routing API)
    const routeLine = L.polyline(
        [[restaurantLat, restaurantLng], [deliveryLat, deliveryLng]], 
        { color: 'blue' }
    ).addTo(map);
    
    // Fit map to bounds
    const bounds = L.latLngBounds([
        [restaurantLat, restaurantLng],
        [deliveryLat, deliveryLng]
    ]);
    map.fitBounds(bounds, { padding: [50, 50] });
}