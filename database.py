"""
Database module for handling user, note, and image data.
"""

import sqlite3
import hashlib
import datetime
import os


class Config:
    """Configuration for database file locations."""
    if 'PYTEST_CURRENT_TEST' in os.environ:
        USER_DB_FILE = "database_file/test_users.db"
        NOTE_DB_FILE = "database_file/test_notes.db"
        IMAGE_DB_FILE = "database_file/test_images.db"
    else:
        USER_DB_FILE = "database_file/users.db"
        NOTE_DB_FILE = "database_file/notes.db"
        IMAGE_DB_FILE = "database_file/images.db"


class DatabaseManager:
    """Manages SQLite database connections and operations."""

    @staticmethod
    def execute_query(db_file, query, params=(), fetchone=False, fetchall=False):
        """Execute a query in the specified database."""
        connection = sqlite3.connect(db_file)
        cursor = connection.cursor()

        cursor.execute(query, params)
        result = None
        if fetchone:
            result = cursor.fetchone()
        elif fetchall:
            result = cursor.fetchall()

        connection.commit()
        connection.close()
        return result


class UserManager:
    """Handles user-related database operations."""

    @staticmethod
    def list_users():
        """List all users."""
        query = "SELECT id FROM users;"
        return [x[0] for x in DatabaseManager.execute_query(Config.USER_DB_FILE, query, fetchall=True)]

    @staticmethod
    def verify(user_id, password):
        """Verify user credentials."""
        query = "SELECT pw FROM users WHERE id = ?;"
        result = DatabaseManager.execute_query(Config.USER_DB_FILE, query, (user_id,), fetchone=True)
        return result and result[0] == hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def add_user(user_id, password):
        """Add a new user."""
        query = "INSERT INTO users VALUES (?, ?);"
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        DatabaseManager.execute_query(Config.USER_DB_FILE, query, (user_id.upper(), hashed_password))

    @staticmethod
    def delete_user(user_id):
        """Delete a user and all associated data."""
        # Delete user from users database
        user_query = "DELETE FROM users WHERE id = ?;"
        DatabaseManager.execute_query(Config.USER_DB_FILE, user_query, (user_id,))

        # Delete user's notes
        NoteManager.delete_notes_by_user(user_id)

        # Delete user's images
        ImageManager.delete_images_by_user(user_id)


class NoteManager:
    """Handles note-related database operations."""

    @staticmethod
    def read_notes(user_id):
        """Read all notes for a user."""
        query = "SELECT note_id, timestamp, note FROM notes WHERE user = ?;"
        return DatabaseManager.execute_query(Config.NOTE_DB_FILE, query, (user_id.upper(),), fetchall=True)

    @staticmethod
    def write_note(user_id, note_content):
        """Write a new note."""
        current_timestamp = str(datetime.datetime.now())
        note_id = hashlib.sha256((user_id.upper() + current_timestamp).encode()).hexdigest()
        query = "INSERT INTO notes VALUES (?, ?, ?, ?);"
        DatabaseManager.execute_query(
            Config.NOTE_DB_FILE,
            query,
            (user_id.upper(), current_timestamp, note_content, note_id)
        )

    @staticmethod
    def delete_note(note_id):
        """Delete a note."""
        query = "DELETE FROM notes WHERE note_id = ?;"
        DatabaseManager.execute_query(Config.NOTE_DB_FILE, query, (note_id,))

    @staticmethod
    def delete_notes_by_user(user_id):
        """Delete all notes for a user."""
        query = "DELETE FROM notes WHERE user = ?;"
        DatabaseManager.execute_query(Config.NOTE_DB_FILE, query, (user_id,))

    @staticmethod
    def get_note_owner(note_id):
        """Get the owner of a note."""
        query = "SELECT user FROM notes WHERE note_id = ?;"
        result = DatabaseManager.execute_query(Config.NOTE_DB_FILE, query, (note_id,), fetchone=True)
        return result[0] if result else None


class ImageManager:
    """Handles image-related database operations."""

    @staticmethod
    def record_upload(image_uid, owner, image_name, timestamp):
        """Record an image upload."""
        query = "INSERT INTO images VALUES (?, ?, ?, ?);"
        DatabaseManager.execute_query(
            Config.IMAGE_DB_FILE,
            query,
            (image_uid, owner, image_name, timestamp)
        )

    @staticmethod
    def list_images(owner):
        """List all images for a user."""
        query = "SELECT uid, timestamp, name FROM images WHERE owner = ?;"
        return DatabaseManager.execute_query(Config.IMAGE_DB_FILE, query, (owner,), fetchall=True)

    @staticmethod
    def delete_image(image_uid):
        """Delete an image."""
        query = "DELETE FROM images WHERE uid = ?;"
        DatabaseManager.execute_query(Config.IMAGE_DB_FILE, query, (image_uid,))

    @staticmethod
    def delete_images_by_user(owner):
        """Delete all images for a user."""
        query = "DELETE FROM images WHERE owner = ?;"
        DatabaseManager.execute_query(Config.IMAGE_DB_FILE, query, (owner,))

    @staticmethod
    def get_image_owner(image_uid):
        """Get the owner of an image."""
        query = "SELECT owner FROM images WHERE uid = ?;"
        result = DatabaseManager.execute_query(Config.IMAGE_DB_FILE, query, (image_uid,), fetchone=True)
        return result[0] if result else None