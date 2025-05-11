document.addEventListener('DOMContentLoaded', function() {
    // Kết nối WebSocket nếu người dùng đã đăng nhập
    const token = localStorage.getItem('access_token');
    const userId = localStorage.getItem('user_id');
    
    if (token && userId) {
        connectWebSocket(userId);
    }
});

// Kết nối WebSocket
function connectWebSocket(userId) {
    // Lấy hostname từ URL hiện tại
    const host = window.location.hostname;
    const port = '8000'; // Port của backend
    
    // Sử dụng protocol phù hợp
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    
    // Tạo kết nối WebSocket
    try {
        const socket = new WebSocket(`${protocol}://${host}:${port}/ws/${userId}`);
        
        socket.onopen = function(e) {
            console.log('Kết nối WebSocket đã được thiết lập');
        };
        
        socket.onmessage = function(event) {
            try {
                const data = JSON.parse(event.data);
                handleWebSocketMessage(data);
            } catch (error) {
                console.error('Lỗi xử lý tin nhắn WebSocket:', error);
            }
        };
        
        socket.onclose = function(event) {
            if (event.wasClean) {
                console.log(`Kết nối WebSocket đóng sạch, mã=${event.code}, lý do=${event.reason}`);
            } else {
                console.log('Kết nối WebSocket bị ngắt');
                // Thử kết nối lại sau một khoảng thời gian
                setTimeout(() => connectWebSocket(userId), 5000);
            }
        };
        
        socket.onerror = function(error) {
            console.error(`Lỗi WebSocket: ${error.message}`);
        };
        
        // Lưu socket vào window để truy cập toàn cục
        window.socket = socket;
    } catch (error) {
        console.error('Lỗi khi tạo kết nối WebSocket:', error);
    }
}

// Xử lý tin nhắn WebSocket đến
function handleWebSocketMessage(data) {
    console.log('Nhận tin nhắn WebSocket:', data);
    
    const userRole = localStorage.getItem('user_role');
    
    switch (data.event) {
        case 'delivery_request_active':
            // Cho tài xế, cập nhật danh sách đơn vận chuyển
            if (userRole === 'driver') {
                if (typeof loadAvailableDeliveries === 'function') {
                    loadAvailableDeliveries();
                }
                
                // Hiện thông báo
                showNotification('Yêu cầu vận chuyển mới', 'Có một yêu cầu vận chuyển mới.');
            }
            break;
        
        case 'delivery_request_assigned':
            // Cho tài xế, cập nhật đơn vận chuyển hiện tại
            if (userRole === 'driver') {
                if (typeof loadCurrentDelivery === 'function') {
                    loadCurrentDelivery();
                }
                
                // Hiện thông báo
                showNotification('Đã giao đơn vận chuyển', 'Bạn đã được giao một đơn vận chuyển mới.');
            }
            break;
        
        case 'order_item_assigned':
            // Cho nhân viên bếp, cập nhật danh sách món cần chuẩn bị
            if (userRole === 'kitchen_staff') {
                if (typeof loadKitchenDashboard === 'function') {
                    loadKitchenDashboard();
                }
                
                // Hiện thông báo
                showNotification('Món mới cần chuẩn bị', 'Bạn có món mới cần chuẩn bị.');
            }
            break;
        
        case 'delivery_request_delivered':
            // Cho khách hàng, cập nhật trạng thái đơn hàng
            if (userRole === 'customer') {
                // Hiện thông báo
                showNotification('Đơn hàng đã giao', 'Đơn hàng của bạn đã được giao! Vui lòng xác nhận.');
                
                // Tải lại lịch sử đơn hàng nếu đang ở trang đó
                if (window.location.pathname.includes('/customer/order-history.html')) {
                    loadOrderHistory();
                }
            }
            break;
    }
}

// Hiện thông báo trình duyệt
function showNotification(title, body) {
    // Kiểm tra xem trình duyệt có hỗ trợ thông báo không
    if (!("Notification" in window)) {
        console.log("Trình duyệt này không hỗ trợ thông báo");
        return;
    }
    
    // Kiểm tra xem đã được cấp quyền chưa
    if (Notification.permission === "granted") {
        const notification = new Notification(title, { body });
    }
    // Nếu chưa, yêu cầu quyền
    else if (Notification.permission !== "denied") {
        Notification.requestPermission().then(function (permission) {
            if (permission === "granted") {
                const notification = new Notification(title, { body });
            }
        });
    }
}