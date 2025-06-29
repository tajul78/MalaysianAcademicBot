# WhatsApp Malaysian Entrepreneur Chatbot

## Overview

This is a Flask-based WhatsApp chatbot application that provides entrepreneurial advice through the persona of Dr. Siti Rahman, a Malaysian academic entrepreneur. The system integrates with Twilio for WhatsApp messaging and OpenAI GPT-4 for intelligent responses, offering culturally-aware business guidance to users in Malaysia.

## System Architecture

The application follows a modular Flask architecture with clear separation of concerns:

- **Flask Web Application**: Core application framework with blueprint-based routing
- **Webhook Handler**: Processes incoming WhatsApp messages via Twilio
- **AI Chatbot Engine**: Generates contextual responses using OpenAI GPT-4
- **Dashboard Interface**: Web-based monitoring and management interface
- **Static Assets**: CSS and JavaScript for frontend functionality

## Key Components

### Backend Components

1. **app.py**: Main Flask application entry point
   - Configures Flask app with security middleware
   - Registers blueprints for modular functionality
   - Sets up session management and proxy handling

2. **webhook.py**: Twilio WhatsApp integration
   - Handles incoming webhook requests from Twilio
   - Processes WhatsApp messages and generates TwiML responses
   - Manages phone number formatting and validation

3. **chatbot.py**: AI conversation engine
   - Implements Malaysian entrepreneur persona (Dr. Siti Rahman)
   - Manages conversation history per user
   - Integrates with OpenAI GPT-4 for response generation

### Frontend Components

4. **templates/dashboard.html**: Web dashboard interface
   - Bootstrap-based responsive design with dark theme
   - Real-time status monitoring and statistics display
   - Conversation history and management interface

5. **static/**: CSS and JavaScript assets
   - Custom styling for dashboard components
   - Interactive JavaScript for real-time updates
   - Responsive design elements

## Data Flow

1. **Incoming Message Flow**:
   - WhatsApp user sends message → Twilio → `/webhook/whatsapp` endpoint
   - Webhook extracts message content and sender information
   - Message passed to AI chatbot engine with conversation context
   - OpenAI generates culturally-aware response as Dr. Siti Rahman
   - Response sent back via TwiML to Twilio → WhatsApp user

2. **Dashboard Flow**:
   - Web interface loads at root endpoint
   - JavaScript fetches real-time statistics and conversation data
   - Auto-refresh mechanism updates dashboard every few seconds
   - Webhook URL displayed for Twilio configuration

## External Dependencies

### Required Services
- **Twilio**: WhatsApp Business API integration
  - Account SID, Auth Token, and Phone Number required
  - Webhook endpoint must be configured in Twilio console

- **OpenAI**: GPT-4 API for conversation generation
  - API key required for accessing language model
  - Conversation history maintained for context

### Python Packages
- **Flask**: Web framework and routing
- **Twilio**: WhatsApp messaging and TwiML generation
- **OpenAI**: AI response generation
- **Werkzeug**: WSGI utilities and proxy handling

### Frontend Dependencies
- **Bootstrap**: UI framework with dark theme
- **Font Awesome**: Icon library for dashboard elements

## Deployment Strategy

The application is designed for cloud deployment with the following considerations:

### Environment Configuration
- Session secret key for security
- Twilio credentials (SID, Auth Token, Phone Number)
- OpenAI API key
- Debug mode controlled via environment

### Hosting Requirements
- Python 3.x runtime environment
- HTTPS endpoint for Twilio webhook security
- Persistent storage for conversation history (currently in-memory)

### Scaling Considerations
- Conversation history stored in memory (should migrate to database for production)
- Stateless design allows for horizontal scaling
- Rate limiting may be needed for OpenAI API calls

## Changelog

```
Changelog:
- June 29, 2025. Initial setup
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
```

### Production Recommendations

1. **Database Integration**: Replace in-memory conversation storage with persistent database (PostgreSQL recommended)
2. **Rate Limiting**: Implement API rate limiting for OpenAI calls
3. **Monitoring**: Add logging and error tracking for production monitoring
4. **Security**: Implement Twilio signature validation for webhook security
5. **Caching**: Add Redis for conversation history and response caching