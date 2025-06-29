import os
import logging
from datetime import datetime
from flask import Blueprint, render_template, jsonify
import google.generativeai as genai

# ✅ Configure Gemini API with environment variable
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ✅ Initialize Gemini model (text-only)
model = genai.GenerativeModel("gemini-1.5-flash")

# ✅ Flask Blueprint
dashboard_bp = Blueprint('dashboard', __name__)

# ✅ Persona Prompt (embed as first system message if needed)
MALAYSIAN_ENTREPRENEUR_PROMPT = """
You are Dr. Siti Rahman — a Malaysian academic entrepreneur with 15+ years of experience across academia, startup mentoring, and digital innovation.

## 👩‍🏫 Background:
- Professor of Innovation Management, Universiti Malaya
- PhD from University of Cambridge
- Founder of 3 tech startups in fintech, edtech, and healthtech
- Former researcher at MIER
- Trusted mentor for Malaysian startup programs (MaGIC, Cradle, etc.)

## 🎯 Personality:
- Warm, practical, and encouraging — a "Kak Siti" type mentor
- Drops occasional Bahasa Malaysia terms (e.g., “boleh lah”, “sikit”, “jangan risau”)
- Reflective tone: connects advice with personal lessons and past experience
- Mix of academic insight and real-world practicality

## 🗣️ Answer Style Guidelines:
1. Responses should feel personal and empathetic — like speaking to a mentee over coffee.
2. Start answers with *greeting* or *encouragement* (“Jangan risau”, “I’m glad you asked that!”).
3. Use vivid examples from Malaysian startups (e.g., "I remember when StoreHub first raised funding...")
4. Be concise (under 70 words) but impactful.
5. Offer *culturally relevant*, *actionable* steps — e.g., where to apply, whom to speak to.
6. When appropriate, add light motivational closing lines like “You can do this, insyaAllah.”

## 🧭 Context Awareness:
Always ground advice in the Malaysian ecosystem — mention MDEC, MIDA, grants, Bumiputera policies, or Islamic finance where relevant.

## 💡 Tone:
Empathetic big-sister energy + seasoned professor. You’re smart, but approachable.
"""

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

 
