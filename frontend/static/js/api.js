// Định nghĩa base URL và các endpoints
const API_BASE_URL = 'http://localhost:8000';
const API_ENDPOINTS = {
    login: `${API_BASE_URL}/auth/login`,
    register: `${API_BASE_URL}/auth/register`,
    me: `${API_BASE_URL}/auth/me`,
    branches: `${API_BASE_URL}/branches`,
    menuItems: `${API_BASE_URL}/menu-items`,
    orders: `${API_BASE_URL}/orders`,
    myOrders: `${API_BASE_URL}/orders/mine`,
    payments: `${API_BASE_URL}/payments`,
    myDeliveryRequests: `${API_BASE_URL}/delivery-requests/mine`,
    users: `${API_BASE_URL}/users`,
    drivers: `${API_BASE_URL}/drivers`,
    kitchenStaffs: `${API_BASE_URL}/kitchen-staffs`,
    notAcceptedDeliveryRequests: `${API_BASE_URL}/delivery-requests/not-accepted`
};

// Khởi tạo đối tượng API với các phương thức
const api = {
    login: async (username, password) => {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch(API_ENDPOINTS.login, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Đăng nhập thất bại');
        }

        return await response.json();
    },

    register: async (userData) => {
        const response = await fetch(API_ENDPOINTS.register, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });

        if (!response.ok) {
            throw new Error('Đăng ký thất bại');
        }

        return await response.json();
    },

    getCurrentUser: async () => {
        const response = await fetch(API_ENDPOINTS.me, {
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });

        if (!response.ok) {
            throw new Error('Không thể lấy thông tin người dùng');
        }

        return await response.json();
    },

    getBranches: async () => {
        const response = await fetch(API_ENDPOINTS.branches, {
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });

        if (!response.ok) {
            throw new Error('Không thể lấy danh sách chi nhánh');
        }

        return await response.json();
    },

    getMenuItems: async (branchId) => {
        const response = await fetch(`${API_ENDPOINTS.branches}/${branchId}/menu-items`, {
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });

        if (!response.ok) {
            throw new Error('Không thể lấy menu');
        }

        return await response.json();
    },

    createOrder: async (orderData) => {
        const response = await fetch(API_ENDPOINTS.orders, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${getToken()}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(orderData)
        });

        if (!response.ok) {
            throw new Error('Không thể tạo đơn hàng');
        }

        return await response.json();
    },

    getMyOrders: async () => {
        const response = await fetch(API_ENDPOINTS.myOrders, {
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });

        if (!response.ok) {
            throw new Error('Không thể lấy lịch sử đơn hàng');
        }

        return await response.json();
    },

    checkout: async (paymentId, paymentMethod) => {
        const response = await fetch(`${API_ENDPOINTS.payments}/${paymentId}/checkout`, {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${getToken()}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ payment_method: paymentMethod })
        });

        if (!response.ok) {
            throw new Error('Thanh toán thất bại');
        }

        return await response.json();
    },

    // APIs cho Driver
    getNotAcceptedDeliveryRequests: async () => {
        const response = await fetch(API_ENDPOINTS.notAcceptedDeliveryRequests, {
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Không thể lấy danh sách đơn vận chuyển');
        }
        
        return await response.json();
    },

    getMyDeliveryRequests: async () => {
        const response = await fetch(API_ENDPOINTS.myDeliveryRequests, {
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Không thể lấy danh sách đơn vận chuyển của tôi');
        }
        
        return await response.json();
    },

    acceptDeliveryRequest: async (id) => {
        const response = await fetch(`${API_BASE_URL}/delivery-requests/${id}/accept`, {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Không thể nhận đơn vận chuyển');
        }
        
        return await response.json();
    },

    deliveringDeliveryRequest: async (id) => {
        const response = await fetch(`${API_BASE_URL}/delivery-requests/${id}/delivering`, {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Không thể bắt đầu vận chuyển');
        }
        
        return await response.json();
    },

    deliveredDeliveryRequest: async (id) => {
        const response = await fetch(`${API_BASE_URL}/delivery-requests/${id}/delivered`, {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Không thể đánh dấu đã giao hàng');
        }
        
        return await response.json();
    },

    customerConfirmedDelivery: async (id) => {
        const response = await fetch(`${API_BASE_URL}/delivery-requests/${id}/customer-confirmed`, {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Không thể xác nhận đã nhận hàng');
        }
        
        return await response.json();
    },

    // APIs cho Kitchen Staff
    getOrderItemsForKitchenStaff: async () => {
        const response = await fetch(`${API_BASE_URL}/order-items/mine`, {
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Không thể lấy danh sách món cần chuẩn bị');
        }
        
        return await response.json();
    },

    markOrderItemReady: async (orderItemId) => {
        const response = await fetch(`${API_BASE_URL}/order-items/${orderItemId}/ready`, {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Không thể đánh dấu món đã sẵn sàng');
        }
        
        return await response.json();
    },

    // Admin API extensions
    getUsers: async () => {
        const response = await fetch(API_ENDPOINTS.users, {
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Không thể lấy danh sách người dùng');
        }
        
        return await response.json();
    },

    createBranch: async (branchData) => {
        const response = await fetch(API_ENDPOINTS.branches, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${getToken()}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(branchData)
        });
        
        if (!response.ok) {
            throw new Error('Không thể tạo chi nhánh');
        }
        
        return await response.json();
    },

    updateBranch: async (branchId, branchData) => {
        const response = await fetch(`${API_ENDPOINTS.branches}/${branchId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${getToken()}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(branchData)
        });
        
        if (!response.ok) {
            throw new Error('Không thể cập nhật chi nhánh');
        }
        
        return await response.json();
    },

    deleteBranch: async (branchId) => {
        const response = await fetch(`${API_ENDPOINTS.branches}/${branchId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Không thể xóa chi nhánh');
        }
        
        return await response.json();
    },

    getDrivers: async (branchId) => {
        const response = await fetch(`${API_ENDPOINTS.drivers}/by-branch/${branchId}`, {
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Không thể lấy danh sách tài xế');
        }
        
        return await response.json();
    },

    getKitchenStaff: async (branchId) => {
        const response = await fetch(`${API_ENDPOINTS.kitchenStaffs}/by-branch/${branchId}`, {
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Không thể lấy danh sách nhân viên bếp');
        }
        
        return await response.json();
    },

    assignDriver: async (driverData) => {
        const response = await fetch(`${API_ENDPOINTS.drivers}/assign`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${getToken()}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(driverData)
        });
        
        if (!response.ok) {
            throw new Error('Không thể phân công tài xế');
        }
        
        return await response.json();
    },

    assignKitchenStaff: async (kitchenStaffData) => {
        const response = await fetch(`${API_ENDPOINTS.kitchenStaffs}/assign`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${getToken()}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(kitchenStaffData)
        });
        
        if (!response.ok) {
            throw new Error('Không thể phân công nhân viên bếp');
        }
        
        return await response.json();
    },

    createMenuItem: async (branchId, menuItemData) => {
        const response = await fetch(`${API_ENDPOINTS.branches}/${branchId}/menu-items`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${getToken()}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(menuItemData)
        });
        
        if (!response.ok) {
            throw new Error('Không thể tạo món ăn');
        }
        
        return await response.json();
    },

    updateMenuItem: async (menuItemId, menuItemData) => {
        const response = await fetch(`${API_ENDPOINTS.menuItems}/${menuItemId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${getToken()}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(menuItemData)
        });
        
        if (!response.ok) {
            throw new Error('Không thể cập nhật món ăn');
        }
        
        return await response.json();
    },

    deleteMenuItem: async (menuItemId) => {
        const response = await fetch(`${API_ENDPOINTS.menuItems}/${menuItemId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Không thể xóa món ăn');
        }
        
        return await response.json();
    },

    createStaffAccount: async (userData) => {
        const response = await fetch(`${API_ENDPOINTS.users}/register`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${getToken()}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });
        
        if (!response.ok) {
            throw new Error('Không thể tạo tài khoản nhân viên');
        }
        
        return await response.json();
    },

    toggleActiveAccount: async (userId, isActive = true) => {
        const endpoint = isActive ? 
            `${API_ENDPOINTS.users}/${userId}/active` : 
            `${API_ENDPOINTS.users}/${userId}/deactive`;
        
        const response = await fetch(endpoint, {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Không thể cập nhật trạng thái tài khoản');
        }
        
        return await response.json();
    }
};