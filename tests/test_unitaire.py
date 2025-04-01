from database import list_users

import unittest
import sqlite3

# Localisation du fichier de la base de données pour les tests
user_db_file_location = ':memory:'

class TestListUsers(unittest.TestCase):

    def setUp(self):
        # Créer une base de données en mémoire et ajouter des données de test
        self.conn = sqlite3.connect(user_db_file_location)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE users (id INTEGER PRIMARY KEY)''')
        self.cursor.execute('''INSERT INTO users (id) VALUES (1), (2), (3)''')
        self.conn.commit()

    def tearDown(self):
        # Fermer la connexion à la base de données
        self.conn.close()

    def test_list_users(self):
        # Appeler la fonction à tester
        result = list_users()

        # Vérifier que la fonction retourne la liste attendue
        self.assertEqual(result, [1, 2, 3])

if __name__ == '__main__':
    unittest.main()