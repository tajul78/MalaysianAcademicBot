// Dashboard JavaScript for WhatsApp Chatbot

let refreshInterval;

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    setWebhookUrl();
    startAutoRefresh();
});

function initializeDashboard() {
    console.log('Initializing WhatsApp Chatbot Dashboard');
    refreshData();
}

function setWebhookUrl() {
    // Set the webhook URL based on current domain
    const webhookUrl = `${window.location.protocol}//${window.location.host}/webhook/whatsapp`;
    document.getElementById('webhook-url').textContent = webhookUrl;
}

async function refreshData() {
    try {
        // Show loading state
        updateLoadingState(true);
        
        // Fetch statistics
        await fetchStats();
        
        // Fetch conversations
        await fetchConversations();
        
        console.log('Dashboard data refreshed successfully');
    } catch (error) {
        console.error('Error refreshing dashboard data:', error);
        showError('Failed to refresh dashboard data');
    } finally {
        updateLoadingState(false);
    }
}

async function fetchStats() {
    try {
        const response = await fetch('/api/stats');
        if (!response.ok) throw new Error('Failed to fetch stats');
        
        const stats = await response.json();
        updateStatsDisplay(stats);
    } catch (error) {
        console.error('Error fetching stats:', error);
        // Set default values on error
        updateStatsDisplay({
            total_conversations: 0,
            total_messages: 0,
            last_updated: new Date().toISOString()
        });
    }
}

async function fetchConversations() {
    try {
        const response = await fetch('/api/conversations');
        if (!response.ok) throw new Error('Failed to fetch conversations');
        
        const conversations = await response.json();
        updateConversationsDisplay(conversations);
    } catch (error) {
        console.error('Error fetching conversations:', error);
        showConversationsError();
    }
}

function updateStatsDisplay(stats) {
    document.getElementById('total-conversations').textContent = stats.total_conversations || 0;
    document.getElementById('total-messages').textContent = stats.total_messages || 0;
    
    // Format last updated time
    if (stats.last_updated) {
        const lastUpdated = new Date(stats.last_updated);
        const timeAgo = getTimeAgo(lastUpdated);
        document.getElementById('last-updated').textContent = timeAgo;
    }
}

function updateConversationsDisplay(conversations) {
    const conversationsContainer = document.getElementById('conversations-list');
    
    if (!conversations || conversations.length === 0) {
        conversationsContainer.innerHTML = `
            <div class="text-center text-muted py-4">
                <i class="fas fa-comments fa-2x mb-3 opacity-50"></i>
                <p>No conversations yet</p>
                <small>WhatsApp messages will appear here once users start chatting</small>
            </div>
        `;
        return;
    }
    
    conversationsContainer.innerHTML = conversations.map(conv => `
        <div class="conversation-item">
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    <h6 class="mb-1">
                        <i class="fab fa-whatsapp me-2 text-success"></i>
                        ${conv.phone}
                    </h6>
                    <p class="text-muted mb-1 small">
                        ${conv.message_count} message${conv.message_count !== 1 ? 's' : ''} exchanged
                    </p>
                </div>
                <small class="text-muted">
                    ${getTimeAgo(new Date(conv.last_message_time))}
                </small>
            </div>
        </div>
    `).join('');
}

function showConversationsError() {
    const conversationsContainer = document.getElementById('conversations-list');
    conversationsContainer.innerHTML = `
        <div class="text-center text-danger py-4">
            <i class="fas fa-exclamation-triangle fa-2x mb-3"></i>
            <p>Error loading conversations</p>
            <button class="btn btn-sm btn-outline-danger" onclick="fetchConversations()">
                <i class="fas fa-retry me-1"></i>
                Try Again
            </button>
        </div>
    `;
}

function updateLoadingState(isLoading) {
    const refreshButton = document.querySelector('button[onclick="refreshData()"]');
    const icon = refreshButton.querySelector('i');
    
    if (isLoading) {
        icon.className = 'fas fa-spinner fa-spin me-1';
        refreshButton.disabled = true;
    } else {
        icon.className = 'fas fa-refresh me-1';
        refreshButton.disabled = false;
    }
}

function showError(message) {
    // Simple error notification (could be enhanced with toast notifications)
    console.error(message);
    
    // Update status badge to show error
    const statusBadge = document.getElementById('status-badge');
    statusBadge.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Error';
    statusBadge.className = 'badge bg-danger';
    
    // Reset after 5 seconds
    setTimeout(() => {
        statusBadge.innerHTML = '<i class="fas fa-circle"></i> Active';
        statusBadge.className = 'badge bg-success';
    }, 5000);
}

function getTimeAgo(date) {
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) {
        return 'Just now';
    } else if (diffInSeconds < 3600) {
        const minutes = Math.floor(diffInSeconds / 60);
        return `${minutes} minute${minutes !== 1 ? 's' : ''} ago`;
    } else if (diffInSeconds < 86400) {
        const hours = Math.floor(diffInSeconds / 3600);
        return `${hours} hour${hours !== 1 ? 's' : ''} ago`;
    } else {
        const days = Math.floor(diffInSeconds / 86400);
        return `${days} day${days !== 1 ? 's' : ''} ago`;
    }
}

function startAutoRefresh() {
    // Refresh data every 30 seconds
    refreshInterval = setInterval(refreshData, 30000);
}

function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
}

// Clean up when page is about to unload
window.addEventListener('beforeunload', function() {
    stopAutoRefresh();
});

// Handle visibility change to pause/resume auto-refresh
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        stopAutoRefresh();
    } else {
        startAutoRefresh();
    }
});
