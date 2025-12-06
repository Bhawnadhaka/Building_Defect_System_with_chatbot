// ===================================
// Building Defect Detection System
// Advanced JavaScript with AJAX & Animations
// ===================================

// Global variables
let currentSessionId = null;
let includeImageContext = true;
let lastAnalysisResult = null;
let defectChart = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    loadChatHistory();
});

// Initialize application
function initializeApp() {
    console.log('🚀 Initializing DefectAI System...');
    
    // Set up drag and drop for single image
    const uploadZone = document.getElementById('uploadZone');
    if (uploadZone) {
        setupDragAndDrop(uploadZone, handleImageUpload);
    }
    
    // Set up drag and drop for batch upload
    const batchUploadZone = document.getElementById('batchUploadZone');
    if (batchUploadZone) {
        setupDragAndDrop(batchUploadZone, handleBatchUpload);
    }
    
    // Theme toggle
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
    
    console.log('✅ Application initialized');
}

// Set up event listeners
function setupEventListeners() {
    // Image input
    const imageInput = document.getElementById('imageInput');
    if (imageInput) {
        imageInput.addEventListener('change', (e) => handleImageUpload(e.target.files));
    }
    
    // Batch image input
    const batchImageInput = document.getElementById('batchImageInput');
    if (batchImageInput) {
        batchImageInput.addEventListener('change', (e) => handleBatchUpload(e.target.files));
    }
    
    // Theme toggle
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    
    // Chat input enter key
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
    }
}

// Drag and drop setup
function setupDragAndDrop(element, callback) {
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        element.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        element.addEventListener(eventName, () => {
            element.classList.add('dragover');
        }, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        element.addEventListener(eventName, () => {
            element.classList.remove('dragover');
        }, false);
    });
    
    element.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        callback(files);
    }, false);
}

// Handle single image upload and analysis
async function handleImageUpload(files) {
    if (!files || files.length === 0) return;
    
    const file = files[0];
    
    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/bmp'];
    if (!allowedTypes.includes(file.type)) {
        showNotification('Invalid file type. Please upload JPG, PNG, WEBP, or BMP.', 'error');
        return;
    }
    
    // Validate file size (16MB max)
    if (file.size > 16 * 1024 * 1024) {
        showNotification('File too large. Maximum size is 16MB.', 'error');
        return;
    }
    
    // Show loading overlay
    showLoading(true);
    
    // Prepare form data
    const formData = new FormData();
    formData.append('image', file);
    
    try {
        // Send to backend
        const response = await fetch('/api/analyze', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        if (result.error) {
            throw new Error(result.error);
        }
        
        // Store result
        lastAnalysisResult = result;
        
        // Display results
        displayAnalysisResults(result);
        
        // Show notification
        showNotification('Analysis complete! 🎉', 'success');
        
        // Scroll to results
        document.getElementById('resultsContainer').scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        console.error('Analysis error:', error);
        showNotification(`Error: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

// Display analysis results
function displayAnalysisResults(result) {
    const resultsContainer = document.getElementById('resultsContainer');
    resultsContainer.style.display = 'block';
    
    // Original image
    const originalImage = document.getElementById('originalImage');
    originalImage.src = result.image_data;
    
    // Heatmap (if available)
    const heatmapImage = document.getElementById('heatmapImage');
    if (result.heatmap_data) {
        heatmapImage.src = result.heatmap_data;
    } else {
        heatmapImage.src = result.image_data;
    }
    
    // Prediction
    const predictionLabel = document.getElementById('predictionLabel');
    const predictionIcon = document.getElementById('predictionIcon');
    const confidenceText = document.getElementById('confidenceText');
    const confidenceFill = document.getElementById('confidenceFill');
    
    predictionLabel.textContent = result.prediction || 'Unknown';
    confidenceText.textContent = `Confidence: ${result.confidence.toFixed(1)}%`;
    confidenceFill.style.width = `${result.confidence}%`;
    
    // Set icon based on defect
    if (result.defect_info) {
        predictionIcon.textContent = result.defect_info.icon;
        
        // Update defect info
        document.getElementById('severityValue').textContent = result.defect_info.severity;
        document.getElementById('costValue').textContent = result.defect_info.avg_cost;
        document.getElementById('repairTimeValue').textContent = result.defect_info.repair_time;
        document.getElementById('urgencyValue').textContent = result.defect_info.urgency;
        document.getElementById('defectDescription').textContent = result.defect_info.description;
        
        document.getElementById('defectInfo').style.display = 'block';
        
        // Color code severity
        const mainPrediction = document.getElementById('mainPrediction');
        mainPrediction.style.background = `linear-gradient(135deg, ${result.defect_info.color} 0%, ${adjustColor(result.defect_info.color, 20)} 100%)`;
    }
    
    // Top predictions
    if (result.top_predictions) {
        displayTopPredictions(result.top_predictions);
    }
}

// Display top predictions
function displayTopPredictions(predictions) {
    const container = document.getElementById('topPredictions');
    container.innerHTML = '<h3 style="margin-bottom: 1rem;">Top Predictions</h3>';
    
    predictions.forEach((pred, index) => {
        const item = document.createElement('div');
        item.className = 'prediction-item';
        item.style.animationDelay = `${index * 0.1}s`;
        
        item.innerHTML = `
            <div>
                <span class="prediction-name">#${index + 1} ${pred.class}</span>
            </div>
            <span class="prediction-confidence">${pred.confidence.toFixed(1)}%</span>
        `;
        
        container.appendChild(item);
    });
}

// Handle batch upload
async function handleBatchUpload(files) {
    if (!files || files.length === 0) return;
    
    showLoading(true);
    
    const formData = new FormData();
    Array.from(files).forEach(file => {
        formData.append('images', file);
    });
    
    try {
        const response = await fetch('/api/batch-analyze', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        displayBatchResults(data);
        showNotification(`Analyzed ${data.results.length} images successfully! 🎉`, 'success');
        
    } catch (error) {
        console.error('Batch analysis error:', error);
        showNotification(`Error: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

// Display batch results
function displayBatchResults(data) {
    const batchResults = document.getElementById('batchResults');
    batchResults.style.display = 'block';
    
    // Update summary
    document.getElementById('totalImages').textContent = data.summary.total_images;
    document.getElementById('highSeverity').textContent = data.summary.high_severity_count;
    document.getElementById('totalCost').textContent = data.summary.total_cost_range;
    document.getElementById('uniqueDefects').textContent = Object.keys(data.summary.defect_distribution).length;
    
    // Create defect distribution chart
    createDefectChart(data.summary.defect_distribution);
    
    // Display individual results
    const itemsContainer = document.getElementById('batchItemsContainer');
    itemsContainer.innerHTML = '';
    
    data.results.forEach((result, index) => {
        const item = document.createElement('div');
        item.className = 'result-card';
        item.style.animationDelay = `${index * 0.05}s`;
        
        const defectInfo = result.defect_info || {};
        
        item.innerHTML = `
            <div class="card-header">
                <h3>${defectInfo.icon || '📷'} ${result.filename}</h3>
            </div>
            <div style="padding: 1rem;">
                <div style="margin-bottom: 0.5rem;">
                    <strong>Defect:</strong> ${result.prediction}
                </div>
                <div style="margin-bottom: 0.5rem;">
                    <strong>Confidence:</strong> ${result.confidence.toFixed(1)}%
                </div>
                <div style="margin-bottom: 0.5rem;">
                    <strong>Severity:</strong> 
                    <span style="color: ${defectInfo.color || '#666'}; font-weight: 600;">
                        ${defectInfo.severity || 'Unknown'}
                    </span>
                </div>
                <div style="margin-bottom: 0.5rem;">
                    <strong>Est. Cost:</strong> ${defectInfo.avg_cost || 'N/A'}
                </div>
            </div>
        `;
        
        itemsContainer.appendChild(item);
    });
    
    // Scroll to results
    batchResults.scrollIntoView({ behavior: 'smooth' });
}

// Create defect distribution chart
function createDefectChart(distribution) {
    const canvas = document.getElementById('defectChart');
    const ctx = canvas.getContext('2d');
    
    // Destroy existing chart
    if (defectChart) {
        defectChart.destroy();
    }
    
    const labels = Object.keys(distribution);
    const data = Object.values(distribution);
    const colors = [
        '#2563eb', '#0891b2', '#8b5cf6', '#10b981',
        '#f59e0b', '#ef4444', '#06b6d4'
    ];
    
    defectChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        font: {
                            size: 14,
                            family: 'Inter'
                        }
                    }
                },
                title: {
                    display: true,
                    text: 'Defect Distribution',
                    font: {
                        size: 18,
                        weight: 'bold',
                        family: 'Inter'
                    }
                }
            }
        }
    });
}

// Chat functionality
async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Clear input
    input.value = '';
    
    // Add user message to chat
    addMessageToChat(message, 'user');
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                image_context: includeImageContext
            })
        });
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Add bot response to chat
        addMessageToChat(data.response, 'bot');
        
    } catch (error) {
        console.error('Chat error:', error);
        addMessageToChat(`Sorry, I encountered an error: ${error.message}`, 'bot');
    }
}

// Send quick message
function sendQuickMessage(message) {
    const input = document.getElementById('chatInput');
    input.value = message;
    sendMessage();
}

// Add message to chat
function addMessageToChat(content, role) {
    const chatMessages = document.getElementById('chatMessages');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${role}`;
    
    const icon = role === 'bot' ? '<i class="fas fa-robot"></i>' : '<i class="fas fa-user"></i>';
    
    messageDiv.innerHTML = `
        <div class="message-avatar">
            ${icon}
        </div>
        <div class="message-content">
            <p>${content}</p>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Load chat history
async function loadChatHistory() {
    try {
        const response = await fetch('/api/sessions');
        const data = await response.json();
        
        if (data.sessions && data.sessions.length > 0) {
            updateSessionList(data.sessions);
        }
    } catch (error) {
        console.error('Error loading chat history:', error);
    }
}

// Update session list
function updateSessionList(sessions) {
    const sessionList = document.getElementById('sessionList');
    
    sessions.forEach(session => {
        const item = document.createElement('div');
        item.className = 'session-item';
        item.onclick = () => loadSession(session.session_id);
        
        const date = new Date(session.created);
        const timeStr = date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
        
        item.innerHTML = `
            <i class="fas fa-comment"></i>
            <div>
                <span class="session-title">Session ${session.session_id}</span>
                <span class="session-time">${timeStr}</span>
            </div>
        `;
        
        sessionList.appendChild(item);
    });
}

// Load specific session
async function loadSession(sessionId) {
    try {
        const response = await fetch(`/api/history?session_id=${sessionId}`);
        const data = await response.json();
        
        if (data.messages) {
            const chatMessages = document.getElementById('chatMessages');
            chatMessages.innerHTML = '';
            
            data.messages.forEach(msg => {
                addMessageToChat(msg.content, msg.role === 'assistant' ? 'bot' : msg.role);
            });
        }
    } catch (error) {
        console.error('Error loading session:', error);
    }
}

// Create new chat session
function createNewSession() {
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.innerHTML = `
        <div class="chat-message bot">
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <p>Hello! I'm your AI assistant for building defect analysis. Upload an image to get started, or ask me anything about building maintenance, repair costs, and defect severity.</p>
            </div>
        </div>
    `;
}

// Toggle image context
function toggleImageContext() {
    includeImageContext = !includeImageContext;
    const btn = event.target.closest('.feature-btn');
    btn.style.color = includeImageContext ? 'var(--primary)' : 'var(--gray-500)';
    showNotification(`Image context ${includeImageContext ? 'enabled' : 'disabled'}`, 'info');
}

// Clear chat
function clearChat() {
    if (confirm('Are you sure you want to clear the chat?')) {
        createNewSession();
        showNotification('Chat cleared', 'info');
    }
}

// Theme toggle
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

// Update theme icon
function updateThemeIcon(theme) {
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.innerHTML = theme === 'light' 
            ? '<i class="fas fa-moon"></i>' 
            : '<i class="fas fa-sun"></i>';
    }
}

// Show/hide loading overlay
function showLoading(show) {
    const overlay = document.getElementById('loadingOverlay');
    overlay.style.display = show ? 'flex' : 'none';
}

// Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${getNotificationColor(type)};
        color: white;
        border-radius: 0.75rem;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
        max-width: 400px;
    `;
    
    const icon = getNotificationIcon(type);
    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.75rem;">
            <i class="${icon}" style="font-size: 1.5rem;"></i>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 4 seconds
    setTimeout(() => {
        notification.style.animation = 'fadeOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}

// Get notification color
function getNotificationColor(type) {
    const colors = {
        success: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
        error: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
        warning: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
        info: 'linear-gradient(135deg, #06b6d4 0%, #0891b2 100%)'
    };
    return colors[type] || colors.info;
}

// Get notification icon
function getNotificationIcon(type) {
    const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };
    return icons[type] || icons.info;
}

// Scroll to section
function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth' });
    }
}

// Adjust color brightness
function adjustColor(color, percent) {
    const num = parseInt(color.replace('#', ''), 16);
    const amt = Math.round(2.55 * percent);
    const R = (num >> 16) + amt;
    const G = (num >> 8 & 0x00FF) + amt;
    const B = (num & 0x0000FF) + amt;
    
    return '#' + (
        0x1000000 +
        (R < 255 ? (R < 1 ? 0 : R) : 255) * 0x10000 +
        (G < 255 ? (G < 1 ? 0 : G) : 255) * 0x100 +
        (B < 255 ? (B < 1 ? 0 : B) : 255)
    ).toString(16).slice(1);
}

// Add fadeOut animation
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeOut {
        to {
            opacity: 0;
            transform: translateX(20px);
        }
    }
`;
document.head.appendChild(style);

console.log('✅ DefectAI JavaScript loaded successfully');
