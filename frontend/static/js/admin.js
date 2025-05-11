// Admin API extensions
api.getUsers = async () => {
    const response = await fetch(API_ENDPOINTS.users, {
        headers: {
            'Authorization': `Bearer ${getToken()}`
        }
    });
    
    if (!response.ok) {
        throw new Error('Failed to get users');
    }
    
    return await response.json();
};

api.createBranch = async (branchData) => {
    const response = await fetch(API_ENDPOINTS.branches, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${getToken()}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(branchData)
    });
    
    if (!response.ok) {
        throw new Error('Failed to create branch');
    }
    
    return await response.json();
};

api.updateBranch = async (branchId, branchData) => {
    const response = await fetch(`${API_ENDPOINTS.branches}/${branchId}`, {
        method: 'PUT',
        headers: {
            'Authorization': `Bearer ${getToken()}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(branchData)
    });
    
    if (!response.ok) {
        throw new Error('Failed to update branch');
    }
    
    return await response.json();
};

api.deleteBranch = async (branchId) => {
    const response = await fetch(`${API_ENDPOINTS.branches}/${branchId}`, {
        method: 'DELETE',
        headers: {
            'Authorization': `Bearer ${getToken()}`
        }
    });
    
    if (!response.ok) {
        throw new Error('Failed to delete branch');
    }
    
    return await response.json();
};

api.getDrivers = async (branchId) => {
    const response = await fetch(`${API_ENDPOINTS.drivers}/by-branch/${branchId}`, {
        headers: {
            'Authorization': `Bearer ${getToken()}`
        }
    });
    
    if (!response.ok) {
        throw new Error('Failed to get drivers');
    }
    
    return await response.json();
};

api.getKitchenStaff = async (branchId) => {
    const response = await fetch(`${API_ENDPOINTS.kitchenStaffs}/by-branch/${branchId}`, {
        headers: {
            'Authorization': `Bearer ${getToken()}`
        }
    });
    
    if (!response.ok) {
        throw new Error('Failed to get kitchen staff');
    }
    
    return await response.json();
};

api.assignDriver = async (driverData) => {
    const response = await fetch(`${API_ENDPOINTS.drivers}/assign`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${getToken()}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(driverData)
    });
    
    if (!response.ok) {
        throw new Error('Failed to assign driver');
    }
    
    return await response.json();
};

api.assignKitchenStaff = async (kitchenStaffData) => {
    const response = await fetch(`${API_ENDPOINTS.kitchenStaffs}/assign`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${getToken()}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(kitchenStaffData)
    });
    
    if (!response.ok) {
        throw new Error('Failed to assign kitchen staff');
    }
    
    return await response.json();
};

api.createMenuItem = async (branchId, menuItemData) => {
    const response = await fetch(`${API_ENDPOINTS.branches}/${branchId}/menu-items`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${getToken()}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(menuItemData)
    });
    
    if (!response.ok) {
        throw new Error('Failed to create menu item');
    }
    
    return await response.json();
};

api.updateMenuItem = async (menuItemId, menuItemData) => {
    const response = await fetch(`${API_ENDPOINTS.menuItems}/${menuItemId}`, {
        method: 'PUT',
        headers: {
            'Authorization': `Bearer ${getToken()}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(menuItemData)
    });
    
    if (!response.ok) {
        throw new Error('Failed to update menu item');
    }
    
    return await response.json();
};

api.deleteMenuItem = async (menuItemId) => {
    const response = await fetch(`${API_ENDPOINTS.menuItems}/${menuItemId}`, {
        method: 'DELETE',
        headers: {
            'Authorization': `Bearer ${getToken()}`
        }
    });
    
    if (!response.ok) {
        throw new Error('Failed to delete menu item');
    }
    
    return await response.json();
};

api.createStaffAccount = async (userData) => {
    const response = await fetch(`${API_ENDPOINTS.users}/register`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${getToken()}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
    });
    
    if (!response.ok) {
        throw new Error('Failed to create staff account');
    }
    
    return await response.json();
};

api.toggleActiveAccount = async (userId, isActive = true) => {
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
        throw new Error('Failed to update account status');
    }
    
    return await response.json();
};