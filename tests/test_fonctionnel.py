import hashlib
import unittest
from unittest.mock import patch, MagicMock
import database

class TestDatabaseFunctions(unittest.TestCase):

    @patch('database.sqlite3.connect')
    def test_list_users(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(1,), (2,)]

        result = database.list_users()
        self.assertEqual(result, [1, 2])

    @patch('database.sqlite3.connect')
    def test_verify(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [hashlib.sha256("password".encode()).hexdigest()]

        result = database.verify("user_id", "password")
        self.assertTrue(result)

    @patch('database.sqlite3.connect')
    def test_delete_user_from_db(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        database.delete_user_from_db("user_id")
        self.assertTrue(mock_cursor.execute.called)

    @patch('database.sqlite3.connect')
    def test_add_user(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        database.add_user("user_id", "password")
        self.assertTrue(mock_cursor.execute.called)

    @patch('database.sqlite3.connect')
    def test_read_note_from_db(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(1, '2025-04-07 20:26:54', 'note')]

        result = database.read_note_from_db("user_id")
        self.assertEqual(result, [(1, '2025-04-07 20:26:54', 'note')])

    @patch('database.sqlite3.connect')
    def test_write_note_into_db(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        database.write_note_into_db("user_id", "note")
        self.assertTrue(mock_cursor.execute.called)

    @patch('database.sqlite3.connect')
    def test_delete_note_from_db(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        database.delete_note_from_db("note_id")
        self.assertTrue(mock_cursor.execute.called)

    @patch('database.sqlite3.connect')
    def test_image_upload_record(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        database.image_upload_record("uid", "owner", "image_name", "timestamp")
        self.assertTrue(mock_cursor.execute.called)

    @patch('database.sqlite3.connect')
    def test_list_images_for_user(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(1, '2025-04-07 20:26:54', 'name')]

        result = database.list_images_for_user("owner")
        self.assertEqual(result, [(1, '2025-04-07 20:26:54', 'name')])

    @patch('database.sqlite3.connect')
    def test_delete_image_from_db(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        database.delete_image_from_db("image_uid")
        self.assertTrue(mock_cursor.execute.called)

if __name__ == "__main__":
    unittest.main()