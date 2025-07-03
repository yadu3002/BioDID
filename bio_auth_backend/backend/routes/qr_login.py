from flask import Flask, send_from_directory, jsonify, request
import os, json

app = Flask(__name__, static_folder='static')

SESSIONS_FILE = 'sessions.json'

def read_sessions():
    if not os.path.exists(SESSIONS_FILE):
        return {}
    with open(SESSIONS_FILE, 'r') as f:
        return json.load(f)

def write_sessions(data):
    with open(SESSIONS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/web_login.html')
def serve_qr_page():
    return send_from_directory('static', 'web_login.html')

@app.route('/result.html')
def serve_result_page():
    return send_from_directory('static', 'result.html')

@app.route('/api/create-session', methods=['POST'])
def create_session():
    session_id = request.json.get('sessionId')
    sessions = read_sessions()
    sessions[session_id] = { 'verified': False, 'did': None }
    write_sessions(sessions)
    return jsonify({ 'message': 'Session created' })

@app.route('/api/session-status/<session_id>')
def session_status(session_id):
    sessions = read_sessions()
    session = sessions.get(session_id)
    if not session:
        return jsonify({ 'verified': False })
    return jsonify({ 'verified': session['verified'], 'did': session['did'] })

@app.route('/api/confirm-session', methods=['POST'])
def confirm_session():
    data = request.get_json()
    session_id = data.get('sessionId')
    did = data.get('did')

    sessions = read_sessions()
    if session_id in sessions:
        sessions[session_id]['verified'] = True
        sessions[session_id]['did'] = did
        write_sessions(sessions)
        return jsonify({ 'message': 'Login confirmed' }), 200

    return jsonify({ 'error': 'Session not found' }), 404
