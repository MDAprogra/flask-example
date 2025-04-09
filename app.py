"""Flask application for note and image management."""

import os
import datetime
import hashlib
from flask import Flask, session, url_for, redirect, render_template, request, abort, flash
from werkzeug.utils import secure_filename
from database import list_users, verify, delete_user_from_db, add_user
from database import read_note_from_db, write_note_into_db, delete_note_from_db, \
match_user_id_with_note_id
from database import image_upload_record, list_images_for_user, \
match_user_id_with_image_uid, delete_image_from_db

app = Flask(__name__)
app.config.from_object('config')

@app.errorhandler(401)
def handle_401_error(error):
    """Handles 401 error."""
    return render_template("page_401.html"), 401

@app.errorhandler(403)
def handle_403_error(error):
    """Handles 403 error."""
    return render_template("page_403.html"), 403

@app.errorhandler(404)
def handle_404_error(error):
    """Handles 404 error."""
    return render_template("page_404.html"), 404

@app.errorhandler(405)
def handle_405_error(error):
    """Handles 405 error."""
    return render_template("page_405.html"), 405

@app.errorhandler(413)
def handle_413_error(error):
    """Handles 413 error."""
    return render_template("page_413.html"), 413

@app.route("/")
def get_root():
    """Handles root route."""
    return render_template("index.html")

@app.route("/public/")
def get_public():
    """Handles public route."""
    return render_template("public_page.html")

@app.route("/private/")
def get_private():
    """Handles private route."""
    if "current_user" in session.keys():
        notes_list = read_note_from_db(session['current_user'])
        notes_table = zip(
            [x[0] for x in notes_list],
            [x[1] for x in notes_list],
            [x[2] for x in notes_list],
            ["/delete_note/" + x[0] for x in notes_list],
        )

        images_list = list_images_for_user(session['current_user'])
        images_table = zip(
            [x[0] for x in images_list],
            [x[1] for x in images_list],
            [x[2] for x in images_list],
            ["/delete_image/" + x[0] for x in images_list],
        )
        return render_template("private_page.html", notes=notes_table, images=images_table)

    return abort(401)

@app.route("/admin/")
def get_admin():
    """Handles admin route."""
    if session.get("current_user", None) == "ADMIN":
        user_list = list_users()
        user_table = zip(
            range(1, len(user_list) + 1),
            user_list,
            ["/delete_user/" + x for x in user_list],
        )
        return render_template("admin.html", users=user_table)

    return abort(401)

@app.route("/write_note", methods=["POST"])
def write_note():
    """Handles note writing."""
    text_to_write = request.form.get("text_note_to_take")
    write_note_into_db(session['current_user'], text_to_write)
    return redirect(url_for("get_private"))

@app.route("/delete_note/<note_id>", methods=["GET"])
def delete_note(note_id):
    """Handles note deletion."""
    if session.get("current_user", None) == match_user_id_with_note_id(note_id):
        delete_note_from_db(note_id)
    else:
        return abort(401)
    return redirect(url_for("get_private"))

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Checks if file is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload_image", methods=['POST'])
def upload_image():
    """Handles image upload."""
    if 'file' not in request.files:
        flash('No file part', category='danger')
        return redirect(url_for("get_private"))

    file = request.files['file']
    if file.filename == '':
        flash('No selected file', category='danger')
        return redirect(url_for("get_private"))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_time = str(datetime.datetime.now())
        image_uid = hashlib.sha256((upload_time + filename).encode()).hexdigest() # Corrected here.
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], image_uid + "-" + filename)
        file.save(file_path)
        image_upload_record(image_uid, session['current_user'], filename, upload_time)
    return redirect(url_for("get_private"))

@app.route("/delete_image/<image_uid>", methods=["GET"])
def delete_image(image_uid):
    """Handles image deletion."""
    if session.get("current_user", None) == match_user_id_with_image_uid(image_uid):
        delete_image_from_db(image_uid)
        image_to_delete_from_pool = next(
            (y for y in os.listdir(app.config['UPLOAD_FOLDER']) if y.split("-", 1)[0] == image_uid),
            None
        )
        if image_to_delete_from_pool:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], image_to_delete_from_pool))
    else:
        return abort(401)
    return redirect(url_for("get_private"))

@app.route("/login", methods=["POST"])
def login():
    """Handles login."""
    id_submitted = request.form.get("id").upper()
    if (id_submitted in list_users()) and verify(id_submitted, request.form.get("pw")):
        session['current_user'] = id_submitted
    return redirect(url_for("get_root"))

@app.route("/logout/")
def logout():
    """Handles logout."""
    session.pop("current_user", None)
    return redirect(url_for("get_root"))

@app.route("/delete_user/<user_id>/", methods=['GET'])
def delete_user(user_id):
    """Handles user deletion."""
    if session.get("current_user", None) == "ADMIN":
        if user_id == "ADMIN":
            return abort(403)
        images_to_remove = [x[0] for x in list_images_for_user(user_id)]
        for f in images_to_remove:
            image_to_delete_from_pool = next(
                (y for y in os.listdir(app.config['UPLOAD_FOLDER']) if y.split("-", 1)[0] == f),
                None
            )
            if image_to_delete_from_pool:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], image_to_delete_from_pool))
        delete_user_from_db(user_id)
        return redirect(url_for("get_admin"))
    return abort(401)

@app.route("/add_user", methods=["POST"])
def add_user_route():
    """Handles user addition."""
    if session.get("current_user", None) == "ADMIN":
        new_id = request.form.get('id').upper()
        if new_id in list_users():
            user_list = list_users()
            user_table = zip(
                range(1, len(user_list) + 1),
                user_list,
                ["/delete_user/" + x for x in user_list],
            )
            return render_template("admin.html", id_to_add_is_duplicated=True, users=user_table)
        if " " in new_id or "'" in new_id:
            user_list = list_users()
            user_table = zip(
                range(1, len(user_list) + 1),
                user_list,
                ["/delete_user/" + x for x in user_list],
            )
            return render_template("admin.html", id_to_add_is_invalid=True, users=user_table)
        add_user(new_id, request.form.get('pw'))
        return redirect(url_for("get_admin"))
    return abort(401)

if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1") # Corrected here.