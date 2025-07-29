import os
from flask import Flask, redirect, url_for, session, render_template_string, jsonify, abort
from functools import wraps
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from keycloak import KeycloakAdmin

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated_function

def require_role(role_name):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user = session.get("user", {})
            roles = user.get("realm_access", {}).get("roles", [])
            if role_name not in roles:
                abort(403)
            return f(*args, **kwargs)
        return wrapper
    return decorator

load_dotenv()

app = Flask(__name__)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,      # True in production (HTTPS only)
    SESSION_COOKIE_SAMESITE="Lax"
)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

oauth = OAuth(app)
oauth.register(
    name="keycloak",
    client_id=os.getenv("KEYCLOAK_CLIENT_ID"),
    client_secret=os.getenv("KEYCLOAK_CLIENT_SECRET"),
    server_metadata_url=os.getenv("KEYCLOAK_SERVER_METADATA_URL"),
    client_kwargs={"scope": "openid profile email"},
)

print("FLASK_SECRET_KEY:", os.getenv("FLASK_SECRET_KEY"))
app.secret_key = os.getenv("FLASK_SECRET_KEY")

print("--- Attempting to connect to Keycloak with the following admin credentials ---")
print(f"SERVER URL: {os.getenv('KEYCLOAK_SERVER_URL')}")
print(f"REALM NAME: {os.getenv('KEYCLOAK_REALM_NAME')}")
print(f"ADMIN CLIENT ID: {os.getenv('KEYCLOAK_SERVICE_ACCOUNT_CLIENT_ID')}")
secret = os.getenv('KEYCLOAK_SERVICE_ACCOUNT_CLIENT_SECRET')
if secret:
    print(f"ADMIN CLIENT SECRET: ...{secret[-4:]}") # Print only last 4 chars
else:
    print("ADMIN CLIENT SECRET: Not found!")
print("--------------------------------------------------------------------------")

keycloak_admin = KeycloakAdmin(
        server_url=os.getenv("KEYCLOAK_SERVER_URL"),
        client_id=os.getenv("KEYCLOAK_SERVICE_ACCOUNT_CLIENT_ID"),
        client_secret_key=os.getenv("KEYCLOAK_SERVICE_ACCOUNT_CLIENT_SECRET"),
        realm_name=os.getenv("KEYCLOAK_REALM_NAME"),
    )


@app.route("/")
def index():
    user = session.get("user")
    if user:
        return render_template_string('''
            <h1>Welcome, {{ user['name'] }}, {{ user['sub'] }}!</h1>
            <h2>All data: {{ user }}</h2>
            <form action="{{ url_for('logout') }}" method="post" style="display:inline;">
                <button type="submit">Logout</button>
            </form>
            <button id="get-users-btn">Get Users</button>
            <script>
                document.getElementById('get-users-btn').addEventListener('click', function() {
                    fetch('{{ url_for('get_users') }}')
                        .then(response => response.json())
                        .then(data => {
                            console.log(data);
                            alert('User data has been logged to the console.');
                        })
                        .catch(error => {
                            console.error('Error fetching users:', error);
                            alert('Failed to fetch user data. See console for details.');
                        });
                });
            </script>
        ''', user=user)
    else:
        return render_template_string('''
            <h1>Hello, you are not logged in.</h1>
            <form action="{{ url_for('login') }}" method="post">
                <button type="submit">Login</button>
            </form>
        ''')

# Login page
@app.route("/login", methods=["POST"])
def login():
    redirect_uri = url_for("auth", _external=True)
    print("Before redirect, session contains:", dict(session))
    return oauth.keycloak.authorize_redirect(redirect_uri)

# Auth callback
@app.route("/auth")
def auth():
    print("At callback, session contains:", dict(session))
    token = oauth.keycloak.authorize_access_token()
    session["id_token"] = token["id_token"]
    session["user"] = oauth.keycloak.userinfo(token=token)
    return redirect("/")

# Logout
@app.route("/logout", methods=["POST"])
def logout():
    id_token = session.pop("id_token", None)
    session.pop("user", None)

    logout_base = os.getenv("KEYCLOAK_LOGOUT_URL")
    post_logout_redirect_uri = url_for("index", _external=True)

    # NOTE: OIDC standard parameters:
    #   post_logout_redirect_uri → where KC should send the browser *after* logout
    #   id_token_hint           → your original login ID token
    url = (
        f"{logout_base}"
        f"?post_logout_redirect_uri={post_logout_redirect_uri}"
        f"&id_token_hint={id_token}"
    )
    return redirect(url)


@app.route("/users")
@login_required
@require_role("admin")
def get_users():
    try:
        # Requires a client with "Service Account" enabled
        # and the "query-users" role assigned to it.
        users = keycloak_admin.get_users({})
        return jsonify(users)
    except Exception as e:
        print(f"Error fetching users from Keycloak: {e}")
        return jsonify({"error": "Failed to fetch users", "details": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
