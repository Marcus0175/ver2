document.addEventListener('DOMContentLoaded', function() {
    // Redirect if already logged in
    const token = localStorage.getItem('access_token');
    if (token) {
        redirectBasedOnRole();
    }
    
    // Handle login form submission
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const errorMessage = document.getElementById('error-message');
            
            try {
                errorMessage.classList.add('d-none');
                const data = await api.login(username, password);
                localStorage.setItem('access_token', data.access_token);
                
                // Get user data to determine role
                const userData = await api.getCurrentUser();
                localStorage.setItem('user_role', userData.role);
                localStorage.setItem('user_id', userData.id);
                
                redirectBasedOnRole();
            } catch (error) {
                errorMessage.textContent = 'Invalid username or password';
                errorMessage.classList.remove('d-none');
                console.error('Login error:', error);
            }
        });
    }
    
    // Handle register form submission
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
                await api.register({
                    username,
                    email,
                    password,
                    role: 'customer'  // Default role
                });
                
                window.location.href = 'index.html?registered=true';
            } catch (error) {
                errorMessage.textContent = 'Registration failed. Please try again.';
                errorMessage.classList.remove('d-none');
                console.error('Registration error:', error);
            }
        });
    }
});

// Redirect based on user role
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
            // If role not recognized, log out
            localStorage.removeItem('access_token');
            localStorage.removeItem('user_role');
            localStorage.removeItem('user_id');
            window.location.href = 'index.html';
    }
}

// Logout function
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_role');
    localStorage.removeItem('user_id');
    window.location.href = '/index.html';
}