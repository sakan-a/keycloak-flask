from flask import Blueprint, render_template
from flask_socketio import SocketIO, emit, join_room
from flask_login import login_required, current_user
from datetime import datetime
from models import db, Message

dm_bp = Blueprint("dm", __name__)

socketio = SocketIO()

@dm_bp.route('/messages/<recipient>')
@login_required
def dm(recipient):
    messages = Message.query.filter(
        ((Message.sender == current_user.username) & (Message.recipient == recipient)) |
        ((Message.sender == recipient) & (Message.recipient == current_user.username))
    ).order_by(Message.timestamp.asc()).all()
    
    return render_template('dm.html',
                           messages=messages,
                           recipient=recipient,
                           user=current_user.username)

@socketio.on('send_message')
def message_handler(data):
    sender = current_user.username
    recipient = data['recipient']
    text = data['message']
    timestamp = datetime.utcnow()

    if text.strip():
        msg = Message(sender=sender, recipient=recipient, text=text, timestamp=timestamp)
        db.session.add(msg)
        db.session.commit()

    dm = get_dm(sender, recipient)
    emit('receive_message', {
        'sender': sender,
        'recipient': recipient,
        'message': text,
        'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S')
    }, room=dm)

@socketio.on('join')
def on_join(data):
    dm = get_dm(current_user.username, data['recipient'])
    join_room(dm)

def get_dm(user1, user2):
    return '_'.join(sorted([user1, user2]))