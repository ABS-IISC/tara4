/**
 * Network Error Handler
 *
 * Fixes "NetworkError when attempting to fetch resource" issues
 * Provides better error handling, retry logic, and user feedback
 */

// Store original fetch for wrapper
const originalFetch = window.fetch;

// Enhanced fetch with error handling and retry
window.fetch = function(url, options = {}) {
    // Add default timeout if not specified
    // Use longer timeout for AI endpoints (240 seconds / 4 minutes)
    let defaultTimeout = 30000; // 30 seconds default

    // AI analysis endpoints need more time
    if (url.includes('/analyze_section') ||
        url.includes('/chat') ||
        url.includes('/complete_review') ||
        url.includes('/analyze_all_sections')) {
        defaultTimeout = 240000; // 240 seconds (4 minutes) for AI operations - increased for reliable analysis
    }

    const timeout = options.timeout || defaultTimeout;

    // Create timeout promise
    const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Request timeout')), timeout);
    });

    // Add default headers if not present
    if (!options.headers) {
        options.headers = {};
    }

    // Ensure Content-Type is set for POST/PUT requests
    if (['POST', 'PUT', 'PATCH'].includes(options.method?.toUpperCase())) {
        if (!options.headers['Content-Type'] && options.body && typeof options.body === 'string') {
            options.headers['Content-Type'] = 'application/json';
        }
    }

    // Race between fetch and timeout
    return Promise.race([
        originalFetch(url, options),
        timeoutPromise
    ])
    .catch(error => {
        console.error('Fetch error details:', {
            url: url,
            method: options.method || 'GET',
            error: error.message,
            stack: error.stack
        });

        // Provide user-friendly error message
        let userMessage = 'Network request failed';

        if (error.message === 'Request timeout') {
            // Check if this is an AI analysis endpoint
            if (url.includes('/analyze_section') || url.includes('/chat') ||
                url.includes('/complete_review') || url.includes('/analyze_all_sections')) {
                userMessage = 'AI analysis is taking longer than expected (>4 minutes). This may be due to:\n' +
                             '• High AWS Bedrock load or API throttling\n' +
                             '• Network connectivity issues\n' +
                             '• Large document content\n\n' +
                             'Please wait a moment and try again, or contact support if the issue persists.';
            } else {
                userMessage = 'Request timed out. Please check your connection and try again.';
            }
        } else if (error.message === 'Failed to fetch') {
            userMessage = 'Unable to connect to server. Please ensure:\n' +
                         '1. The server is running (python app.py)\n' +
                         '2. You are accessing the correct URL\n' +
                         '3. Your firewall allows the connection';
        } else if (error.name === 'TypeError') {
            userMessage = 'Network error occurred. Please refresh the page and try again.';
        }

        // Show notification if function exists
        if (typeof showNotification === 'function') {
            showNotification(userMessage, 'error');
        } else {
            console.error('Network Error:', userMessage);
            alert(userMessage);
        }

        // Re-throw with enhanced error info
        const enhancedError = new Error(userMessage);
        enhancedError.originalError = error;
        enhancedError.url = url;
        enhancedError.method = options.method || 'GET';
        throw enhancedError;
    });
};

// Function to test server connectivity
window.testServerConnection = function() {
    console.log('Testing server connection...');

    return fetch('/health', {
        method: 'GET',
        timeout: 5000
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Server returned ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('✅ Server connection successful:', data);
        if (typeof showNotification === 'function') {
            showNotification('✅ Server connection successful', 'success');
        }
        return true;
    })
    .catch(error => {
        console.error('❌ Server connection failed:', error);
        if (typeof showNotification === 'function') {
            showNotification('❌ Server connection failed: ' + error.message, 'error');
        }
        return false;
    });
};

// Function to retry failed requests
window.retryFetch = function(url, options = {}, maxRetries = 3, delayMs = 1000) {
    let retries = 0;

    const attemptFetch = () => {
        return fetch(url, options)
            .catch(error => {
                retries++;

                if (retries >= maxRetries) {
                    console.error(`❌ Failed after ${maxRetries} retries:`, error);
                    throw error;
                }

                console.warn(`⚠️ Retry ${retries}/${maxRetries} for ${url} after ${delayMs}ms...`);

                // Wait before retrying
                return new Promise(resolve => setTimeout(resolve, delayMs))
                    .then(() => attemptFetch());
            });
    };

    return attemptFetch();
};

// Add network status monitoring
let isOnline = navigator.onLine;

window.addEventListener('online', () => {
    isOnline = true;
    console.log('✅ Network connection restored');
    if (typeof showNotification === 'function') {
        showNotification('✅ Network connection restored', 'success');
    }
});

window.addEventListener('offline', () => {
    isOnline = false;
    console.warn('⚠️ Network connection lost');
    if (typeof showNotification === 'function') {
        showNotification('⚠️ Network connection lost. Some features may not work.', 'warning');
    }
});

// Export helper function to check if online
window.isNetworkOnline = function() {
    return isOnline;
};

// Add fetch interceptor for debugging
window.enableFetchDebugging = function() {
    const originalFetch = window.fetch;

    window.fetch = function(...args) {
        console.log('🔍 Fetch Debug:', {
            url: args[0],
            options: args[1],
            timestamp: new Date().toISOString()
        });

        return originalFetch.apply(this, args)
            .then(response => {
                console.log('✅ Fetch Success:', {
                    url: args[0],
                    status: response.status,
                    statusText: response.statusText
                });
                return response;
            })
            .catch(error => {
                console.error('❌ Fetch Error:', {
                    url: args[0],
                    error: error.message,
                    stack: error.stack
                });
                throw error;
            });
    };

    console.log('🔍 Fetch debugging enabled');
};

// Log that network error handler is loaded
console.log('✅ Network Error Handler loaded');
console.log('💡 Use testServerConnection() to test connectivity');
console.log('💡 Use enableFetchDebugging() to debug all fetch requests');
