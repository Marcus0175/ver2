// API base URL
const API_BASE_URL = 'http://localhost:8000';

// Hàm lấy token từ localStorage
function getToken() {
    return localStorage.getItem('access_token');
}

document.addEventListener('DOMContentLoaded', function() {
    // Chuyển hướng nếu đã đăng nhập
    const token = localStorage.getItem('access_token');
    if (token) {
        redirectBasedOnRole();
    }
    
    // Kiểm tra nếu có thông báo đăng ký thành công
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('registered') === 'true') {
        document.getElementById('registered-message')?.classList.remove('d-none');
    }
    
    // Xử lý submit form đăng nhập
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const errorMessage = document.getElementById('error-message');
            
            try {
                errorMessage.classList.add('d-none');
                
                // Tạo FormData để gửi theo đúng định dạng mà backend chấp nhận
                const formData = new FormData();
                formData.append('username', username);
                formData.append('password', password);
                
                // Gọi API đăng nhập
                const response = await fetch(`${API_BASE_URL}/auth/login`, {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    throw new Error('Đăng nhập thất bại');
                }
                
                const data = await response.json();
                localStorage.setItem('access_token', data.access_token);
                
                // Lấy thông tin người dùng
                const userResponse = await fetch(`${API_BASE_URL}/auth/me`, {
                    headers: {
                        'Authorization': `Bearer ${data.access_token}`
                    }
                });
                
                if (!userResponse.ok) {
                    throw new Error('Không thể lấy thông tin người dùng');
                }
                
                const userData = await userResponse.json();
                localStorage.setItem('user_role', userData.role);
                localStorage.setItem('user_id', userData.id);
                
                redirectBasedOnRole();
            } catch (error) {
                errorMessage.textContent = 'Tên đăng nhập hoặc mật khẩu không đúng';
                errorMessage.classList.remove('d-none');
                console.error('Lỗi đăng nhập:', error);
            }
        });
    }
    
    // Xử lý submit form đăng ký
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const errorMessage = document.getElementById('error-message');
            
            try {
                errorMessage.classList.add('d-none');
                
                const response = await fetch(`${API_BASE_URL}/auth/register`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        username,
                        email,
                        password,
                        role: 'customer'  // Vai trò mặc định
                    })
                });
                
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || 'Đăng ký thất bại');
                }
                
                window.location.href = 'index.html?registered=true';
            } catch (error) {
                errorMessage.textContent = error.message || 'Đăng ký thất bại. Vui lòng thử lại.';
                errorMessage.classList.remove('d-none');
                console.error('Lỗi đăng ký:', error);
            }
        });
    }
});

// Chuyển hướng dựa trên vai trò người dùng
function redirectBasedOnRole() {
    const role = localStorage.getItem('user_role');
    
    switch (role) {
        case 'customer':
            window.location.href = 'customer/dashboard.html';
            break;
        case 'admin':
        case 'owner':
            window.location.href = 'admin/dashboard.html';
            break;
        case 'driver':
            window.location.href = 'driver/dashboard.html';
            break;
        case 'kitchen_staff':
            window.location.href = 'kitchen/dashboard.html';
            break;
        default:
            // Nếu không nhận diện được vai trò, đăng xuất
            logout();
    }
}

// Hàm đăng xuất
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_role');
    localStorage.removeItem('user_id');
    window.location.href = '/index.html';
}