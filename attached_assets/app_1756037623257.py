import os
from app import create_app, db
from flask import render_template

app = create_app()

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/')
def signin():
    return render_template('signin.html')
@app.route('/')
def signup():
    return render_template('signup.html')
@app.route('/')
def forgot():
    return render_template('forgot-password.html')
@app.route('/')
def bot():
    return render_template('bot.html')

import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

# -------------------------
# Flask App Initialization
# -------------------------
app = Flask(__name__)

# Example DB configuration (adjust as needed)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chatbot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# -------------------------
# Database Models
# -------------------------
class ChatSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    user_data = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

# -------------------------
# HTML Routes
# -------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signin")
def signin():
    return render_template("signin.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/forgot-password")
def forgot_password():
    return render_template("forgot-password.html")

# -------------------------
# Simple Chat Endpoint
# -------------------------
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"response": "Please enter your message."})

    # For now, echo back the message
    response_message = f"You said: {user_message}"

    return jsonify({
        "response": response_message
    })

# -------------------------
# Main App Runner
# -------------------------
if __name__ == '__main__':
    with app.app_context():
        # Create database tables
        db.create_all()
        print("✅ Database tables created successfully!")

    # Run the application
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.environ.get('PORT', 8081))

    print(f"🏥 Health Assistant Chatbot starting...")
    print(f"📱 Access the application at: http://localhost:{port}")
    print(f"🔧 Debug mode: {debug_mode}")

    app.run(host='0.0.0.0', port=port, debug=debug_mode, threaded=True)
