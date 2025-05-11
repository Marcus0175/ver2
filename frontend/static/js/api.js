// API endpoints extension
API_ENDPOINTS.users = `${API_BASE_URL}/users`;
API_ENDPOINTS.drivers = `${API_BASE_URL}/drivers`;
API_ENDPOINTS.kitchenStaffs = `${API_BASE_URL}/kitchen-staffs`;
API_ENDPOINTS.notAcceptedDeliveryRequests = `${API_BASE_URL}/delivery-requests/not-accepted`;
API_ENDPOINTS.myDeliveryRequests = `${API_BASE_URL}/delivery-requests/mine`;

// Driver API
api.getNotAcceptedDeliveryRequests = async () => {
    const response = await fetch(API_ENDPOINTS.notAcceptedDeliveryRequests, {
        headers: {
            'Authorization': `Bearer ${getToken()}`
        }
    });
    
    if (!response.ok) {
        throw new Error('Failed to get not accepted delivery requests');
    }
    
    return await response.json();
};

api.getMyDeliveryRequests = async () => {
    const response = await fetch(API_ENDPOINTS.myDeliveryRequests, {
        headers: {
            'Authorization': `Bearer ${getToken()}`
        }
    });
    
    if (!response.ok) {
        throw new Error('Failed to get my delivery requests');
    }
    
    return await response.json();
};

api.acceptDeliveryRequest = async (id) => {
    const response = await fetch(`${API_BASE_URL}/delivery-requests/${id}/accept`, {
        method: 'PATCH',
        headers: {
            'Authorization': `Bearer ${getToken()}`
        }
    });
    
    if (!response.ok) {
        throw new Error('Failed to accept delivery request');
    }
    
    return await response.json();
};

api.deliveringDeliveryRequest = async (id) => {
    const response = await fetch(`${API_BASE_URL}/delivery-requests/${id}/delivering`, {
        method: 'PATCH',
        headers: {
            'Authorization': `Bearer ${getToken()}`
        }
    });
    
    if (!response.ok) {
        throw new Error('Failed to start delivery');
    }
    
    return await response.json();
};

api.deliveredDeliveryRequest = async (id) => {
    const response = await fetch(`${API_BASE_URL}/delivery-requests/${id}/delivered`, {
        method: 'PATCH',
        headers: {
            'Authorization': `Bearer ${getToken()}`
        }
    });
    
    if (!response.ok) {
        throw new Error('Failed to mark as delivered');
    }
    
    return await response.json();
};

api.customerConfirmedDelivery = async (id) => {
    const response = await fetch(`${API_BASE_URL}/delivery-requests/${id}/customer-confirmed`, {
        method: 'PATCH',
        headers: {
            'Authorization': `Bearer ${getToken()}`
        }
    });
    
    if (!response.ok) {
        throw new Error('Failed to confirm delivery');
    }
    
    return await response.json();
};