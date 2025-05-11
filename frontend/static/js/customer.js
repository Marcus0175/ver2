// Giỏ hàng
let cart = [];

document.addEventListener('DOMContentLoaded', async function() {
    // Kiểm tra xác thực
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
        
        // Khởi tạo trang order nếu đang ở trang đó
        if (window.location.pathname.includes('/customer/order.html')) {
            initOrderPage();
        }
        
        // Khởi tạo trang lịch sử đơn hàng nếu đang ở trang đó
        if (window.location.pathname.includes('/customer/order-history.html')) {
            loadOrderHistory();
        }
    } catch (error) {
        console.error('Lỗi xác thực:', error);
        logout();
    }
});

// Khởi tạo trang đặt hàng với bản đồ và lựa chọn nhà hàng
async function initOrderPage() {
    // Tải danh sách nhà hàng
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
        
        // Ẩn menu cho đến khi chọn nhà hàng
        document.getElementById('menu-container').style.display = 'none';
        
        // Xử lý thay đổi lựa chọn nhà hàng
        branchSelect.addEventListener('change', async function() {
            if (this.value) {
                await loadMenuItems(this.value);
                document.getElementById('menu-container').style.display = 'flex';
                
                // Đặt vị trí nhà hàng trên bản đồ
                const selectedOption = this.options[this.selectedIndex];
                updateMap(selectedOption.dataset.lat, selectedOption.dataset.lng);
            }
        });
    } catch (error) {
        console.error('Lỗi khi tải danh sách nhà hàng:', error);
    }
    
    // Khởi tạo bản đồ
    initMap();
    
    // Khởi tạo nút thanh toán
    document.getElementById('checkout-btn').addEventListener('click', showCheckoutModal);
    
    // Khởi tạo nút thanh toán trong modal
    document.getElementById('pay-btn').addEventListener('click', processPayment);
}

// Khởi tạo bản đồ
function initMap() {
    // Mặc định đến một vị trí ở Hồ Chí Minh
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

// Cập nhật bản đồ với vị trí nhà hàng
function updateMap(lat, lng) {
    const map = window.orderMap;
    map.setView([lat, lng], 13);
    
    // Thêm marker của nhà hàng
    const restaurantIcon = L.icon({
        iconUrl: '../static/img/restaurant.png',
        iconSize: [32, 32],
        iconAnchor: [16, 32]
    });
    
    L.marker([lat, lng], { icon: restaurantIcon }).addTo(map);
}

// Tải các món ăn của một nhà hàng
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
                        <p class="card-text">${item.description || 'Không có mô tả'}</p>
                        <p class="card-text">$${parseFloat(item.price).toFixed(2)}</p>
                        <button class="btn btn-sm btn-outline-primary add-to-cart" 
                            data-id="${item.id}" 
                            data-name="${item.name}" 
                            data-price="${item.price}">
                            Thêm vào giỏ hàng
                        </button>
                    </div>
                </div>
            `;
            menuContainer.appendChild(menuItem);
        });
        
        // Thêm event listeners cho các nút "Thêm vào giỏ hàng"
        document.querySelectorAll('.add-to-cart').forEach(button => {
            button.addEventListener('click', addToCart);
        });
        
    } catch (error) {
        console.error('Lỗi khi tải menu:', error);
    }
}

// Thêm món vào giỏ hàng
function addToCart(e) {
    const button = e.target;
    const id = button.dataset.id;
    const name = button.dataset.name;
    const price = parseFloat(button.dataset.price);
    
    // Kiểm tra xem món đã có trong giỏ hàng chưa
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

// Cập nhật hiển thị giỏ hàng
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
    
    // Cập nhật tổng tiền
    document.getElementById('total-amount').textContent = `$${total.toFixed(2)}`;
    
    // Thêm event listeners cho các nút xóa
    document.querySelectorAll('.remove-item').forEach(button => {
        button.addEventListener('click', removeFromCart);
    });
}

// Xóa món khỏi giỏ hàng
function removeFromCart(e) {
    const id = e.target.dataset.id;
    cart = cart.filter(item => item.id !== id);
    updateCartDisplay();
}

// Hiển thị modal thanh toán
function showCheckoutModal() {
    // Kiểm tra có món trong giỏ hàng không
    if (cart.length === 0) {
        alert('Vui lòng thêm món vào giỏ hàng trước');
        return;
    }
    
    // Kiểm tra đã chọn địa điểm giao hàng chưa
    const lat = document.getElementById('latitude').value;
    const lng = document.getElementById('longitude').value;
    
    if (!lat || !lng) {
        alert('Vui lòng chọn địa điểm giao hàng trên bản đồ');
        return;
    }
    
    // Cập nhật thông tin tóm tắt trong modal
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
    
    // Hiển thị modal
    const paymentModal = new bootstrap.Modal(document.getElementById('paymentModal'));
    paymentModal.show();
}

// Xử lý thanh toán và tạo đơn hàng
async function processPayment() {
    try {
        const branchId = document.getElementById('branch-select').value;
        const lat = document.getElementById('latitude').value;
        const lng = document.getElementById('longitude').value;
        const paymentMethod = document.getElementById('payment-method').value;
       
       // Tạo mảng món ăn cho API
       const items = cart.map(item => ({
           menu_item_id: item.id,
           quanity: item.quantity
       }));
       
       // Tạo đơn hàng
       const orderData = {
           branch_id: parseInt(branchId),
           items: items,
           dropoff_lat: parseFloat(lat),
           dropoff_lon: parseFloat(lng)
       };
       
       // Gọi API tạo đơn hàng
       const order = await api.createOrder(orderData);
       
       // Lấy ID thanh toán từ đơn hàng (giả định API trả về thông tin này)
       // Trong ứng dụng thực tế, bạn có thể cần gọi API riêng để lấy ID thanh toán
       const paymentId = order.id; // Hoặc có thể là order.payment_id tùy vào API của bạn
       
       // Xử lý thanh toán
       await api.checkout(paymentId, paymentMethod);
       
       // Ẩn modal
       const paymentModal = bootstrap.Modal.getInstance(document.getElementById('paymentModal'));
       paymentModal.hide();
       
       // Hiển thị thông báo thành công
       alert('Đặt hàng thành công! Món ăn của bạn đang được chuẩn bị.');
       
       // Đặt lại giỏ hàng
       cart = [];
       updateCartDisplay();
       
       // Chuyển hướng đến trang lịch sử đơn hàng
       window.location.href = 'order-history.html';
       
   } catch (error) {
       console.error('Lỗi thanh toán:', error);
       alert('Thanh toán thất bại. Vui lòng thử lại.');
   }
}

// Tải lịch sử đơn hàng
async function loadOrderHistory() {
   try {
       const orders = await api.getMyOrders();
       const orderHistoryContainer = document.getElementById('order-history');
       
       if (orders.length === 0) {
           orderHistoryContainer.innerHTML = '<div class="alert alert-info">Bạn chưa có đơn hàng nào.</div>';
           return;
       }
       
       // Sắp xếp đơn hàng theo thời gian mới nhất
       orders.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
       
       // Hiển thị từng đơn hàng
       orders.forEach(order => {
           const orderCard = document.createElement('div');
           orderCard.className = 'card mb-3';
           
           // Tạo HTML cho từng món trong đơn
           let itemsHtml = '';
           let totalItems = 0;
           
           order.order_items.forEach(item => {
               totalItems += item.quantity;
               itemsHtml += `
                   <li class="list-group-item d-flex justify-content-between">
                       <div>
                           <h6 class="my-0">Món #${item.menu_item_id}</h6>
                           <small class="text-muted">$${parseFloat(item.price).toFixed(2)} x ${item.quantity}</small>
                       </div>
                       <span class="text-muted">$${(parseFloat(item.price) * item.quantity).toFixed(2)}</span>
                   </li>
               `;
           });
           
           // Xác định màu badge dựa trên trạng thái
           let statusBadgeClass = 'bg-secondary';
           let statusText = '';
           
           switch (order.status) {
               case 'pending':
                   statusBadgeClass = 'bg-warning';
                   statusText = 'ĐANG CHỜ';
                   break;
               case 'preparing':
                   statusBadgeClass = 'bg-info';
                   statusText = 'ĐANG CHUẨN BỊ';
                   break;
               case 'ready_for_delivery':
                   statusBadgeClass = 'bg-primary';
                   statusText = 'SẴN SÀNG GIAO HÀNG';
                   break;
               case 'delivered':
                   statusBadgeClass = 'bg-success';
                   statusText = 'ĐÃ GIAO';
                   break;
               case 'canceled':
                   statusBadgeClass = 'bg-danger';
                   statusText = 'ĐÃ HỦY';
                   break;
           }
           
           // Tạo HTML cho card
           orderCard.innerHTML = `
               <div class="card-header d-flex justify-content-between align-items-center">
                   <div>
                       <h5>Đơn hàng #${order.id}</h5>
                       <small class="text-muted">${new Date(order.created_at).toLocaleString()}</small>
                   </div>
                   <span class="badge ${statusBadgeClass}">${statusText}</span>
               </div>
               <div class="card-body">
                   <p class="card-text">Nhà hàng: ${order.branch_name}</p>
                   <p class="card-text">Số lượng món: ${totalItems}</p>
                   <h6>Các món:</h6>
                   <ul class="list-group mb-3">
                       ${itemsHtml}
                   </ul>
                   <div class="d-flex justify-content-between">
                       <h5>Tổng cộng:</h5>
                       <h5>$${parseFloat(order.total_amount).toFixed(2)}</h5>
                   </div>
               </div>
           `;
           
           orderHistoryContainer.appendChild(orderCard);
       });
   } catch (error) {
       console.error('Lỗi khi tải lịch sử đơn hàng:', error);
       document.getElementById('order-history').innerHTML = '<div class="alert alert-danger">Không thể tải lịch sử đơn hàng.</div>';
   }
}