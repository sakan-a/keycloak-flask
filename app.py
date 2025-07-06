from flask import Flask
from routes.index import index_bp
from routes.login import login_bp
from routes.register import register_bp

app = Flask(__name__)

app.register_blueprint(index_bp)
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)

if __name__ == "__main__":
    app.run(debug=True)