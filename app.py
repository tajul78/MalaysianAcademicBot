import os
import google.generativeai as genai
import logging
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Set up logging
logging.basicConfig(level=logging.DEBUG)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Import and register blueprints/routes
from webhook import webhook_bp
from chatbot import dashboard_bp

app.register_blueprint(webhook_bp)
app.register_blueprint(dashboard_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
