// Configuration
const API_BASE_URL = 'http://localhost:8000';

// DOM Elements
const pdfForm = document.getElementById('pdfForm');
const submitButton = document.getElementById('submitButton');
const loadingState = document.getElementById('loadingState');
const successState = document.getElementById('successState');
const errorState = document.getElementById('errorState');
const downloadButton = document.getElementById('downloadButton');
const generateAnotherButton = document.getElementById('generateAnotherButton');
const tryAgainButton = document.getElementById('tryAgainButton');
const successMessage = document.getElementById('successMessage');
const errorMessage = document.getElementById('errorMessage');

// Form inputs
const figmaLinkInput = document.getElementById('figmaLink');
const figmaTokenInput = document.getElementById('figmaToken');
const reportFileInput = document.getElementById('reportFile');

// State Management
let currentState = 'form'; // 'form', 'loading', 'success', 'error'

/**
 * Show specific state and hide others
 */
function showState(state) {
    currentState = state;

    // Hide all states
    pdfForm.classList.add('hidden');
    loadingState.classList.add('hidden');
    successState.classList.add('hidden');
    errorState.classList.add('hidden');

    // Show requested state
    switch (state) {
        case 'form':
            pdfForm.classList.remove('hidden');
            break;
        case 'loading':
            loadingState.classList.remove('hidden');
            break;
        case 'success':
            successState.classList.remove('hidden');
            break;
        case 'error':
            errorState.classList.remove('hidden');
            break;
    }
}

/**
 * Validate JSON string
 */
function isValidJSON(str) {
    if (!str || str.trim() === '') return true; // Empty is valid (optional field)
    try {
        JSON.parse(str);
        return true;
    } catch (e) {
        return false;
    }
}

/**
 * Display error message
 */
function showError(message) {
    errorMessage.textContent = message;
    showState('error');
}

/**
 * Display success message
 */
function showSuccess(pdfUrl, filename) {
    successMessage.textContent = `Your architecture PDF "${filename}" is ready!`;
    downloadButton.href = `${API_BASE_URL}${pdfUrl}`;
    downloadButton.download = filename;
    showState('success');
}

/**
 * Handle form submission
 */
async function handleSubmit(event) {
    event.preventDefault();

    // Get form values
    const figmaLink = figmaLinkInput.value.trim();
    const figmaToken = figmaTokenInput.value.trim();
    const reportFile = reportFileInput.files[0];

    // Validate inputs
    if (!figmaLink) {
        showError('Please enter a Figma link');
        return;
    }

    if (!figmaToken) {
        showError('Please enter your Figma access token');
        return;
    }

    // Validate file size if provided (max 10MB)
    if (reportFile && reportFile.size > 10 * 1024 * 1024) {
        showError('File size too large. Please upload a file smaller than 10MB.');
        return;
    }

    // Prepare form data for file upload
    const formData = new FormData();
    formData.append('figma_link', figmaLink);
    formData.append('figma_token', figmaToken);
    if (reportFile) {
        formData.append('report_file', reportFile);
    }

    // Show loading state
    showState('loading');

    try {
        // Make API request with file upload
        const response = await fetch(`${API_BASE_URL}/api/generate-pdf`, {
            method: 'POST',
            body: formData  // No Content-Type header needed for FormData
        });

        const data = await response.json();

        if (!response.ok) {
            // Handle error response
            throw new Error(data.detail || `Server error: ${response.status}`);
        }

        if (data.success) {
            // Show success state
            showSuccess(data.pdf_url, data.pdf_filename);
        } else {
            throw new Error(data.message || 'PDF generation failed');
        }

    } catch (error) {
        console.error('Error generating PDF:', error);

        // Handle specific error types
        let errorMsg = 'An unexpected error occurred. Please try again.';

        if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError') || error.message.includes('CORS')) {
            let connectionError = 'Cannot connect to the backend server. Please ensure the server is running on http://localhost:8000';
            
            // Check if opened via file:// protocol (common CORS issue)
            if (window.location.protocol === 'file:') {
                connectionError += '\n\n⚠️ CORS Issue Detected:\n';
                connectionError += 'You opened the HTML file directly (file:// protocol).\n';
                connectionError += 'Browsers block cross-origin requests from local files.\n\n';
                connectionError += '✅ Solution:\n';
                connectionError += '1. Open a terminal in the frontend directory\n';
                connectionError += '2. Run: python -m http.server 3000\n';
                connectionError += '3. Open: http://localhost:3000 in your browser\n\n';
                connectionError += 'Or use VS Code Live Server extension.';
            } else {
                connectionError += '\n\nTroubleshooting:\n';
                connectionError += '1. Check if backend is running: cd backend && python main.py\n';
                connectionError += '2. Verify backend is accessible: http://localhost:8000/api/health\n';
                connectionError += '3. Check browser console for detailed errors';
            }
            
            errorMsg = connectionError;
        } else if (error.message.includes('429') || error.message.includes('Too Many Requests')) {
            errorMsg = 'Rate Limit Exceeded (429) - Too many requests to Figma API.\n\n' +
                      'Figma API Rate Limits:\n' +
                      '• Free tier: ~200 requests per minute\n' +
                      '• Paid tier: Higher limits\n\n' +
                      'What to do:\n' +
                      '1. Wait a few minutes before trying again\n' +
                      '2. Reduce the frequency of requests\n' +
                      '3. Consider upgrading your Figma plan for higher limits\n' +
                      '4. Check Figma API status: https://status.figma.com\n\n' +
                      'The system will show how long to wait if available.';
        } else if (error.message.includes('403') || error.message.includes('Forbidden')) {
            errorMsg = 'Access Forbidden (403) - Figma API rejected the request.\n\n' +
                      'Possible causes:\n' +
                      '1. Invalid or expired Figma access token\n' +
                      '2. Token doesn\'t have permission to access this file\n' +
                      '3. File is private/restricted and token lacks access\n' +
                      '4. Token format is incorrect (should start with "figd_")\n\n' +
                      'Solutions:\n' +
                      '• Verify your token at: https://www.figma.com/settings\n' +
                      '• Ensure the file is shared with your account\n' +
                      '• Generate a new token if the current one is expired\n' +
                      '• Check that you have access to the specific Figma file';
        } else if (error.message.includes('401') || error.message.includes('Unauthorized') || error.message.includes('access token')) {
            errorMsg = 'Authentication failed with Figma API. Please verify:\n\n1. Your Figma access token is correct\n2. The token has not expired\n3. You have access to the Figma file\n4. The file is not private/restricted';
        } else if (error.message.includes('400') || error.message.includes('Bad Request') || error.message.includes('Invalid Figma')) {
            errorMsg = 'Invalid Figma link format. Please check your URL.\n\nExpected format:\nhttps://www.figma.com/file/{key}/...\nor\nhttps://www.figma.com/design/{key}/...';
        } else if (error.message.includes('404')) {
            errorMsg = 'Figma file not found. Please check that the link is correct and the file exists.';
        } else if (error.message.includes('500')) {
            errorMsg = 'Server error occurred while generating PDF. Please check the backend logs for details.';
        } else if (error.message) {
            errorMsg = error.message;
        }

        showError(errorMsg);
    }
}

/**
 * Reset form and show initial state
 */
function resetForm() {
    pdfForm.reset();
    showState('form');
}

/**
 * Check backend connection on page load
 */
async function checkBackendConnection() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/health`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (response.ok) {
            const data = await response.json();
            console.log('✅ Backend connection successful:', data);
            return true;
        } else {
            console.error('❌ Backend health check failed:', response.status);
            return false;
        }
    } catch (error) {
        console.error('❌ Cannot connect to backend:', error);
        
        // Check if it's a CORS issue (file:// protocol)
        if (window.location.protocol === 'file:') {
            console.warn('⚠️ Frontend opened via file:// protocol. CORS restrictions may apply.');
            console.warn('💡 Solution: Serve the frontend using a web server:');
            console.warn('   cd frontend && python -m http.server 3000');
            console.warn('   Then open: http://localhost:3000');
        }
        
        return false;
    }
}

/**
 * Initialize event listeners
 */
async function init() {
    // Check backend connection first
    const isConnected = await checkBackendConnection();
    if (!isConnected) {
        console.warn('⚠️ Backend connection check failed. The server may not be running.');
        console.warn(`💡 Make sure the backend is running: cd backend && python main.py`);
        console.warn(`💡 Backend should be accessible at: ${API_BASE_URL}`);
    }

    // Form submission
    pdfForm.addEventListener('submit', handleSubmit);

    // Generate another button
    generateAnotherButton.addEventListener('click', resetForm);

    // Try again button
    tryAgainButton.addEventListener('click', () => showState('form'));

    // File upload validation
    reportFileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file && file.size > 10 * 1024 * 1024) {
            reportFileInput.style.borderColor = 'var(--accent-error)';
            console.warn('File size exceeds 10MB limit');
        } else {
            reportFileInput.style.borderColor = '';
        }
    });

    console.log('System Architecture Agent initialized');
    console.log(`API Base URL: ${API_BASE_URL}`);
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
