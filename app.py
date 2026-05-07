import os
import logging
from logging.handlers import TimedRotatingFileHandler
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__, static_folder="asset", static_url_path="/asset")
app.secret_key = "secret-key-ganti-ini"

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

handler = TimedRotatingFileHandler(
    filename=os.path.join(LOG_DIR, "app.log"),
    when="midnight",
    interval=1,
    backupCount=30,
    encoding="utf-8"
)
handler.suffix = "%Y-%m-%d.log"
handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
))

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

# User dummy untuk demo
USERS = {"admin@example.com": "password123"}


@app.route("/")
def home():
    logger.debug(f"Home route accessed, method: {request.method}, IP: {request.remote_addr}")
    logger.debug(f"Home session state: {dict(session)}")
    logger.debug(f"Home request headers: User-Agent={request.headers.get('User-Agent')}")
    if "email" not in session:
        logger.debug("No email in session, redirecting to login")
        return redirect(url_for("login"))
    logger.info(f"Home accessed by {session['email']}")
    logger.debug(f"Rendering home.html for {session['email']}")
    return render_template("home.html", email=session["email"])


@app.route("/login", methods=["GET", "POST"])
def login():
    logger.debug(f"Login route accessed, method: {request.method}, IP: {request.remote_addr}")
    logger.debug(f"Login request headers: User-Agent={request.headers.get('User-Agent')}")
    logger.debug(f"Login current session state: {dict(session)}")
    error = None
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        logger.debug(f"Login POST received, email: {email}, password: {password}")
        logger.debug(f"Login checking credentials for: {email}")
        logger.debug(f"Login email exists in USERS: {email in USERS}")
        if USERS.get(email) == password:
            session["email"] = email
            logger.debug(f"Login session created for: {email}")
            logger.info(f"Login success: {email}, IP: {request.remote_addr}")
            logger.debug(f"Login redirecting to home")
            return redirect(url_for("home"))
        logger.warning(f"Login failed: {email}, IP: {request.remote_addr}")
        logger.debug(f"Login password mismatch for: {email}")
        error = "Email atau password salah"
    logger.debug(f"Login rendering login.html, error: {error}")
    return render_template("login.html", error=error)


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    logger.debug(f"Forgot password route accessed, method: {request.method}, IP: {request.remote_addr}")
    logger.debug(f"Forgot password request headers: User-Agent={request.headers.get('User-Agent')}")
    error = None
    success = None
    if request.method == "POST":
        email = request.form["email"]
        last_password = request.form["last_password"]
        new_password = request.form["new_password"]
        logger.debug(f"Forgot password POST received, email: {email}, last_password: {last_password}, new_password: {new_password}")
        logger.debug(f"Forgot password email exists in USERS: {email in USERS}")
        logger.debug(f"Forgot password verifying last password for: {email}")
        if USERS.get(email) == last_password:
            USERS[email] = new_password
            logger.info(f"Password changed: {email}")
            logger.debug(f"Password updated in USERS dict for: {email}")
            success = "Password berhasil diubah! Silakan login."
        else:
            logger.warning(f"Password recovery failed: {email}, IP: {request.remote_addr}")
            logger.debug(f"Forgot password last_password mismatch for: {email}")
            error = "Email atau password lama tidak cocok"
    logger.debug(f"Forgot password rendering, error: {error}, success: {success}")
    return render_template("forgot_password.html", error=error, success=success)


@app.route("/logout")
def logout():
    logger.debug(f"Logout route accessed, IP: {request.remote_addr}")
    logger.debug(f"Logout session before clear: {dict(session)}")
    email = session.get('email')
    logger.info(f"Logout: {email}")
    session.pop("email", None)
    logger.debug(f"Logout session after clear: {dict(session)}")
    logger.debug(f"Logout redirecting to login")
    return redirect(url_for("login"))


@app.route("/verify", methods=["GET", "POST"])
def verify():
    logger.debug(f"Verify route accessed, method: {request.method}, IP: {request.remote_addr}")
    if "email" not in session:
        logger.debug("Verify: no session, redirecting to login")
        return redirect(url_for("login"))
    error = None
    success = None
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        logger.debug(f"Verify POST received, email: {email}, password: {password}")
        logger.debug(f"Verify session email: {session['email']}")
        logger.debug(f"Verify email match session: {email == session['email']}")
        if email == session["email"] and USERS.get(email) == password:
            logger.info(f"Verify success: {email}")
            success = "Verifikasi berhasil! Akun Anda terconfirm."
        else:
            logger.warning(f"Verify failed: {email}, IP: {request.remote_addr}")
            logger.debug(f"Verify mismatch - input email: {email}, session: {session['email']}, password valid: {USERS.get(email) == password}")
            error = "Email atau password tidak cocok dengan akun yang sedang login"
    logger.debug(f"Verify rendering, error: {error}, success: {success}")
    return render_template("verify.html", error=error, success=success)


@app.route("/api/log", methods=["POST"])
def client_log():
    data = request.get_json()
    if not data:
        logger.debug("Client log received empty payload")
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
        logger.debug(log_msg)
    return "", 204


if __name__ == "__main__":
    logger.debug("="*50)
    logger.debug("Application starting...")
    logger.debug(f"Log directory: {os.path.abspath(LOG_DIR)}")
    logger.debug(f"Static folder: {app.static_folder}")
    logger.debug(f"Registered users: {list(USERS.keys())}")
    logger.debug("="*50)
    app.run(debug=True)
