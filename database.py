"""
Database module for handling user, note, and image data.
"""

import sqlite3
import hashlib
import datetime
import os

# Utilisez une base de données différente pour les tests
if 'PYTEST_CURRENT_TEST' in os.environ:
    USER_DB_FILE_LOCATION = "database_file/test_users.db"
    NOTE_DB_FILE_LOCATION = "database_file/test_notes.db"
    IMAGE_DB_FILE_LOCATION = "database_file/test_images.db"
else:
    USER_DB_FILE_LOCATION = "database_file/users.db"
    NOTE_DB_FILE_LOCATION = "database_file/notes.db"
    IMAGE_DB_FILE_LOCATION = "database_file/images.db"

def list_users():
    """
List all users in the database.
    """
    _conn = sqlite3.connect(USER_DB_FILE_LOCATION)
    _c = _conn.cursor()

    _c.execute("SELECT id FROM users;")
    result = [x[0] for x in _c.fetchall()]

    _conn.close()

    return result

def verify(user_id, pw):
    """
Verify user credentials.
    """
    _conn = sqlite3.connect(USER_DB_FILE_LOCATION)
    _c = _conn.cursor()

    _c.execute("SELECT pw FROM users WHERE id = ?;", (user_id,))
    result = _c.fetchone()[0] == hashlib.sha256(pw.encode()).hexdigest()

    _conn.close()

    return result

def delete_user_from_db(user_id):
    """
Delete a user and all associated data from the database.
    """
    _conn = sqlite3.connect(USER_DB_FILE_LOCATION)
    _c = _conn.cursor()
    _c.execute("DELETE FROM users WHERE id = ?;", (user_id,))
    _conn.commit()
    _conn.close()

    # when we delete a user FROM database USERS, we also need to delete all his or her notes data FROM database NOTES
    _conn = sqlite3.connect(NOTE_DB_FILE_LOCATION)
    _c = _conn.cursor()
    _c.execute("DELETE FROM notes WHERE user = ?;", (user_id,))
    _conn.commit()
    _conn.close()

    # when we delete a user FROM database USERS, we also need to
    # [1] delete all his or her images FROM image pool (done in app.py)
    # [2] delete all his or her images records FROM database IMAGES
    _conn = sqlite3.connect(IMAGE_DB_FILE_LOCATION)
    _c = _conn.cursor()
    _c.execute("DELETE FROM images WHERE owner = ?;", (user_id,))
    _conn.commit()
    _conn.close()

def add_user(user_id, pw):
    """
Add a new user to the database.
    """
    _conn = sqlite3.connect(USER_DB_FILE_LOCATION)
    _c = _conn.cursor()

    _c.execute(
        "INSERT INTO users values(?, ?)",
        (user_id.upper(), hashlib.sha256(pw.encode()).hexdigest())
    )

    _conn.commit()
    _conn.close()

def read_note_from_db(user_id):
    """
Read all notes for a specific user from the database.
    """
    _conn = sqlite3.connect(NOTE_DB_FILE_LOCATION)
    _c = _conn.cursor()

    command = "SELECT note_id, timestamp, note FROM notes WHERE user = ?;"
    _c.execute(command, (user_id.upper(),))
    result = _c.fetchall()

    _conn.commit()
    _conn.close()

    return result

def match_user_id_with_note_id(note_id):
    """
Given the note id, confirm if the current user is the owner of the note which is being operated.
    """
    _conn = sqlite3.connect(NOTE_DB_FILE_LOCATION)
    _c = _conn.cursor()

    command = "SELECT user FROM notes WHERE note_id = ?;"
    _c.execute(command, (note_id,))
    result = _c.fetchone()[0]

    _conn.commit()
    _conn.close()

    return result

def write_note_into_db(user_id, note_to_write):
    """
Write a new note into the database.
    """
    _conn = sqlite3.connect(NOTE_DB_FILE_LOCATION)
    _c = _conn.cursor()

    current_timestamp = str(datetime.datetime.now())
    _c.execute(
        "INSERT INTO notes values(?, ?, ?, ?)",
        (
            user_id.upper(),
            current_timestamp,
            note_to_write,
            hashlib.sha256((user_id.upper() + current_timestamp).encode()).hexdigest() # corrected here
        )
    )

    _conn.commit()
    _conn.close()

def delete_note_from_db(note_id):
    """
Delete a note from the database.
    """
    _conn = sqlite3.connect(NOTE_DB_FILE_LOCATION)
    _c = _conn.cursor()

    _c.execute("DELETE FROM notes WHERE note_id = ?;", (note_id,))
    _conn.commit()
    _conn.close()

def image_upload_record(uid, owner, image_name, timestamp):
    """
Record an image upload into the database.
    """
    _conn = sqlite3.connect(IMAGE_DB_FILE_LOCATION)
    _c = _conn.cursor()

    _c.execute(
        "INSERT INTO images VALUES (?, ?, ?, ?)",
        (uid, owner, image_name, timestamp)
    )

    _conn.commit()
    _conn.close()

def list_images_for_user(owner):
    """
List all images for a specific user from the database.
    """
    _conn = sqlite3.connect(IMAGE_DB_FILE_LOCATION)
    _c = _conn.cursor()

    command = "SELECT uid, timestamp, name FROM images WHERE owner = ?"
    _c.execute(command, (owner,))
    result = _c.fetchall()

    _conn.commit()
    _conn.close()

    return result

def match_user_id_with_image_uid(image_uid):
    """
Given the image id, confirm if the current user is the owner of the image which is being operated.
    """
    _conn = sqlite3.connect(IMAGE_DB_FILE_LOCATION)
    _c = _conn.cursor()

    command = "SELECT owner FROM images WHERE uid = ?;"
    _c.execute(command, (image_uid,))
    result = _c.fetchone()[0]

    _conn.commit()
    _conn.close()

    return result

def delete_image_from_db(image_uid):
    """
Delete an image from the database.
    """
    _conn = sqlite3.connect(IMAGE_DB_FILE_LOCATION)
    _c = _conn.cursor()

    _c.execute("DELETE FROM images WHERE uid = ?;", (image_uid,))
    _conn.commit()
    _conn.close()