import os
import google.generativeai as genai
import traceback
import logging
from datetime import datetime
from flask import Blueprint, render_template, jsonify


# Initialize OpenAI client
dashboard_bp = Blueprint('dashboard', __name__)

# Malaysian Academic Entrepreneur System Prompt
MALAYSIAN_ENTREPRENEUR_PROMPT = """You are Dr. Siti Rahman, a Malaysian academic entrepreneur with over 15 years of experience in both academia and business. You are a Professor of Innovation Management at Universiti Malaya and founder of three successful tech startups in Malaysia.

Your background:
- PhD in Business Innovation from University of Cambridge
- Former researcher at Malaysian Institute of Economic Research (MIER)
- Founder of successful fintech and edtech companies in Malaysia
- Expert in Southeast Asian markets, Islamic finance, and digital transformation
- Fluent in English, Bahasa Malaysia, and Mandarin
- Deep understanding of Malaysian business culture, government policies (like MSC status, grants from MDEC, MIDA incentives)
- Experience with Malaysian startup ecosystem including MaGIC, Cradle Fund, and various accelerators

Your personality:
- Warm, approachable, and encouraging
- Uses occasional Bahasa Malaysia terms naturally (like "boleh", "sikit", "lah")
- Practical and data-driven advice
- Culturally sensitive to Malaysian diversity
- Passionate about education and entrepreneurship
- Enjoys mentoring young entrepreneurs

When responding:
- Provide practical, actionable advice
- Reference Malaysian context when relevant (regulations, funding, market conditions)
- Use a warm, professional tone with occasional casual Malaysian expressions
- Draw from both academic research and real-world business experience
- Be encouraging but realistic about challenges
- When appropriate, mention relevant Malaysian resources, organizations, or programs

Keep responses conversational, helpful, and under 200 words unless detailed explanation is specifically requested."""

# Store for conversation history (in production, use a proper database)
conversation_history = {}

def get_ai_response(user_message, phone_number):
    try:
        # Initialize conversation history if needed
        if phone_number not in conversation_history:
            conversation_history[phone_number] = []

        # Append user message
        conversation_history[phone_number].append({"role": "user", "parts": [user_message]})

        # Trim history to last 10
        if len(conversation_history[phone_number]) > 10:
            conversation_history[phone_number] = conversation_history[phone_number][-10:]

        # Create Gemini model and chat session
        model = genai.GenerativeModel("gemini-pro")
        chat = model.start_chat(history=conversation_history[phone_number])

        # Send user message
        gemini_response = chat.send_message(user_message)

        # Append bot reply to history
        conversation_history[phone_number].append({"role": "model", "parts": [gemini_response.text]})

        return gemini_response.text

    except Exception as e:
        logging.error(f"Error generating Gemini AI response: {str(e)}")
        return "Maaf, sistem AI sedang menghadapi masalah teknikal. Sila cuba sebentar lagi."
        
@dashboard_bp.route('/')
def dashboard():
    """Simple dashboard to monitor chatbot activity"""
    return render_template('dashboard.html')

@dashboard_bp.route('/api/stats')
def get_stats():
    """API endpoint to get chatbot statistics"""
    try:
        total_conversations = len(conversation_history)
        total_messages = sum(len(conv) for conv in conversation_history.values())
        
        return jsonify({
            'status': 'active',
            'total_conversations': total_conversations,
            'total_messages': total_messages,
            'last_updated': datetime.now().isoformat()
        })
    except Exception as e:
        logging.error(f"Error getting stats: {str(e)}")
        return jsonify({'error': 'Failed to get statistics'}), 500

@dashboard_bp.route('/api/conversations')
def get_conversations():
    """API endpoint to get recent conversations (last message only for privacy)"""
    try:
        recent_conversations = []
        for phone, history in conversation_history.items():
            if history:
                # Only show last message timestamp and phone (masked for privacy)
                masked_phone = phone[:3] + "*" * (len(phone) - 6) + phone[-3:]
                recent_conversations.append({
                    'phone': masked_phone,
                    'last_message_time': datetime.now().isoformat(),  # In production, store actual timestamps
                    'message_count': len(history)
                })
        
        return jsonify(recent_conversations[-10:])  # Last 10 conversations
    except Exception as e:
        logging.error(f"Error getting conversations: {str(e)}")
        return jsonify({'error': 'Failed to get conversations'}), 500
