import os
import logging
from flask import Blueprint, request, Response
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from chatbot import get_ai_response

webhook_bp = Blueprint('webhook', __name__)

# Twilio configuration
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER")

# Initialize Twilio client
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
else:
    twilio_client = None
    logging.warning("Twilio credentials not found in environment variables")

@webhook_bp.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """Handle incoming WhatsApp messages from Twilio"""
    try:
        # Get the incoming message details
        incoming_msg = request.values.get('Body', '').strip()
        from_number = request.values.get('From', '')
        to_number = request.values.get('To', '')
        
        logging.info(f"Received message from {from_number}: {incoming_msg}")
        
        # Validate the message
        if not incoming_msg:
            logging.warning("Empty message received")
            return Response("", status=200)
        
        # Extract phone number (remove whatsapp: prefix if present)
        clean_phone = from_number.replace('whatsapp:', '').replace('+', '')
        
        # Get AI response
        ai_response = get_ai_response(incoming_msg, clean_phone)
        
        # Create TwiML response
        resp = MessagingResponse()
        resp.message(ai_response)
        
        logging.info(f"Sent response to {from_number}: {ai_response[:50]}...")
        
        return Response(str(resp), mimetype='text/xml')
        
    except Exception as e:
        logging.error(f"Error processing webhook: {str(e)}")
        
        # Send error response
        resp = MessagingResponse()
        resp.message("Sorry, I encountered an error. Please try again later.")
        return Response(str(resp), mimetype='text/xml')

@webhook_bp.route('/webhook/status', methods=['POST'])
def message_status():
    """Handle message status updates from Twilio"""
    try:
        message_sid = request.values.get('MessageSid')
        message_status = request.values.get('MessageStatus')
        
        logging.info(f"Message {message_sid} status: {message_status}")
        
        return Response("", status=200)
        
    except Exception as e:
        logging.error(f"Error processing status webhook: {str(e)}")
        return Response("", status=200)

@webhook_bp.route('/test', methods=['GET'])
def test_endpoint():
    """Test endpoint to verify the webhook is working"""
    return {
        'status': 'success',
        'message': 'WhatsApp chatbot webhook is running',
        'twilio_configured': TWILIO_ACCOUNT_SID is not None,
        'openai_configured': os.environ.get("OPENAI_API_KEY") is not None
    }

def send_whatsapp_message(to_phone_number: str, message: str) -> bool:
    """Send a WhatsApp message using Twilio (for testing or proactive messaging)"""
    try:
        if not twilio_client:
            logging.error("Twilio client not initialized")
            return False
            
        # Ensure phone number has whatsapp: prefix
        if not to_phone_number.startswith('whatsapp:'):
            to_phone_number = f'whatsapp:{to_phone_number}'
            
        message = twilio_client.messages.create(
            body=message,
            from_=f'whatsapp:{TWILIO_PHONE_NUMBER}',
            to=to_phone_number
        )
        
        logging.info(f"Message sent with SID: {message.sid}")
        return True
        
    except Exception as e:
        logging.error(f"Error sending WhatsApp message: {str(e)}")
        return False
