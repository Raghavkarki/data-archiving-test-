"""Authentication routes"""
from flask import Blueprint, render_template, request, redirect, url_for, session, current_app

auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Login page"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        config = current_app.config
        
        current_app.logger.info(f"Login attempt from IP: {request.remote_addr}, Username: {username}")


        if username == config['VALID_USERNAME'] and password == config['VALID_PASSWORD']:
            session["logged_in"] = True
            current_app.logger.info(f"Successful login for user: {username} from IP :{request.remote_addr}")
            return redirect(url_for("main.admin"))
        else:
            current_app.logger.info(f"Failed to log in for uset {username}  form IP :{reuest.remote_addr}")
            return render_template("login.html", error="Invalid username or password.")
    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    """Logout and clear session"""
    current_app.logger.info(f" User logged out from IP : {request.remote_addr}")
    session.pop("logged_in", None)
    return redirect(url_for("auth.login"))

