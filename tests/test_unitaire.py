import unittest
import sqlite3
import hashlib
from database import verify, user_db_file_location, delete_user_from_db

class TestVerify(unittest.TestCase):

    def setUp(self):
        # Mettre à jour la localisation de la base de données pour utiliser en mémoire
        global user_db_file_location
        user_db_file_location = ':memory:'

        # Créer une base de données en mémoire et ajouter des données de test
        self.conn = sqlite3.connect(user_db_file_location)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE users (id TEXT PRIMARY KEY, pw TEXT)''')
        hashed_pw = hashlib.sha256('password123'.encode()).hexdigest()
        self.cursor.execute('''INSERT INTO users (id, pw) VALUES (?, ?)''', ('user1', hashed_pw))
        self.conn.commit()

    def tearDown(self):
        # Fermer la connexion à la base de données
        self.conn.close()

    '''
        Test Unitaire pour la fonction database.verify :
                    -> MDP OK
                    -> MDP NOK
                    -> MDP NC
    '''
    def test_verify_correct_password(self):
        # Appeler la fonction avec des identifiants corrects
        result = verify('ADMIN', 'admin')
        self.assertTrue(result)

    def test_verify_incorrect_password(self):
        # Appeler la fonction avec un mot de passe incorrect
        result = None
        try:
            result = verify('user1', 'wrongpassword')
        except TypeError:
            result = False
        self.assertFalse(result)

    def test_verify_nonexistent_user(self):
        # Appeler la fonction avec un utilisateur inexistant
        result = None
        try:
            result = verify('nonexistent', 'password123')
        except TypeError:
            result = False
        self.assertFalse(result)

        '''
        Test Unitaire pour la fonction database.delete_user_from_db :
        -> USER OK
        -> USER NOK
        '''
    def test_delete_user_exist(self):
        result = delete_user_from_db("TEST")
        self.assertFalse(result)

    def test_delete_user_not_exist(self):
        result = None
        try:
            result = delete_user_from_db("TESTEUR")
        except TypeError:
            result = False
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()