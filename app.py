import os
import logging
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__, static_folder="asset", static_url_path="/asset")
app.secret_key = "secret-key-ganti-ini"

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# User dummy untuk demo
USERS = {"admin@example.com": "password123"}


@app.route("/")
def home():
    logger.info(f"Home route accessed, method: {request.method}, IP: {request.remote_addr}")
    logger.info(f"Home session state: {dict(session)}")
    logger.info(f"Home request headers: User-Agent={request.headers.get('User-Agent')}")
    if "email" not in session:
        logger.info("No email in session, redirecting to login")
        return redirect(url_for("login"))
    logger.info(f"Home accessed by {session['email']}")
    logger.info(f"Rendering home.html for {session['email']}")
    return render_template("home.html", email=session["email"])


@app.route("/login", methods=["GET", "POST"])
def login():
    logger.info(f"Login route accessed, method: {request.method}, IP: {request.remote_addr}")
    logger.info(f"Login request headers: User-Agent={request.headers.get('User-Agent')}")
    logger.info(f"Login current session state: {dict(session)}")
    error = None
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        logger.info(f"Login POST received, email: {email}, password: {password}")
        logger.info(f"Login checking credentials for: {email}")
        logger.info(f"Login email exists in USERS: {email in USERS}")
        if USERS.get(email) == password:
            session["email"] = email
            logger.info(f"Login session created for: {email}")
            logger.info(f"Login success: {email}, IP: {request.remote_addr}")
            logger.info(f"Login redirecting to home")
            return redirect(url_for("home"))
        logger.warning(f"Login failed: {email}, IP: {request.remote_addr}")
        logger.info(f"Login password mismatch for: {email}")
        error = "Email atau password salah"
    logger.info(f"Login rendering login.html, error: {error}")
    return render_template("login.html", error=error)


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    logger.info(f"Forgot password route accessed, method: {request.method}, IP: {request.remote_addr}")
    logger.info(f"Forgot password request headers: User-Agent={request.headers.get('User-Agent')}")
    error = None
    success = None
    if request.method == "POST":
        email = request.form["email"]
        last_password = request.form["last_password"]
        new_password = request.form["new_password"]
        logger.info(f"Forgot password POST received, email: {email}, last_password: {last_password}, new_password: {new_password}")
        logger.info(f"Forgot password email exists in USERS: {email in USERS}")
        logger.info(f"Forgot password verifying last password for: {email}")
        if USERS.get(email) == last_password:
            USERS[email] = new_password
            logger.info(f"Password changed: {email}")
            logger.info(f"Password updated in USERS dict for: {email}")
            success = "Password berhasil diubah! Silakan login."
        else:
            logger.warning(f"Password recovery failed: {email}, IP: {request.remote_addr}")
            logger.info(f"Forgot password last_password mismatch for: {email}")
            error = "Email atau password lama tidak cocok"
    logger.info(f"Forgot password rendering, error: {error}, success: {success}")
    return render_template("forgot_password.html", error=error, success=success)


@app.route("/logout")
def logout():
    logger.info(f"Logout route accessed, IP: {request.remote_addr}")
    logger.info(f"Logout session before clear: {dict(session)}")
    email = session.get('email')
    logger.info(f"Logout: {email}")
    session.pop("email", None)
    logger.info(f"Logout session after clear: {dict(session)}")
    logger.info(f"Logout redirecting to login")
    return redirect(url_for("login"))


@app.route("/verify", methods=["GET", "POST"])
def verify():
    logger.info(f"Verify route accessed, method: {request.method}, IP: {request.remote_addr}")
    if "email" not in session:
        logger.info("Verify: no session, redirecting to login")
        return redirect(url_for("login"))
    error = None
    success = None
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        logger.info(f"Verify POST received, email: {email}, password: {password}")
        logger.info(f"Verify session email: {session['email']}")
        logger.info(f"Verify email match session: {email == session['email']}")
        if email == session["email"] and USERS.get(email) == password:
            logger.info(f"Verify success: {email}")
            success = "Verifikasi berhasil! Akun Anda terconfirm."
        else:
            logger.warning(f"Verify failed: {email}, IP: {request.remote_addr}")
            logger.info(f"Verify mismatch - input email: {email}, session: {session['email']}, password valid: {USERS.get(email) == password}")
            error = "Email atau password tidak cocok dengan akun yang sedang login"
    logger.info(f"Verify rendering, error: {error}, success: {success}")
    return render_template("verify.html", error=error, success=success)


@app.route("/api/log", methods=["POST"])
def client_log():
    data = request.get_json()
    if not data:
        logger.info("Client log received empty payload")
        return "", 400
    level = data.get("level", "debug")
    message = data.get("message", "")
    log_msg = f"[CLIENT][{request.remote_addr}] {message}"
    if level == "error":
        logger.error(log_msg)
    elif level == "warning":
        logger.warning(log_msg)
    elif level == "info":
        logger.info(log_msg)
    else:
        logger.info(log_msg)
    return "", 204


if __name__ == "__main__":
    app.run(debug=True)
