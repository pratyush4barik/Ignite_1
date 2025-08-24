from flask import Blueprint, jsonify, request, render_template
import pandas as pd
import os
import json
import uuid
import requests
from datetime import datetime
from app import db
from app.models import ChatSession, Alert

main_bp = Blueprint('main', __name__)

# Health Assistant Configuration
DISCLAIMER = "I can guide you with basic health information and suggest clinics from my database, but I am not a doctor. For medical treatment always consult a licensed healthcare provider."

# Department mapping for symptoms
SYMPTOM_DEPARTMENT_MAP = {
    'fever': 'General Physician',
    'cough': 'General Physician',
    'flu': 'General Physician',
    'cold': 'General Physician',
    'headache': 'General Physician',
    'chest pain': 'Cardiology',
    'breathing': 'Cardiology',
    'heart': 'Cardiology',
    'bone pain': 'Orthopedics',
    'fracture': 'Orthopedics',
    'joint': 'Orthopedics',
    'muscle': 'Orthopedics',
    'skin': 'Dermatology',
    'rash': 'Dermatology',
    'acne': 'Dermatology',
    'stomach': 'Gastroenterology',
    'digestion': 'Gastroenterology',
    'nausea': 'Gastroenterology',
    'diarrhea': 'Gastroenterology',
    'eye': 'Ophthalmology',
    'vision': 'Ophthalmology',
    'ear': 'ENT',
    'throat': 'ENT',
    'nose': 'ENT',
    'pregnancy': 'Gynecology',
    'period': 'Gynecology',
    'mental': 'Psychiatry',
    'depression': 'Psychiatry',
    'anxiety': 'Psychiatry'
}

# Emergency keywords
EMERGENCY_KEYWORDS = [
    'suicide', 'kill myself', 'self-harm', 'severe chest pain', 
    'difficulty breathing', 'can\'t breathe', 'choking', 'unconscious',
    'severe bleeding', 'overdose', 'poison', 'stroke', 'heart attack'
]

def load_clinic_data():
    """Load clinic data from CSV file"""
    try:
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'clinics.csv')
        if os.path.exists(csv_path):
            return pd.read_csv(csv_path)
        else:
            # Return empty DataFrame with expected columns if CSV doesn't exist
            return pd.DataFrame(columns=[
                'clinic_name', 'district', 'address', 'department', 
                'doctor_name', 'doctor_qualification', 'doctor_speciality', 
                'timings', 'contact_number'
            ])
    except Exception as e:
        print(f"Error loading clinic data: {e}")
        return pd.DataFrame()

def detect_emergency(message):
    """Detect emergency situations in user message"""
    message_lower = message.lower()
    for keyword in EMERGENCY_KEYWORDS:
        if keyword in message_lower:
            return True
    return False

def map_symptoms_to_department(symptoms):
    """Map symptoms to medical department"""
    symptoms_lower = symptoms.lower()
    for symptom, department in SYMPTOM_DEPARTMENT_MAP.items():
        if symptom in symptoms_lower:
            return department
    return 'General Physician'  # Default department

def search_clinics(district, department, limit=3):
    """Search clinics based on district and department"""
    df = load_clinic_data()
    if df.empty:
        return []
    
    # First try exact district match
    results = df[
        (df['district'].str.lower() == district.lower()) & 
        (df['department'].str.lower() == department.lower())
    ].head(limit)
    
    # If no results, try nearby districts (this is simplified - in real app you'd have geographic data)
    if results.empty:
        results = df[df['department'].str.lower() == department.lower()].head(limit)
    
    return results.to_dict('records')

def call_ai_api(message, conversation_history=[]):
    """Call AI API for general health questions"""
    api_provider = os.environ.get('AI_PROVIDER', 'openai').lower()
    
    # Prepare system prompt
    system_prompt = f"""You are a safe, concise health assistant chatbot. You are NOT a doctor.

IMPORTANT RULES:
- Always show this disclaimer first: "{DISCLAIMER}"
- Provide only general health information and lifestyle advice
- Never prescribe medicine or treatment
- Keep responses short and professional
- If asked about specific medical conditions, always recommend consulting a licensed healthcare provider
- Focus on: hydration, nutrition, sleep, exercise, stress management
- Be empathetic but cautious"""

    try:
        if api_provider == 'openai':
            return call_openai_api(message, system_prompt, conversation_history)
        elif api_provider == 'gemini':
            return call_gemini_api(message, system_prompt, conversation_history)
        elif api_provider == 'mgx':
            return call_mgx_api(message, system_prompt, conversation_history)
        else:
            return "I'm sorry, I don't have access to AI services right now. Please consult a licensed healthcare provider for medical advice."
    except Exception as e:
        print(f"AI API Error: {e}")
        return "I'm sorry, I'm having trouble accessing my knowledge base right now. Please consult a licensed healthcare provider for medical advice."

def call_openai_api(message, system_prompt, conversation_history):
    """Call OpenAI API"""
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        return "AI service is not configured. Please consult a licensed healthcare provider."
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add conversation history
    for msg in conversation_history[-6:]:  # Last 6 messages for context
        messages.append(msg)
    
    messages.append({"role": "user", "content": message})
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": messages,
        "max_tokens": 300,
        "temperature": 0.7
    }
    
    response = requests.post('https://api.openai.com/v1/chat/completions', 
                           headers=headers, json=data, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    else:
        raise Exception(f"OpenAI API error: {response.status_code}")

def call_gemini_api(message, system_prompt, conversation_history):
    """Call Gemini API"""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return "AI service is not configured. Please consult a licensed healthcare provider."
    
    # Build conversation history in Gemini's expected format
    contents = []
    
    # Add system instructions (Gemini doesn’t have "system" role, so prepend as user content)
    contents.append({
        "role": "user",
        "parts": [{"text": system_prompt}]
    })
    
    # Add history
    for msg in conversation_history[-6:]:
        role = "user" if msg["role"] == "user" else "model"
        contents.append({
            "role": role,
            "parts": [{"text": msg["content"]}]
        })
    
    # Add latest user input
    contents.append({
        "role": "user",
        "parts": [{"text": message}]
    })
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": contents,
        "generationConfig": {
            "maxOutputTokens": 300,
            "temperature": 0.7
        }
    }
    
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    response = requests.post(url, headers=headers, json=data, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text'].strip()
    else:
        raise Exception(f"Gemini API error: {response.status_code} - {response.text}")

def call_mgx_api(message, system_prompt, conversation_history):
    """Call MGX API"""
    api_key = os.environ.get('MGX_API_KEY')
    if not api_key:
        return "AI service is not configured. Please consult a licensed healthcare provider."
    
    # Implement MGX API call here based on their documentation
    # This is a placeholder - you'll need to update with actual MGX endpoint and format
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    data = {
        "prompt": f"{system_prompt}\n\nUser: {message}",
        "max_tokens": 300,
        "temperature": 0.7
    }
    
    # Replace with actual MGX endpoint
    response = requests.post('https://api.mgx.com/v1/chat', 
                           headers=headers, json=data, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        # Adjust based on MGX response format
        return result.get('response', 'Sorry, I could not process your request.')
    else:
        raise Exception(f"MGX API error: {response.status_code}")

@main_bp.route('/')
def index():
    """Serve the main chat interface"""
    return render_template('index.html')

@main_bp.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

@main_bp.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        # Load or create session
        session = ChatSession.query.filter_by(session_id=session_id).first()
        if not session:
            session = ChatSession(session_id=session_id, user_data='{}')
            db.session.add(session)
        
        # Parse session data
        try:
            session_data = json.loads(session.user_data) if session.user_data else {}
        except:
            session_data = {}
        
        conversation_history = session_data.get('conversation', [])
        user_info = session_data.get('user_info', {})

        # Check for emergency
        if detect_emergency(message):
            emergency_response = (
                "⚠️ Emergency detected. Please call emergency services (Dial 108 in India "
                "or your local emergency number) and visit the nearest hospital immediately."
            )
            # Log emergency alert
            alert = Alert(
                session_id=session_id,
                alert_type='emergency',
                message=f"Emergency detected in message: {message}"
            )
            db.session.add(alert)

            conversation_history.append({"role": "user", "content": message})
            conversation_history.append({"role": "assistant", "content": emergency_response})

            session_data['conversation'] = conversation_history
            session.user_data = json.dumps(session_data)
            session.updated_at = datetime.utcnow()
            db.session.commit()

            return jsonify({
                "response": emergency_response,
                "session_id": session_id,
                "type": "emergency"
            })

        # --- Clinic search logic ---
        is_clinic_request = any(keyword in message.lower() for keyword in ['clinic', 'hospital', 'doctor', 'appointment', 'find'])
        message_lower = message.lower()
        
        # Extract district from message if user provides it
        if 'district' in message_lower or 'area' in message_lower or 'location' in message_lower:
            words = message.split()
            for i, word in enumerate(words):
                if word.lower() in ['district', 'area', 'location'] and i + 1 < len(words):
                    user_info['district'] = words[i + 1].title()
                    break

        # If clinic request and district known, fetch all clinics in that district
        if is_clinic_request and 'district' in user_info:
            district = user_info['district']
            df = load_clinic_data()
            clinics = df[df['district'].str.lower() == district.lower()].to_dict('records')

            if clinics:
                response = f"Here are all healthcare providers in {district}:\n\n"
                for i, clinic in enumerate(clinics, 1):
                    response += f"{i}. **{clinic.get('clinic_name', 'N/A')}**\n"
                    response += f"   📍 {clinic.get('district', 'N/A')} - {clinic.get('address', 'N/A')}\n"
                    response += f"   🏥 Department: {clinic.get('department', 'N/A')}\n"
                    response += f"   👨‍⚕️ Dr. {clinic.get('doctor_name', 'N/A')} ({clinic.get('doctor_qualification', 'N/A')})\n"
                    response += f"   🩺 Speciality: {clinic.get('doctor_speciality', 'N/A')}\n"
                    response += f"   🕒 Timings: {clinic.get('timings', 'N/A')}\n"
                    response += f"   📞 Contact: {clinic.get('contact_number', 'N/A')}\n\n"
                response += "Please contact the clinic directly to book an appointment."
            else:
                response = f"No clinic information is available for {district}. Please check local directories."
        elif is_clinic_request:
            # District not provided yet
            response = "Please tell me which district you are located in so I can find nearby clinics."
        else:
            # General health question - use AI
            response = call_ai_api(message, conversation_history)

        # Update conversation history
        conversation_history.append({"role": "user", "content": message})
        conversation_history.append({"role": "assistant", "content": response})

        # Keep only last 20 messages to manage memory
        if len(conversation_history) > 20:
            conversation_history = conversation_history[-20:]

        # Update session
        session_data['conversation'] = conversation_history
        session_data['user_info'] = user_info
        session.user_data = json.dumps(session_data)
        session.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            "response": response,
            "session_id": session_id,
            "type": "normal"
        })
    
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({"error": "An error occurred processing your request"}), 500


@main_bp.route('/admin/alerts')
def admin_alerts():
    """Admin endpoint to view emergency alerts"""
    try:
        alerts = Alert.query.order_by(Alert.created_at.desc()).limit(50).all()
        alerts_data = []
        
        for alert in alerts:
            alerts_data.append({
                'id': alert.id,
                'session_id': alert.session_id,
                'alert_type': alert.alert_type,
                'message': alert.message,
                'created_at': alert.created_at.isoformat()
            })
        
        return jsonify({"alerts": alerts_data})
        
    except Exception as e:
        print(f"Admin alerts error: {e}")
        return jsonify({"error": "Error fetching alerts"}), 500