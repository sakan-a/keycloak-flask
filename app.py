import os
from flask import Flask
from flask_login import LoginManager
from models import db, User

from routes.index import index_bp
from routes.login import login_bp
from routes.register import register_bp
from routes.home import home_bp
from routes.messages import messages_bp
from routes.dm import dm_bp, socketio

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
socketio.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

app.register_blueprint(index_bp)
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(home_bp)
app.register_blueprint(messages_bp)
app.register_blueprint(dm_bp)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == '__main__':
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        with app.app_context():
            db.create_all()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=True)
