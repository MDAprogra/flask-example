"""Flask application for note and image management."""
import os
import datetime
import hashlib
from flask import Flask, session, url_for, redirect, render_template, request, abort, flash
from werkzeug.utils import secure_filename
from database import (
    list_users, verify, delete_user_from_db, add_user,
    read_note_from_db, write_note_into_db, delete_note_from_db,
    match_user_id_with_note_id, image_upload_record,
    list_images_for_user, match_user_id_with_image_uid,
    delete_image_from_db
)

app = Flask(__name__)
app.config.from_object('config')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    """Checks if file is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# === Error Handlers === #
@app.errorhandler(401)
def handle_401_error(error): return render_template("page_401.html"), 401

@app.errorhandler(403)
def handle_403_error(error): return render_template("page_403.html"), 403

@app.errorhandler(404)
def handle_404_error(error): return render_template("page_404.html"), 404

@app.errorhandler(405)
def handle_405_error(error): return render_template("page_405.html"), 405

@app.errorhandler(413)
def handle_413_error(error): return render_template("page_413.html"), 413


# === Routes === #
@app.route("/")
def get_root(): return render_template("index.html")

@app.route("/public/")
def get_public(): return render_template("public_page.html")

@app.route("/private/")
def get_private():
    user = session.get("current_user")
    if not user: return abort(401)

    notes = read_note_from_db(user)
    notes_table = zip(
        [n[0] for n in notes],
        [n[1] for n in notes],
        [n[2] for n in notes],
        [f"/delete_note/{n[0]}" for n in notes]
    )

    images = list_images_for_user(user)
    images_table = zip(
        [img[0] for img in images],
        [img[1] for img in images],
        [img[2] for img in images],
        [f"/delete_image/{img[0]}" for img in images]
    )

    return render_template("private_page.html", notes=notes_table, images=images_table)


@app.route("/admin/")
def get_admin():
    if session.get("current_user") != "ADMIN":
        return abort(401)
    users = list_users()
    user_table = zip(range(1, len(users) + 1), users, [f"/delete_user/{u}" for u in users])
    return render_template("admin.html", users=user_table)


@app.route("/login", methods=["POST"])
def login():
    user_id = request.form.get("id", "").upper()
    password = request.form.get("pw")

    if user_id in list_users() and verify(user_id, password):
        session['current_user'] = user_id
    return redirect(url_for("get_root"))


@app.route("/logout/")
def logout():
    session.pop("current_user", None)
    return redirect(url_for("get_root"))


@app.route("/write_note", methods=["POST"])
def write_note():
    text = request.form.get("text_note_to_take")
    write_note_into_db(session['current_user'], text)
    return redirect(url_for("get_private"))


@app.route("/delete_note/<note_id>", methods=["GET"])
def delete_note(note_id):
    user = session.get("current_user")
    if user != match_user_id_with_note_id(note_id):
        return abort(401)
    delete_note_from_db(note_id)
    return redirect(url_for("get_private"))


@app.route("/upload_image", methods=["POST"])
def upload_image():
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
        image_uid = hashlib.sha256((upload_time + filename).encode()).hexdigest()
        path = os.path.join(app.config['UPLOAD_FOLDER'], f"{image_uid}-{filename}")
        file.save(path)
        image_upload_record(image_uid, session['current_user'], filename, upload_time)

    return redirect(url_for("get_private"))


@app.route("/delete_image/<image_uid>", methods=["GET"])
def delete_image(image_uid):
    user = session.get("current_user")
    if user != match_user_id_with_image_uid(image_uid):
        return abort(401)

    delete_image_from_db(image_uid)
    folder = app.config['UPLOAD_FOLDER']
    file = next((f for f in os.listdir(folder) if f.startswith(image_uid)), None)
    if file:
        os.remove(os.path.join(folder, file))
    return redirect(url_for("get_private"))


@app.route("/add_user", methods=["POST"])
def add_user_route():
    if session.get("current_user") != "ADMIN":
        return abort(401)

    new_id = request.form.get("id", "").upper()
    pw = request.form.get("pw")

    if new_id in list_users():
        return render_template("admin.html", users=_render_users(), id_to_add_is_duplicated=True)

    if " " in new_id or "'" in new_id:
        return render_template("admin.html", users=_render_users(), id_to_add_is_invalid=True)

    add_user(new_id, pw)
    return redirect(url_for("get_admin"))


@app.route("/delete_user/<user_id>/", methods=["GET"])
def delete_user(user_id):
    if session.get("current_user") != "ADMIN":
        return abort(401)
    if user_id == "ADMIN":
        return abort(403)

    images = [img[0] for img in list_images_for_user(user_id)]
    folder = app.config['UPLOAD_FOLDER']

    for uid in images:
        file = next((f for f in os.listdir(folder) if f.startswith(uid)), None)
        if file:
            os.remove(os.path.join(folder, file))

    delete_user_from_db(user_id)
    return redirect(url_for("get_admin"))


# === Helpers === #
def _render_users():
    user_list = list_users()
    return zip(range(1, len(user_list) + 1), user_list, [f"/delete_user/{u}" for u in user_list])


# === Run Server === #
if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1")
    