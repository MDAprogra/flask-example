import os
import datetime
import hashlib
from flask import Flask, session, url_for, redirect, render_template, request, abort, flash
from werkzeug.utils import secure_filename
from services.user_service import UserService
from services.note_service import NoteService
from services.image_service import ImageService
from config import Config
from functools import wraps

# Flask App Initialization
app = Flask(__name__)
app.config.from_object(Config)

# Service Initialization
user_service = UserService()
note_service = NoteService()
image_service = ImageService()

# Helper Functions and Decorators
def create_table(data, headers):
    """Creates a table-like structure from data."""
    return zip(*[iter(data)] * len(headers))

def validate_file(filename):
    """Checks if a file is allowed."""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_authenticated(func):
    """Decorator to ensure the user is authenticated."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "current_user" not in session:
            return abort(401)
        return func(*args, **kwargs)
    return wrapper

def ensure_admin(func):
    """Decorator to ensure the user is an admin."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get("current_user") != "ADMIN":
            return abort(403)
        return func(*args, **kwargs)
    return wrapper

# Error Handlers
@app.errorhandler(401)
@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(405)
@app.errorhandler(413)
def handle_error(error):
    """Handles HTTP errors."""
    return render_template(f"page_{error.code}.html"), error.code

# Routes
@app.route("/")
def get_root():
    """Handles root route."""
    return render_template("index.html")

@app.route("/public/")
def get_public():
    """Handles public route."""
    return render_template("public_page.html")

@app.route("/private/")
@ensure_authenticated
def get_private():
    """Handles private route."""
    user_id = session['current_user']
    notes_table = create_table(note_service.get_notes(user_id), ["ID", "Content", "Date", "Delete URL"])
    images_table = create_table(image_service.get_images(user_id), ["ID", "Name", "Date", "Delete URL"])
    return render_template("private_page.html", notes=notes_table, images=images_table)

@app.route("/admin/")
@ensure_admin
def get_admin():
    """Handles admin route."""
    users_table = create_table(user_service.get_users(), ["#", "Username", "Delete URL"])
    return render_template("admin.html", users=users_table)

@app.route("/write_note", methods=["POST"])
@ensure_authenticated
def write_note():
    """Handles note writing."""
    note_service.write_note(session['current_user'], request.form.get("text_note_to_take"))
    return redirect(url_for("get_private"))

@app.route("/delete_note/<note_id>", methods=["GET"])
@ensure_authenticated
def delete_note(note_id):
    """Handles note deletion."""
    note_service.delete_note_if_owned(session['current_user'], note_id)
    return redirect(url_for("get_private"))

@app.route("/upload_image", methods=['POST'])
@ensure_authenticated
def upload_image():
    """Handles image upload."""
    file = request.files.get('file')
    if not file or not validate_file(file.filename):
        flash('Invalid file upload', category='danger')
        return redirect(url_for("get_private"))
    image_service.upload_image(file, session['current_user'], app.config['UPLOAD_FOLDER'])
    return redirect(url_for("get_private"))

@app.route("/delete_image/<image_uid>", methods=["GET"])
@ensure_authenticated
def delete_image(image_uid):
    """Handles image deletion."""
    image_service.delete_image_if_owned(image_uid, session['current_user'], app.config['UPLOAD_FOLDER'])
    return redirect(url_for("get_private"))

@app.route("/login", methods=["POST"])
def login():
    """Handles login."""
    user_service.login(session, request.form.get("id").upper(), request.form.get("pw"))
    return redirect(url_for("get_root"))

@app.route("/logout/")
def logout():
    """Handles logout."""
    session.pop("current_user", None)
    return redirect(url_for("get_root"))

@app.route("/delete_user/<user_id>/", methods=['GET'])
@ensure_admin
def delete_user(user_id):
    """Handles user deletion."""
    user_service.delete_user(user_id, app.config['UPLOAD_FOLDER'])
    return redirect(url_for("get_admin"))

@app.route("/add_user", methods=["POST"])
@ensure_admin
def add_user_route():
    """Handles user addition."""
    new_id = request.form.get('id').upper()
    password = request.form.get('pw')
    if not user_service.add_user(new_id, password):
        users_table = create_table(user_service.get_users(), ["#", "Username", "Delete URL"])
        return render_template("admin.html", id_to_add_is_invalid=True, users=users_table)
    return redirect(url_for("get_admin"))

if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1")