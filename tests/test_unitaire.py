"""
Unit tests for the User API.
"""

import unittest
from flask import Flask
from app import app  # Ensure 'app' module is correctly installed and accessible

class TestUserAPI(unittest.TestCase):
    """Test cases for User API endpoints."""

    def setUp(self):
        """Configuration exécutée avant chaque test."""
        # Création d'un client de test pour simuler les requêtes HTTP
        self.client = app.test_client()
        # Connexion en tant qu'administrateur pour les tests
        self.client.post("/login", data={"id": "ADMIN", "pw": "admin"})

    def tearDown(self):
        """Nettoyage exécuté après chaque test."""
        # Supprimer les utilisateurs ajoutés pendant les tests
        self.client.get("/delete_user/Alice/")
        self.client.get("/delete_user/Bob/")

    def test_get_users(self):
        """Vérifie que la route '/admin/' retourne un statut 200 (OK)."""
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)

    def test_add_user(self):
        """Vérifie que l'ajout d'un utilisateur retourne un statut 200"""
        response = self.client.post("/add_user", data={"id": "Alice", "pw": "password"})
        self.assertEqual(response.status_code, 200)

    def test_delete_user(self):
        """Vérifie que la suppression d'un utilisateur retourne un statut 302 (redirection)."""
        # Ajouter un utilisateur avant de le supprimer
        self.client.post("/add_user", data={"id": "Bob", "pw": "password"})
        # Supprimer l'utilisateur ajouté
        response = self.client.get("/delete_user/Bob/")
        self.assertEqual(response.status_code, 302)

    def test_login(self):
        """Vérifie que la connexion d'un utilisateur retourne un statut 302 (redirection)."""
        response = self.client.post("/login", data={"id": "Alice", "pw": "password"})
        self.assertEqual(response.status_code, 302)

    def test_logout(self):
        """Vérifie que la déconnexion retourne un statut 302 (redirection)."""
        response = self.client.get("/logout/")
        self.assertEqual(response.status_code, 302)

    def test_write_note(self):
        """Vérifie que l'écriture d'une note retourne un statut 302 (redirection)."""
        response = self.client.post(
            "/write_note", data={"text_note_to_take": "This is a test note"}
        )
        self.assertEqual(response.status_code, 302)

    def test_401_error(self):
        """Vérifie que la route '/private/' retourne un statut 401 pour un utilisateur non connecté."""
        self.client.get("/logout/")
        response = self.client.get("/private/")
        self.assertEqual(response.status_code, 401)

    def test_403_error(self):
        """Vérifie que la suppression de l'utilisateur 'ADMIN' retourne un statut 403."""
        response = self.client.get("/delete_user/ADMIN/")
        self.assertEqual(response.status_code, 403)

    def test_404_error(self):
        """Vérifie qu'une route inexistante retourne un statut 404."""
        response = self.client.get("/nonexistent_route")
        self.assertEqual(response.status_code, 404)

    def test_405_error(self):
        """Vérifie qu'une méthode non autorisée retourne un statut 405."""
        response = self.client.post("/admin/")
        self.assertEqual(response.status_code, 405)

    def test_413_error(self):
        """Vérifie qu'un fichier trop volumineux retourne un statut 413."""
        with open("large_test_file.jpg", "wb") as f:
            f.seek(1024 * 1024 * 100)  # 100 MB
            f.write(b"\0")
        with open("large_test_file.jpg", "rb") as img:
            response = self.client.post("/upload_image", data={"file": img})
        self.assertEqual(response.status_code, 413)

if __name__ == "__main__":
    unittest.main()