<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Malaysian Economic Expert Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #f8f9fb;
            font-family: 'Segoe UI', sans-serif;
            color: #333;
        }
        
        .card {
            border: none;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            margin-bottom: 1.5rem;
        }
        
        .dashboard-header {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
        }
        
        .dashboard-title {
            font-size: 2rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        
        .stat-card {
            text-align: center;
            padding: 1.5rem;
        }
        
        .stat-icon {
            font-size: 2rem;
            color: #667eea;
            margin-bottom: 0.5rem;
        }
        
        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 0.25rem;
        }
        
        .stat-label {
            color: #6c757d;
            font-size: 0.9rem;
            font-weight: 500;
        }
        
        .section-title {
            font-size: 1.25rem;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 1rem;
        }
        
        .conversation-item {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 0.75rem;
            border-left: 3px solid #667eea;
        }
        
        .conversation-phone {
            font-weight: 600;
            color: #2c3e50;
        }
        
        .conversation-meta {
            color: #6c757d;
            font-size: 0.85rem;
        }
        
        .status-item {
            display: flex;
            align-items: center;
            padding: 0.75rem 0;
            border-bottom: 1px solid #e9ecef;
        }
        
        .status-item:last-child {
            border-bottom: none;
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #28a745;
            margin-right: 0.75rem;
        }
        
        .btn-refresh {
            background: #667eea;
            border: none;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 6px;
        }
        
        .btn-refresh:hover {
            background: #5a6fd8;
            color: white;
        }
        
        .persona-list {
            list-style: none;
            padding: 0;
        }
        
        .persona-list li {
            padding: 0.5rem 0;
            padding-left: 1.25rem;
            position: relative;
        }
        
        .persona-list li::before {
            content: '•';
            position: absolute;
            left: 0;
            color: #667eea;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container py-4">
        <!-- Header -->
        <div class="dashboard-header">
            <h1 class="dashboard-title">📊 Malaysian Economic Expert Dashboard</h1>
            <p class="mb-0">Monitoring <strong>Dr. Siti Rahman</strong> – Your Malaysian Economic Expert Assistant</p>
        </div>

        <!-- Statistics Cards -->
        <div class="row g-3 mb-4">
            <div class="col-md-4">
                <div class="card stat-card">
                    <div class="stat-icon">💬</div>
                    <div class="stat-value" id="total-conversations">–</div>
                    <div class="stat-label">Total Conversations</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card stat-card">
                    <div class="stat-icon">📧</div>
                    <div class="stat-value" id="total-messages">–</div>
                    <div class="stat-label">Messages Processed</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card stat-card">
                    <div class="stat-icon">🕒</div>
                    <div class="stat-value" id="last-updated">–</div>
                    <div class="stat-label">Last Updated</div>
                </div>
            </div>
        </div>

        <!-- Bot Persona -->
        <div class="card p-4">
            <h5 class="section-title">👩‍🎓 Bot Persona: Dr. Siti Rahman</h5>
            <div class="row">
                <div class="col-md-6">
                    <h6>Professional Background</h6>
                    <ul class="persona-list">
                        <li>Senior Economic Advisor at Malaysian Institute of Economic Research (MIER)</li>
                        <li>PhD in Development Economics from University of Cambridge</li>
                        <li>Former researcher with World Bank's Southeast Asia division</li>
                        <li>15+ years experience in economic research and policy advisory</li>
                    </ul>
                </div>
                <div class="col-md-6">
                    <h6>Areas of Expertise</h6>
                    <ul class="persona-list">
                        <li>Productivity Growth & Manufacturing Efficiency</li>
                        <li>Economic Policy & Structural Reforms</li>
                        <li>Malaysian Development Planning (ETP, GTP, NTP)</li>
                        <li>ASEAN Integration & Regional Economics</li>
                        <li>Islamic Finance & Sectoral Analysis</li>
                    </ul>
                </div>
            </div>
        </div>

        <!-- Recent Conversations -->
        <div class="card p-4">
            <h5 class="section-title">💬 Recent Conversations</h5>
            <div id="conversation-list">
                <div class="text-muted">Loading...</div>
            </div>
            <button class="btn btn-refresh mt-3" onclick="loadConversations()">🔄 Refresh</button>
        </div>

        <!-- Configuration Status -->
        <div class="card p-4">
            <h5 class="section-title">⚙️ Configuration Status</h5>
            <div class="status-item">
                <div class="status-dot"></div>
                <div>
                    <strong>Gemini Integration</strong><br>
                    <small class="text-muted">Gemini-Pro model configured and active</small>
                </div>
            </div>
            <div class="status-item">
                <div class="status-dot"></div>
                <div>
                    <strong>Twilio WhatsApp</strong><br>
                    <small class="text-muted">Webhook endpoint active</small>
                </div>
            </div>
        </div>
    </div>

    <script>
        async function loadStats() {
            try {
                // Replace with actual API endpoint
                // const res = await fetch('/api/stats');
                // const data = await res.json();
                
                // Mock data for demo
                const data = {
                    total_conversations: 142,
                    total_messages: 1247,
                    last_updated: new Date().toISOString()
                };
                
                document.getElementById('total-conversations').textContent = data.total_conversations;
                document.getElementById('total-messages').textContent = data.total_messages;
                document.getElementById('last-updated').textContent = new Date(data.last_updated).toLocaleTimeString('en-MY', {
                    hour: '2-digit',
                    minute: '2-digit'
                });
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }

        async function loadConversations() {
            const container = document.getElementById('conversation-list');
            container.innerHTML = '<div class="text-muted">Loading...</div>';
            
            try {
                // Replace with actual API endpoint
                // const res = await fetch('/api/conversations');
                // const data = await res.json();
                
                // Mock data for demo
                const data = [
                    {
                        phone: '+60123456789',
                        message_count: 12,
                        last_message: 'What are your thoughts on Malaysia\'s productivity growth in manufacturing?'
                    },
                    {
                        phone: '+60198765432',
                        message_count: 8,
                        last_message: 'Could you explain the Economic Transformation Programme impact on SMEs?'
                    },
                    {
                        phone: '+60147258369',
                        message_count: 15,
                        last_message: 'How does Malaysia compare with other ASEAN countries economically?'
                    }
                ];
                
                container.innerHTML = '';
                
                if (data.length === 0) {
                    container.innerHTML = '<div class="text-muted">No recent conversations found.</div>';
                } else {
                    data.forEach(conv => {
                        const div = document.createElement('div');
                        div.className = 'conversation-item';
                        div.innerHTML = `
                            <div class="conversation-phone">${conv.phone}</div>
                            <div class="conversation-meta">${conv.message_count} messages</div>
                            <div class="mt-1"><em>"${conv.last_message}"</em></div>
                        `;
                        container.appendChild(div);
                    });
                }
            } catch (error) {
                console.error('Error loading conversations:', error);
                container.innerHTML = '<div class="text-muted">Error loading conversations.</div>';
            }
        }

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            loadStats();
            loadConversations();
        });
    </script>
</body>
</html>
