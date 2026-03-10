#!/usr/bin/env python3
"""
Fiverr Monitor Server
WebSocket server that bridges agent and dashboard
"""

import os
import json
import logging
import secrets
from datetime import datetime, timedelta
from typing import Dict, Set
from collections import deque

from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit, disconnect
from werkzeug.security import generate_password_hash, check_password_hash
from flask_compress import Compress

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configuration
SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_urlsafe(64))
AGENT_TOKEN = os.getenv('AGENT_TOKEN', '')
DASHBOARD_USER = os.getenv('DASHBOARD_USER', 'admin')
DASHBOARD_PASS = os.getenv('DASHBOARD_PASS', 'admin123')
VAPID_PUBLIC_KEY = os.getenv('VAPID_PUBLIC_KEY', '')
VAPID_PRIVATE_KEY = os.getenv('VAPID_PRIVATE_KEY', '')
VAPID_CLAIM_EMAIL = os.getenv('VAPID_CLAIM_EMAIL', '')

# Setup Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Setup SocketIO
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='threading',
    ping_timeout=60,
    ping_interval=25
)

# Setup compression
Compress(app)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# In-memory storage
connected_agents: Dict[str, dict] = {}
connected_clients: Set[str] = set()
messages: deque = deque(maxlen=100)  # Last 100 messages
failed_logins: Dict[str, list] = {}  # IP -> list of attempt times


# ============================================================================
# Authentication Middleware
# ============================================================================

def check_auth(username, password):
    """Check dashboard credentials"""
    return username == DASHBOARD_USER and password == DASHBOARD_PASS


def check_agent_token(token):
    """Check agent token"""
    return token == AGENT_TOKEN


def is_ip_blocked(ip):
    """Check if IP is blocked due to failed logins"""
    if ip in failed_logins:
        # Remove attempts older than 1 hour
        now = datetime.now()
        failed_logins[ip] = [
            t for t in failed_logins[ip]
            if now - t < timedelta(hours=1)
        ]
        return len(failed_logins[ip]) >= 3
    return False


# ============================================================================
# HTTP Routes
# ============================================================================

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'agents_online': len(connected_agents),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/login', methods=['POST'])
def login():
    """Dashboard login endpoint"""
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    ip = request.remote_addr

    if is_ip_blocked(ip):
        return jsonify({'error': 'IP blocked due to too many failed attempts'}), 429

    if check_auth(username, password):
        session['authenticated'] = True
        session['login_time'] = datetime.now().isoformat()

        # Clear failed attempts on successful login
        if ip in failed_logins:
            del failed_logins[ip]

        return jsonify({
            'success': True,
            'vapid_public_key': VAPID_PUBLIC_KEY
        })

    # Record failed attempt
    if ip not in failed_logins:
        failed_logins[ip] = []
    failed_logins[ip].append(datetime.now())

    return jsonify({'error': 'Invalid credentials'}), 401


@app.route('/api/status')
def status():
    """Get system status"""
    if not session.get('authenticated'):
        return jsonify({'error': 'Unauthorized'}), 401

    return jsonify({
        'agents_online': len(connected_agents),
        'clients_connected': len(connected_clients),
        'messages_stored': len(messages),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/messages')
def get_messages():
    """Get stored messages"""
    if not session.get('authenticated'):
        return jsonify({'error': 'Unauthorized'}), 401

    return jsonify({
        'messages': list(messages),
        'count': len(messages)
    })


@app.route('/api/vapid-config')
def vapid_config():
    """Get VAPID configuration for push notifications"""
    if not session.get('authenticated'):
        return jsonify({'error': 'Unauthorized'}), 401

    return jsonify({
        'publicKey': VAPID_PUBLIC_KEY,
        'claimEmail': VAPID_CLAIM_EMAIL
    })


@app.route('/api/push-subscription', methods=['POST'])
def push_subscription():
    """Store push notification subscription"""
    if not session.get('authenticated'):
        return jsonify({'error': 'Unauthorized'}), 401

    subscription = request.get_json()
    # In production, store this in a database
    logger.info(f"Push subscription registered: {subscription.get('endpoint', 'unknown')}")
    return jsonify({'success': True})


# ============================================================================
# WebSocket Events
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    if not session.get('authenticated'):
        # Check for agent token in query params
        token = request.args.get('token', '')
        if check_agent_token(token):
            # This is an agent connection
            connected_agents[request.sid] = {
                'connected_at': datetime.now().isoformat(),
                'user_agent': request.user_agent.string
            }
            logger.info(f"Agent connected: {request.sid}")
            emit('agent_connected', {
                'agent_id': request.sid,
                'timestamp': datetime.now().isoformat()
            }, broadcast=True)
        else:
            logger.warning(f"Unauthorized connection attempt from {request.remote_addr}")
            return False
    else:
        # This is a dashboard client
        connected_clients.add(request.sid)
        logger.info(f"Dashboard client connected: {request.sid}")

        # Send current agent status
        emit('status', {
            'agents_online': len(connected_agents),
            'agents': list(connected_agents.keys())
        })


@socketio.on('disconnect')
def handle_disconnect():
    """Handle disconnection"""
    if request.sid in connected_agents:
        del connected_agents[request.sid]
        logger.info(f"Agent disconnected: {request.sid}")
        emit('agent_disconnected', {
            'agent_id': request.sid,
            'timestamp': datetime.now().isoformat()
        }, broadcast=True)

    if request.sid in connected_clients:
        connected_clients.remove(request.sid)
        logger.info(f"Dashboard client disconnected: {request.sid}")


@socketio.on('agent_info')
def handle_agent_info(data):
    """Handle agent info update"""
    if request.sid in connected_agents:
        connected_agents[request.sid].update(data)
        emit('agent_status', {
            'agent_id': request.sid,
            'info': data,
            'timestamp': datetime.now().isoformat()
        }, broadcast=True)


@socketio.on('heartbeat')
def handle_heartbeat(data):
    """Handle agent heartbeat"""
    if request.sid in connected_agents:
        connected_agents[request.sid]['last_heartbeat'] = datetime.now().isoformat()


@socketio.on('new_message')
def handle_new_message(data):
    """Handle new message from agent"""
    # Store message
    message_data = {
        **data,
        'server_timestamp': datetime.now().isoformat()
    }
    messages.append(message_data)

    # Broadcast to all dashboard clients
    emit('new_message', message_data, broadcast=True, include_self=False)

    logger.info(f"New message from {data.get('conversation', {}).get('username', 'unknown')}")


@socketio.on('reply_sent')
def handle_reply_sent(data):
    """Handle reply confirmation from agent"""
    emit('reply_sent', data, broadcast=True, include_self=False)


@socketio.on('send_reply')
def handle_send_reply(data):
    """Handle send reply request from dashboard"""
    conversation_id = data.get('conversation_id')
    message = data.get('message')

    if not conversation_id or not message:
        return

    # Forward to agent
    emit('send_reply', data, broadcast=True)


@socketio.on('ping')
def handle_ping():
    """Handle ping"""
    emit('pong')


# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# Main
# ============================================================================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    logger.info("==================================================")
    logger.info("Fiverr Monitor Server শুরু হচ্ছে | Starting...")
    logger.info(f"Port: {port}")
    logger.info(f"Agents: {len(connected_agents)}")
    logger.info("==================================================")

    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=False,
        allow_unsafe_werkzeug=True
    )
