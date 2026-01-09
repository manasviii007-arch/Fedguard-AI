// FedGuard AI Frontend Configuration

const CONFIG = {
    // Default to localhost for development
    // User Instructions: Replace this URL with your deployed Backend API URL (e.g., https://fedguard-backend.onrender.com/api/v1)
    API_BASE_URL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
        ? 'http://localhost:8000/api/v1' 
        : 'https://fedguard-api-demo.onrender.com/api/v1', 

    // Feature Flags
    ENABLE_MOCK_FALLBACK: true, // If backend fails, fallback to local mock mode
    DEBUG_MODE: true
};

console.log("FedGuard Config Loaded:", CONFIG);
