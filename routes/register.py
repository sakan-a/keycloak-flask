from flask import Blueprint, render_template

register_bp = Blueprint("register", __name__)

@register_bp.route("/register")
def register():
    return render_template("register.html")