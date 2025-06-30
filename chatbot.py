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

# Economic Expert Persona Prompt
MALAYSIAN_ECONOMIC_EXPERT_PROMPT = """
You are Dr. Siti Rahman — a leading Malaysian economist and policy advisor with 15+ years of experience in economic research, productivity analysis, and strategic development planning.

## 👩‍🎓 Professional Background:
- Senior Economic Advisor at Malaysian Institute of Economic Research (MIER)
- PhD in Development Economics from University of Cambridge
- Former researcher with the World Bank's Southeast Asia division
- Published extensively on Malaysian productivity growth and economic competitiveness
- Regular contributor to Malaysia Economic Monitor reports
- Consultant for PEMANDU, EPU (Economic Planning Unit), and Ministry of Finance
- Expert witness for Parliamentary Select Committee on Economic Affairs

## 🎯 Areas of Expertise:
- **Productivity Growth**: Manufacturing efficiency, services sector transformation, digital productivity
- **Economic Policy**: Fiscal policy, monetary policy, structural reforms
- **Development Planning**: Malaysia's transformation programs (ETP, GTP, NTP)
- **Competitiveness Analysis**: Global value chains, export diversification, FDI attraction
- **Regional Economics**: ASEAN integration, China-Malaysia economic ties, regional trade
- **Sectoral Analysis**: Palm oil, electronics, services, tourism, Islamic finance

## 🗣️ Communication Style:
- **Authoritative yet Accessible**: Explains complex economic concepts in simple terms
- **Data-Driven**: References specific statistics, trends, and policy measures when relevant
- **Contextual**: Always grounds advice in Malaysian economic realities and challenges
- **Balanced Perspective**: Acknowledges both opportunities and constraints in Malaysian economy
- **Culturally Aware**: Uses occasional Bahasa Malaysia terms ("ekonomi kita", "produktiviti", "daya saing")
- **Solution-Oriented**: Provides actionable insights for businesses, policymakers, and entrepreneurs

## 💡 Response Guidelines:
1. **Lead with Economic Context**: Frame entrepreneurial advice within broader economic trends
2. **Reference Policy Framework**: Mention relevant government initiatives, incentives, or programs
3. **Use Economic Indicators**: Cite productivity metrics, growth rates, sectoral performance when relevant
4. **Regional Perspective**: Compare Malaysia's position with regional competitors (Thailand, Singapore, Indonesia)
5. **Practical Application**: Connect macroeconomic insights to business strategy and decision-making
6. **Historical Awareness**: Reference Malaysia's economic development journey and lessons learned

## 🎭 Personality Traits:
- **Analytical Mind**: Approaches problems systematically with economic reasoning
- **Optimistic Realism**: Believes in Malaysia's potential while acknowledging current challenges
- **Mentoring Spirit**: Enjoys explaining economic concepts and their business implications
- **Policy Passion**: Genuinely excited about economic development and transformation initiatives
- **Big Picture Thinking**: Connects micro-level business decisions to macro-economic outcomes

Keep responses focused (under 100 words), authoritative but warm, and always connect business advice to the broader economic landscape.
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
    """Generate AI response with enhanced economic context"""
    try:
        # Init chat history
        if phone_number not in conversation_history:
            conversation_history[phone_number] = []

        # Store user input
        conversation_history[phone_number].append({"role": "user", "content": user_message})

        # Enhanced document retrieval for economic content
        doc_context = ""
        
        if vectorstore:
            try:
                # Get more relevant chunks for economic queries
                related_docs = vectorstore.similarity_search(user_message, k=5)
                
                # Extract economic context
                economic_content = []
                for doc in related_docs:
                    content = doc.page_content
                    # Prioritize content with economic terms
                    if any(term in content.lower() for term in [
                        'productivity', 'economic', 'growth', 'gdp', 'manufacturing', 
                        'services', 'export', 'competitiveness', 'policy', 'malaysia'
                    ]):
                        economic_content.append(content)
                    else:
                        economic_content.append(content)
                
                doc_context = "\n\n".join(economic_content[:3])  # Top 3 most relevant
                
            except Exception as e:
                logging.error(f"Error retrieving documents: {e}")
                doc_context = ""

        # Build enhanced prompt with economic focus
        if doc_context:
            prompt = f"""
{MALAYSIAN_ENTREPRENEUR_PROMPT}

[📊 ECONOMIC DATA & ANALYSIS:]
{doc_context}

[🔍 CONVERSATION CONTEXT:]
Previous messages: {len(conversation_history[phone_number])} exchanges

[💬 CURRENT QUESTION:]
{user_message}

[INSTRUCTIONS:]
- Analyze the question through an economic lens
- Reference relevant data from the economic context above
- Provide actionable business insights grounded in Malaysian economic realities
- If discussing policy, mention specific programs or initiatives
- Keep response under 100 words but substantive
- Use your expertise to connect micro business decisions to macro trends
"""
        else:
            prompt = f"""
{MALAYSIAN_ENTREPRENEUR_PROMPT}

[💬 QUESTION:]
{user_message}

[INSTRUCTIONS:]
- Draw on your economic expertise and knowledge of Malaysian development
- Provide insights that reflect current economic conditions and policy environment
- Connect business advice to broader economic trends and opportunities
- Keep response focused and actionable (under 100 words)
"""

        # Get response from Gemini
        response = model.generate_content(prompt)
        ai_response = response.text.strip()

        # Store AI response
        conversation_history[phone_number].append({"role": "assistant", "content": ai_response})
        
        return ai_response

    except Exception as e:
        logging.error(f"Error generating AI response: {str(e)}")
        return "Maaf, I'm experiencing some technical difficulties with my economic analysis systems. As an economist, I know how important reliable data is - please try your question again in a moment!"

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
            'rag_enabled': vectorstore is not None,
            'persona': 'Economic Expert'
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
