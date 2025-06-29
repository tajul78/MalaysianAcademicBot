import os
import logging
from datetime import datetime
from flask import Blueprint, render_template, jsonify
import google.generativeai as genai

# ✅ Configure Gemini API with environment variable
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ✅ Initialize Gemini model (text-only)
model = genai.GenerativeModel("gemini-pro")

# ✅ Flask Blueprint
dashboard_bp = Blueprint('dashboard', __name__)

# ✅ Persona Prompt (embed as first system message if needed)
MALAYSIAN_ENTREPRENEUR_PROMPT = """You are Dr. Siti Rahman, a Malaysian academic entrepreneur with over 15 years of experience in both academia and business. 
You are a Professor of Innovation Management at Universiti Malaya and founder of three successful tech startups in Malaysia.

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

# ✅ In-memory store for conversation history
conversation_history = {}

# ✅ Main AI response function using Gemini
def get_ai_response(user_message, phone_number):
    try:
        # Init history
        if phone_number not in conversation_history:
            conversation_history[phone_number] = []

        # Add user input
        conversation_history[phone_number].append({"role": "user", "content": user_message})

        # Build prompt parts in Gemini format
        parts = [{"role": "user", "parts": [MALAYSIAN_ENTREPRENEUR_PROMPT]}]  # Persona prompt as context
        parts += [{"role": "user", "parts": [msg["content"]]} for msg in conversation_history[phone_number]]

        # Get Gemini response
        response = model.generate_content(parts)
        return response.text.strip()

    except Exception as e:
        logging.error(f"Error generating Gemini AI response: {str(e)}")
        return "Maaf, sistem AI sedang menghadapi masalah teknikal. Sila cuba sebentar lagi."

# ✅ Basic dashboard route
@dashboard_bp.route('/')
def dashboard():
    return render_template('dashboard.html')

# ✅ Statistics API
@dashboard_bp.route('/api/stats')
def get_stats():
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

# ✅ Recent conversations API
@dashboard_bp.route('/api/conversations')
def get_conversations():
    try:
        recent_conversations = []
        for phone, history in conversation_history.items():
            if history:
                masked_phone = phone[:3] + "*" * (len(phone) - 6) + phone[-3:]
                recent_conversations.append({
                    'phone': masked_phone,
                    'last_message_time': datetime.now().isoformat(),
                    'message_count': len(history)
                })
        return jsonify(recent_conversations[-10:])
    except Exception as e:
        logging.error(f"Error getting conversations: {str(e)}")
        return jsonify({'error': 'Failed to get conversations'}), 500

 
