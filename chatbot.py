import os
import logging
from datetime import datetime
from flask import Blueprint, render_template, jsonify
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize Gemini model
model = genai.GenerativeModel("gemini-1.5-pro", generation_config={
    "temperature": 0.7,
    "top_p": 1,
    "max_output_tokens": 512
})

# Flask Blueprint
dashboard_bp = Blueprint('dashboard', __name__)

# Persona Prompt
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
- Drops occasional Bahasa Malaysia terms (e.g., "boleh lah", "sikit", "jangan risau")
- Reflective tone: connects advice with personal lessons and past experience
- Mix of academic insight and real-world practicality

## 🗣️ Answer Style Guidelines:
1. Responses should feel personal and empathetic — like speaking to a mentee over coffee.
2. Use vivid examples from Malaysian startups (e.g., "I remember when StoreHub first raised funding...")
3. Be concise (under 70 words) but impactful.
4. Offer *culturally relevant*, *actionable* steps — e.g., where to apply, whom to speak to.
5. When appropriate, add light motivational closing lines like "You can do this, insyaAllah."

## 🧭 Context Awareness:
Ground advice in Malaysian context as much as possible.

## 💡 Tone:
Empathetic big-sister energy + seasoned professor. You're smart, but approachable.
"""

# Initialize embeddings and vectorstore
embeddings = None
vectorstore = None

try:
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    if os.path.exists("faiss_index"):
        vectorstore = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        logging.info("✅ FAISS vectorstore loaded successfully")
    else:
        logging.warning("⚠️ FAISS index not found. RAG features disabled.")
except Exception as e:
    logging.error(f"❌ Error loading vectorstore: {e}")
    vectorstore = None

# In-memory store for chat history
conversation_history = {}

def get_ai_response(user_message, phone_number):
    """Generate AI response with optional RAG"""
    try:
        # Init chat history
        if phone_number not in conversation_history:
            conversation_history[phone_number] = []

        # Store user input
        conversation_history[phone_number].append({"role": "user", "content": user_message})

        # Try to get relevant context from vectorstore
        doc_context = ""
        if vectorstore:
            try:
                related_docs = vectorstore.similarity_search(user_message, k=3)
                doc_context = "\n\n".join([doc.page_content for doc in related_docs])
            except Exception as e:
                logging.error(f"Error retrieving documents: {e}")
                doc_context = ""

        # Build prompt
        if doc_context:
            prompt = f"""
{MALAYSIAN_ENTREPRENEUR_PROMPT}

[📄 Context from trusted sources:]
{doc_context}

[🧑‍🎓 Question:]
{user_message}
"""
        else:
            prompt = f"""
{MALAYSIAN_ENTREPRENEUR_PROMPT}

[🧑‍🎓 Question:]
{user_message}
"""

        # Get response from Gemini
        response = model.generate_content(prompt)
        ai_response = response.text.strip()

        # Store AI response
        conversation_history[phone_number].append({"role": "assistant", "content": ai_response})
        
        return ai_response

    except Exception as e:
        logging.error(f"Error generating AI response: {str(e)}")
        return "Maaf, sistem AI sedang menghadapi masalah teknikal. Sila cuba sebentar lagi."

@dashboard_bp.route('/')
def dashboard():
    return render_template('dashboard.html')

@dashboard_bp.route('/api/stats')
def get_stats():
    try:
        total_conversations = len(conversation_history)
        total_messages = sum(len(conv) for conv in conversation_history.values())
        return jsonify({
            'status': 'active',
            'total_conversations': total_conversations,
            'total_messages': total_messages,
            'last_updated': datetime.now().isoformat(),
            'rag_enabled': vectorstore is not None
        })
    except Exception as e:
        logging.error(f"Error getting stats: {str(e)}")
        return jsonify({'error': 'Failed to get statistics'}), 500

@dashboard_bp.route('/api/conversations')
def get_conversations():
    try:
        recent_conversations = []
        for phone, history in conversation_history.items():
            if history:
                masked_phone = phone[:3] + "*" * (len(phone) - 6) + phone[-3:] if len(phone) > 6 else phone[:2] + "***"
                recent_conversations.append({
                    'phone': masked_phone,
                    'last_message_time': datetime.now().isoformat(),
                    'message_count': len(history)
                })
        return jsonify(recent_conversations[-10:])
    except Exception as e:
        logging.error(f"Error getting conversations: {str(e)}")
        return jsonify({'error': 'Failed to get conversations'}), 500