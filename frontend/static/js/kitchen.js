// Kitchen Staff API extensions
api.getOrderItemsForKitchenStaff = async () => {
    const response = await fetch(`${API_BASE_URL}/order-items/mine`, {
        headers: {
            'Authorization': `Bearer ${getToken()}`
        }
    });
    
    if (!response.ok) {
        throw new Error('Failed to get order items');
    }
    
    return await response.json();
};

api.markOrderItemReady = async (orderItemId) => {
    const response = await fetch(`${API_BASE_URL}/order-items/${orderItemId}/ready`, {
        method: 'PATCH',
        headers: {
            'Authorization': `Bearer ${getToken()}`
        }
    });
    
    if (!response.ok) {
        throw new Error('Failed to mark order item as ready');
    }
    
    return await response.json();
};