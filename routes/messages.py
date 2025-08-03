from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import db, User, Message

messages_bp = Blueprint("messages", __name__)

@messages_bp.route('/messages')
@login_required
def messages():
    recipient = db.session.query(Message.recipient).filter_by(sender=current_user.username)
    sender = db.session.query(Message.sender).filter_by(recipient=current_user.username)
    usernames = set(row[0] for row in recipient.union(sender).all())
    usernames.discard(current_user.username)

    users = User.query.filter(User.username.in_(usernames)).all()

    return render_template('messages.html',
                           users=users,
                           user=current_user)

@messages_bp.route('/search_messages')
@login_required
def search_messages():
    query = request.args.get('q', '').strip()

    if not query:
        return jsonify([])

    recipient = db.session.query(Message.recipient).filter_by(sender=current_user.username)
    sender = db.session.query(Message.sender).filter_by(recipient=current_user.username)
    usernames = set(row[0] for row in recipient.union(sender).all())

    matches = User.query.filter(
        User.username.ilike(f"%{query}%"),
        User.username != current_user.username,
        ~User.username.in_(usernames)
    ).all()

    results = [{'username': u.username} for u in matches]
    return jsonify(results)