import os
import logging
from datetime import datetime, timedelta
from collections import deque
from flask import Blueprint, render_template, jsonify
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize Gemini model with reduced parameters
model = genai.GenerativeModel("gemini-1.5-flash", generation_config={
    "temperature": 0.7,
    "top_p": 1,
    "max_output_tokens": 256  # Reduced from 512
})

# Flask Blueprint
dashboard_bp = Blueprint('dashboard', __name__)

# Economic Expert Persona Prompt (Shortened)
MALAYSIAN_ECONOMIC_EXPERT_PROMPT = """
You are Dr. Siti Rahman — a leading Malaysian economist and policy advisor with 15+ years of experience.

## Professional Background:
- Senior Economic Advisor at MIER
- PhD in Development Economics from University of Cambridge
- Former World Bank researcher (Southeast Asia)

## Expertise:
- Productivity Growth & Manufacturing Efficiency
- Economic Policy & Structural Reforms
- Malaysian Development Planning (ETP, GTP, NTP)
- ASEAN Integration & Regional Economics

## Response Style:
- Authoritative yet accessible
- Data-driven with Malaysian context
- Solution-oriented business insights
- Keep responses under 80 words

Connect business advice to broader economic trends and Malaysian policy framework.
"""

# Memory-efficient conversation storage
MAX_CONVERSATIONS = 50  # Limit total conversations
MAX_MESSAGES_PER_CONVERSATION = 10  # Limit messages per chat
conversation_history = {}
conversation_timestamps = {}

# Lazy loading variables (load only when needed)
embeddings = None
vectorstore = None
_embeddings_loaded = False

def cleanup_old_conversations():
    """Remove old conversations to free memory"""
    global conversation_history, conversation_timestamps
    
    current_time = datetime.now()
    cutoff_time = current_time - timedelta(hours=24)  # Keep only last 24 hours
    
    # Remove old conversations
    to_remove = []
    for phone, timestamp in conversation_timestamps.items():
        if timestamp < cutoff_time:
            to_remove.append(phone)
    
    for phone in to_remove:
        conversation_history.pop(phone, None)
        conversation_timestamps.pop(phone, None)
    
    # Limit total conversations
    if len(conversation_history) > MAX_CONVERSATIONS:
        # Remove oldest conversations
        sorted_conversations = sorted(conversation_timestamps.items(), key=lambda x: x[1])
        oldest_to_remove = sorted_conversations[:len(conversation_history) - MAX_CONVERSATIONS]
        
        for phone, _ in oldest_to_remove:
            conversation_history.pop(phone, None)
            conversation_timestamps.pop(phone, None)

def get_limited_context(phone_number):
    """Get limited conversation context to save memory"""
    if phone_number not in conversation_history:
        conversation_history[phone_number] = deque(maxlen=MAX_MESSAGES_PER_CONVERSATION)
        conversation_timestamps[phone_number] = datetime.now()
    
    # Return only last few messages for context
    recent_messages = list(conversation_history[phone_number])[-3:]  # Last 3 messages only
    return recent_messages

def load_embeddings_if_needed():
    """Lazy load embeddings only when actually needed"""
    global embeddings, vectorstore, _embeddings_loaded
    
    if _embeddings_loaded:
        return vectorstore is not None
    
    try:
        # Use lighter embedding model
        from sentence_transformers import SentenceTransformer
        embeddings = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
        
        if os.path.exists("faiss_index"):
            from langchain_community.vectorstores import FAISS
            from langchain_community.embeddings import HuggingFaceEmbeddings
            
            hf_embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            vectorstore = FAISS.load_local("faiss_index", hf_embeddings, allow_dangerous_deserialization=True)
            logging.info("✅ FAISS vectorstore loaded successfully")
        else:
            logging.warning("⚠️ FAISS index not found. Using basic responses.")
            vectorstore = None
            
        _embeddings_loaded = True
        return vectorstore is not None
        
    except Exception as e:
        logging.error(f"❌ Error loading embeddings: {e}")
        _embeddings_loaded = True
        vectorstore = None
        return False

def get_minimal_rag_context(user_message, max_docs=2):
    """Get minimal RAG context to reduce memory usage"""
    if not load_embeddings_if_needed() or not vectorstore:
        return ""
    
    try:
        # Get fewer, more relevant documents
        related_docs = vectorstore.similarity_search(user_message, k=max_docs)
        
        # Keep only essential content
        context_parts = []
        for doc in related_docs:
            content = doc.page_content.strip()
            # Truncate long documents
            if len(content) > 200:
                content = content[:200] + "..."
            context_parts.append(content)
        
        return "\n".join(context_parts)
        
    except Exception as e:
        logging.error(f"Error in RAG retrieval: {e}")
        return ""

def get_ai_response(user_message, phone_number):
    """Generate AI response with memory optimization"""
    try:
        # Cleanup old conversations periodically
        if len(conversation_history) > 30:  # Trigger cleanup
            cleanup_old_conversations()
        
        # Get limited context
        recent_context = get_limited_context(phone_number)
        
        # Add user message
        conversation_history[phone_number].append({"role": "user", "content": user_message})
        conversation_timestamps[phone_number] = datetime.now()
        
        # Get minimal RAG context (only for economic queries)
        doc_context = ""
        economic_keywords = ['economic', 'economy', 'productivity', 'growth', 'policy', 'malaysia', 'business']
        
        if any(keyword in user_message.lower() for keyword in economic_keywords):
            doc_context = get_minimal_rag_context(user_message, max_docs=1)  # Only 1 doc
        
        # Build minimal prompt
        if doc_context:
            prompt = f"""
{MALAYSIAN_ECONOMIC_EXPERT_PROMPT}

Context: {doc_context}

Question: {user_message}

Provide a focused economic analysis (max 80 words):
"""
        else:
            prompt = f"""
{MALAYSIAN_ECONOMIC_EXPERT_PROMPT}

Question: {user_message}

Provide expert economic advice (max 80 words):
"""

        # Get response from Gemini
        response = model.generate_content(prompt)
        ai_response = response.text.strip()
        
        # Ensure response isn't too long
        if len(ai_response) > 500:
            ai_response = ai_response[:500] + "..."

        # Store AI response
        conversation_history[phone_number].append({"role": "assistant", "content": ai_response})
        
        return ai_response

    except Exception as e:
        logging.error(f"Error generating AI response: {str(e)}")
        return "Maaf, I'm experiencing technical difficulties. Please try again shortly."

@dashboard_bp.route('/')
def dashboard():
    return render_template('dashboard.html')

@dashboard_bp.route('/api/stats')
def get_stats():
    try:
        # Cleanup before calculating stats
        cleanup_old_conversations()
        
        total_conversations = len(conversation_history)
        total_messages = sum(len(conv) for conv in conversation_history.values())
        
        return jsonify({
            'status': 'active',
            'total_conversations': total_conversations,
            'total_messages': total_messages,
            'last_updated': datetime.now().isoformat(),
            'rag_enabled': vectorstore is not None,
            'persona': 'Economic Expert',
            'memory_optimized': True
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
                # Get last message safely
                last_message = ""
                if len(history) > 0:
                    last_user_messages = [msg for msg in history if msg["role"] == "user"]
                    if last_user_messages:
                        last_message = last_user_messages[-1]["content"][:50] + "..." if len(last_user_messages[-1]["content"]) > 50 else last_user_messages[-1]["content"]
                
                masked_phone = phone[:3] + "*" * (len(phone) - 6) + phone[-3:] if len(phone) > 6 else phone[:2] + "***"
                recent_conversations.append({
                    'phone': masked_phone,
                    'last_message': last_message,
                    'message_count': len(history),
                    'last_message_time': conversation_timestamps.get(phone, datetime.now()).isoformat()
                })
        
        # Return only most recent 10 conversations
        recent_conversations.sort(key=lambda x: x['last_message_time'], reverse=True)
        return jsonify(recent_conversations[:10])
        
    except Exception as e:
        logging.error(f"Error getting conversations: {str(e)}")
        return jsonify({'error': 'Failed to get conversations'}), 500

# Memory cleanup route (optional - for manual cleanup)
@dashboard_bp.route('/api/cleanup')
def manual_cleanup():
    try:
        cleanup_old_conversations()
        return jsonify({'status': 'cleaned', 'remaining_conversations': len(conversation_history)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
