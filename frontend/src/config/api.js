// API Configuration for all backend services
// 
// 🚀 DEPLOYMENT NOTE:
// After deploying backend to Render, update line 18 with your actual Render URL
// Example: 'https://ey-codecrafters-backend.onrender.com'
// OR set VITE_BACKEND_URL environment variable in Vercel

// Detect environment and set base URL
const getBaseURL = () => {
  // Check for Vite environment variable (preferred for production)
  const backendURL = import.meta.env.VITE_BACKEND_URL;
  
  if (backendURL) {
    return backendURL.replace(/\/$/, ''); // Remove trailing slash
  }
  
  // Check if we're in production (Vercel sets NODE_ENV)
  if (import.meta.env.PROD) {
    // Update this with your actual Render URL after deployment
    return 'https://ey-code-crafters.onrender.com';
  }
  
  // Default to localhost for development
  return 'http://localhost';
};

const API_BASE_URL = getBaseURL();
const IS_PRODUCTION = import.meta.env.PROD && !API_BASE_URL.includes('localhost');

// Helper to build endpoint URL - production uses mounted paths
const buildEndpoint = (path, port = null) => {
  if (IS_PRODUCTION) {
    // In production, all services are mounted under the main domain
    return `${API_BASE_URL}${path}`;
  }
  // In development, services run on different ports
  return `${API_BASE_URL}:${port}${path}`;
};

export const API_ENDPOINTS = {
  // Session Management (Port 8000 / /session in production)
  SESSION_MANAGER: IS_PRODUCTION ? `${API_BASE_URL}/session` : `${API_BASE_URL}:8000`,
  SESSION_START: buildEndpoint('/session/start', 8000),
  SESSION_END: buildEndpoint('/session/end', 8000),
  SESSION_UPDATE: buildEndpoint('/session/update', 8000),
  SESSION_LOGIN: buildEndpoint('/session/login', 8000),
  
  // Authentication (Password-based - Port 8000 / /session in production)
  AUTH_SIGNUP: buildEndpoint('/auth/signup', 8000),
  AUTH_LOGIN: buildEndpoint('/auth/login', 8000),
  AUTH_LOGOUT: buildEndpoint('/auth/logout', 8000),
  AUTH_QR_INIT: buildEndpoint('/auth/qr-init', 8000),
  AUTH_QR_VERIFY: buildEndpoint('/auth/qr-verify', 8000),
  
  // Sales Agent with Orchestration (Port 8010 / /sales in production)
  SALES_AGENT: IS_PRODUCTION ? `${API_BASE_URL}/sales` : `${API_BASE_URL}:8010`,
  SEND_MESSAGE: buildEndpoint('/sales/api/message', 8010),
  RESUME_SESSION: buildEndpoint('/sales/api/resume_session', 8010),
  VISUAL_SEARCH: buildEndpoint('/sales/api/visual-search', 8010),
  RECOMMENDATIONS: buildEndpoint('/sales/api/recommendations', 8010),
  GIFT_SUGGESTIONS: buildEndpoint('/sales/api/gift-suggestions', 8010),
  CHECKOUT: buildEndpoint('/sales/api/checkout', 8010),
  POST_PAYMENT: buildEndpoint('/sales/api/post-payment', 8010),
  VERIFY_INVENTORY: buildEndpoint('/sales/api/verify-inventory', 8010),
  SEASONAL_TRENDS: buildEndpoint('/sales/api/seasonal-trends', 8010),

  // Inventory Agent
  INVENTORY: IS_PRODUCTION ? `${API_BASE_URL}/inventory` : `${API_BASE_URL}:8001`,
  INVENTORY_CHECK: buildEndpoint('/inventory', 8001),
  INVENTORY_HOLD: buildEndpoint('/inventory/hold', 8001),
  INVENTORY_RELEASE: buildEndpoint('/inventory/release', 8001),
  INVENTORY_SIMULATE_SALE: buildEndpoint('/inventory/simulate/sale', 8001),

  // Loyalty Agent
  LOYALTY: IS_PRODUCTION ? `${API_BASE_URL}/loyalty` : `${API_BASE_URL}:8002`,
  LOYALTY_POINTS: buildEndpoint('/loyalty/points', 8002),
  LOYALTY_TIER_INFO: buildEndpoint('/loyalty/tier', 8002),
  LOYALTY_APPLY: buildEndpoint('/loyalty/apply', 8002),
  LOYALTY_ADD_POINTS: buildEndpoint('/loyalty/add-points', 8002),
  LOYALTY_VALIDATE_COUPON: buildEndpoint('/loyalty/validate-coupon', 8002),
  LOYALTY_PROMOTIONS: buildEndpoint('/loyalty/available-promotions', 8002),

  // Payment Agent (proxied through Sales Agent)
  PAYMENT: buildEndpoint('/sales/api/payment', 8010),
  PAYMENT_PROCESS: buildEndpoint('/sales/api/payment/process', 8010),
  PAYMENT_TRANSACTION: buildEndpoint('/sales/api/payment/transaction', 8010),
  PAYMENT_USER_TRANSACTIONS: buildEndpoint('/sales/api/payment/user-transactions', 8010),
  PAYMENT_METHODS: buildEndpoint('/sales/api/payment/methods', 8010),
  PAYMENT_REFUND: buildEndpoint('/sales/api/payment/refund', 8010),
  PAYMENT_AUTHORIZE: buildEndpoint('/sales/api/payment/authorize', 8010),
  PAYMENT_CAPTURE: buildEndpoint('/sales/api/payment/capture', 8010),
  PAYMENT_NEXT_ORDER_ID: buildEndpoint('/sales/api/payment/next-order-id', 8010),
  PAYMENT_RAZORPAY_CREATE: buildEndpoint('/sales/api/payment/razorpay/create-order', 8010),
  PAYMENT_RAZORPAY_VERIFY: buildEndpoint('/sales/api/payment/razorpay/verify-payment', 8010),

  // Fulfillment Agent
  FULFILLMENT: IS_PRODUCTION ? `${API_BASE_URL}/fulfillment` : `${API_BASE_URL}:8004`,
  FULFILLMENT_START: buildEndpoint('/fulfillment/start', 8004),
  FULFILLMENT_STATUS: buildEndpoint('/fulfillment', 8004),
  FULFILLMENT_UPDATE: buildEndpoint('/fulfillment/update-status', 8004),
  FULFILLMENT_DELIVERED: buildEndpoint('/fulfillment/mark-delivered', 8004),
  FULFILLMENT_CANCEL: buildEndpoint('/fulfillment/cancel-order', 8004),
  FULFILLMENT_SET_DELIVERY_WINDOW: buildEndpoint('/fulfillment/set-delivery-window', 8004),

  // Post-Purchase Agent
  POST_PURCHASE: IS_PRODUCTION ? `${API_BASE_URL}/post-purchase` : `${API_BASE_URL}:8005`,
  POST_PURCHASE_RETURN: buildEndpoint('/post-purchase/return', 8005),
  POST_PURCHASE_EXCHANGE: buildEndpoint('/post-purchase/exchange', 8005),
  POST_PURCHASE_COMPLAINT: buildEndpoint('/post-purchase/complaint', 8005),
  POST_PURCHASE_FEEDBACK: buildEndpoint('/post-purchase/feedback', 8005),
  POST_PURCHASE_RETURN_REASONS: buildEndpoint('/post-purchase/return-reasons', 8005),
  POST_PURCHASE_RETURNS: buildEndpoint('/post-purchase/returns', 8005),
  POST_PURCHASE_ISSUE_TYPES: buildEndpoint('/post-purchase/issue-types', 8005),
  POST_PURCHASE_REGISTER_ORDER: buildEndpoint('/post-purchase/register-order', 8005),

  // Stylist Agent
  STYLIST: IS_PRODUCTION ? `${API_BASE_URL}/stylist` : `${API_BASE_URL}:8006`,
  STYLIST_OUTFIT_SUGGESTIONS: buildEndpoint('/stylist/outfit-suggestions', 8006),
  STYLIST_CARE_INSTRUCTIONS: buildEndpoint('/stylist/care-instructions', 8006),
  STYLIST_OCCASION: buildEndpoint('/stylist/occasion-styling', 8006),
  STYLIST_SEASONAL: buildEndpoint('/stylist/seasonal-styling', 8006),
  STYLIST_FIT_FEEDBACK: buildEndpoint('/stylist/fit-feedback', 8006),
  
  // Data API (CSV Data + Supabase Products)
  DATA_API: IS_PRODUCTION ? `${API_BASE_URL}/data` : `${API_BASE_URL}:8007`,
  DATA_PRODUCTS: buildEndpoint('/data/products', 8007),
  DATA_CUSTOMERS: buildEndpoint('/data/customers', 8007),
  DATA_ORDERS: buildEndpoint('/data/orders', 8007),
  DATA_STORES: buildEndpoint('/data/stores', 8007),
  DATA_INVENTORY: buildEndpoint('/data/inventory', 8007),
  DATA_PAYMENTS: buildEndpoint('/data/payments', 8007),
  
  // Recommendation Agent
  RECOMMENDATION: IS_PRODUCTION ? `${API_BASE_URL}/recommendation` : `${API_BASE_URL}:8008`,
  RECOMMENDATION_PERSONALIZED: buildEndpoint('/recommendation/recommend', 8008),
  
  // Ambient Commerce (Visual Search)
  AMBIENT_COMMERCE: IS_PRODUCTION ? `${API_BASE_URL}/ambient` : `${API_BASE_URL}:8017`,
  VISUAL_SEARCH_IMAGE: buildEndpoint('/ambient/search/image', 8017),
  
  // Virtual Circles (Community Chat)
  VIRTUAL_CIRCLES: IS_PRODUCTION ? `${API_BASE_URL}/virtual-circles` : `${API_BASE_URL}:8009`,
  
  // Sales Agent Memory Endpoints (Port 8000 / /session in production)
  SESSION_CONTEXT: buildEndpoint('/session/{id}/context', 8000),
  SESSION_SUMMARY: buildEndpoint('/session/{id}/summary', 8000),
  SESSION_RECOMMENDATIONS: buildEndpoint('/session/{id}/recommendations', 8000),
  SESSION_CART: buildEndpoint('/session/{id}/cart', 8000),
};

// Helper function for API calls with error handling
export const apiCall = async (url, options = {}) => {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorBody = await response.json().catch(() => null);
      const msg = (errorBody && (errorBody.message || errorBody.error)) || `HTTP ${response.status}`;
      const err = new Error(msg);
      err.status = response.status;
      err.body = errorBody;
      throw err;
    }

    return await response.json();
  } catch (error) {
    console.error(`API call failed for ${url}:`, error);
    throw error;
  }
};

export default API_ENDPOINTS;
