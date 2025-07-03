from flask import Flask, request, jsonify, send_from_directory
from routes.register import register_bp
from routes.verify import verify_bp
from routes.delete import delete_bp
import os
import json
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)
print("AES_KEY Loaded:", os.environ.get("AES_KEY"))

# Create Flask app
app = Flask(__name__, static_folder='static')

# Register modular route blueprints
app.register_blueprint(register_bp)
app.register_blueprint(verify_bp)
app.register_blueprint(delete_bp)

@app.route("/")
def index():
    return "BioAuth backend running with QR login"

# File path for storing QR session data
SESSIONS_FILE = Path(__file__).resolve().parent / 'sessions.json'

def read_sessions():
    if not SESSIONS_FILE.exists():
        return {}
    try:
        with open(SESSIONS_FILE, 'r') as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception as e:
        print(f"Error reading sessions.json: {e}")
        return {}

def write_sessions(data):
    try:
        with open(SESSIONS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error writing sessions.json: {e}")

# Serve static login pages
@app.route('/web_login.html')
def serve_qr_page():
    return send_from_directory(app.static_folder, 'web_login.html')

@app.route('/result.html')
def serve_result_page():
    return send_from_directory(app.static_folder, 'result.html')

# Create a new QR login session
@app.route('/api/create-session', methods=['POST'])
def create_session():
    data = request.get_json()
    session_id = data.get('sessionId')
    if not session_id:
        return jsonify({ 'error': 'Missing sessionId' }), 400

    sessions = read_sessions()
    sessions[session_id] = { 'verified': False, 'did': None }
    write_sessions(sessions)
    return jsonify({ 'message': 'Session created' })

# Check QR session status
@app.route('/api/session-status/<session_id>')
def session_status(session_id):
    sessions = read_sessions()
    if not isinstance(sessions, dict):
        return jsonify({ 'verified': False })

    session = sessions.get(session_id)
    if not session:
        return jsonify({ 'verified': False })
    
    return jsonify({
        'verified': session['verified'],
        'did': session['did']
    })

# Confirm session from mobile device
@app.route('/api/confirm-session', methods=['POST'])
def confirm_session():
    data = request.get_json()
    if not data:
        return jsonify({ 'error': 'Missing JSON payload' }), 400

    session_id = data.get('sessionId')
    did = data.get('did')

    if not session_id or not did:
        return jsonify({ 'error': 'Missing sessionId or DID' }), 400

    sessions = read_sessions()
    if session_id in sessions:
        sessions[session_id]['verified'] = True
        sessions[session_id]['did'] = did
        write_sessions(sessions)
        return jsonify({ 'message': 'Login confirmed' }), 200

    return jsonify({ 'error': 'Session not found' }), 404

# Handle unknown routes
@app.errorhandler(404)
def not_found(e):
    return jsonify({ "error": "Route not found", "path": request.path }), 404

# Start the server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
