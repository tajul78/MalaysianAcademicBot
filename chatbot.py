import os
import logging
from datetime import datetime
from flask import Blueprint, render_template, jsonify
import google.generativeai as genai
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.chains.question_answering import load_qa_chain
from langchain_core.documents import Document

# ✅ Configure Gemini API with environment variable
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ✅ Initialize Gemini model
model = genai.GenerativeModel("gemini-1.5-pro", generation_config={
    "temperature": 0.7,
    "top_p": 1,
    "max_output_tokens": 512
})

# ✅ Flask Blueprint
dashboard_bp = Blueprint('dashboard', __name__)

# ✅ Persona Prompt
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
2. Use vivid examples from Malaysian startups (e.g., "I remember when StoreHub first raised funding...")
3. Be concise (under 70 words) but impactful.
4. Offer *culturally relevant*, *actionable* steps — e.g., where to apply, whom to speak to.
5. When appropriate, add light motivational closing lines like “You can do this, insyaAllah.”

## 🧭 Context Awareness:
Ground advice in Malaysian context as much as possible.

## 💡 Tone:
Empathetic big-sister energy + seasoned professor. You’re smart, but approachable.
"""

# ✅ Load vector store from FAISS (assumes built already)
embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
vectorstore = FAISS.load_local("faiss_index", embedding, allow_dangerous_deserialization=True)
qa_chain = load_qa_chain(llm=model, chain_type="stuff")

# ✅ In-memory store for chat history
conversation_history = {}

# ✅ Main AI response with RAG

def get_ai_response(user_message, phone_number):
    try:
        # Init chat history
        if phone_number not in conversation_history:
            conversation_history[phone_number] = []

        # Store user input
        conversation_history[phone_number].append({"role": "user", "content": user_message})

        # Retrieve docs from vector store
        related_docs = vectorstore.similarity_search(user_message, k=3)

        # Combine retrieved context
        doc_context = "\n\n".join([doc.page_content for doc in related_docs])

        # Final prompt to Gemini
        prompt = f"""
{MALAYSIAN_ENTREPRENEUR_PROMPT}

[📄 Context from trusted sources:]
{doc_context}

[🧑‍🎓 Question:]
{user_message}
"""

        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        logging.error(f"Error generating RAG response: {str(e)}")
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
            'last_updated': datetime.now().isoformat()
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
