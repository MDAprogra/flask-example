"""
Unit tests for the User API.

setUp : Cette méthode est exécutée avant chaque test. Elle crée un client de test pour simuler les requêtes HTTP et se connecte en tant qu'administrateur.
tearDown : Cette méthode est exécutée après chaque test. Elle nettoie les données en supprimant les utilisateurs ajoutés pendant les tests.
test_get_users : Vérifie que la route /admin/ retourne un statut 200 (OK).
test_add_user : Vérifie que l'ajout d'un utilisateur retourne un statut 200 (OK).
test_delete_user : Vérifie que la suppression d'un utilisateur retourne un statut 302 (redirection).
test_login : Vérifie que la connexion d'un utilisateur retourne un statut 302 (redirection).
test_logout : Vérifie que la déconnexion retourne un statut 302 (redirection).
test_write_note : Vérifie que l'écriture d'une note retourne un statut 302 (redirection).
test_401_error : Vérifie que la route /private/ retourne un statut 401 pour un utilisateur non connecté.
test_403_error : Vérifie que la suppression de l'utilisateur ADMIN retourne un statut 403.
test_404_error : Vérifie qu'une route inexistante retourne un statut 404.
test_405_error : Vérifie qu'une méthode non autorisée retourne un statut 405.
test_413_error : Vérifie qu'un fichier trop volumineux retourne un statut 413.
test_FUN_root : Vérifie que la route / retourne un statut 200 (OK).
test_FUN_public : Vérifie que la route /public/ retourne un statut 200 (OK).
test_FUN_private : Vérifie que la route /private/ retourne un statut 200 (OK) pour un utilisateur connecté.
test_allowed_file : Vérifie que la fonction allowed_file retourne True pour des fichiers autorisés et False pour des fichiers non autorisés.
test_FUN_delete_user : Vérifie que la suppression d'un utilisateur retourne un statut 302 (redirection).
test_FUN_add_user : Vérifie que l'ajout d'un utilisateur retourne un statut 200 (OK).
"""

import unittest
import os
import datetime
import hashlib
from flask import Flask, session
from app import app, allowed_file  # Ensure 'app' module is correctly installed and accessible
from database import list_images_for_user, read_note_from_db  # Import the necessary functions

class TestUserAPI(unittest.TestCase):
    """Test cases for User API endpoints."""

    def setUp(self):
        """Configuration exécutée avant chaque test."""
        # Création d'un client de test pour simuler les requêtes HTTP
        self.client = app.test_client()
        # Connexion en tant qu'administrateur pour les tests
        self.client.post("/login", data={"id": "ADMIN", "pw": "admin"})
        with self.client.session_transaction() as sess:
            sess['current_user'] = 'ADMIN'

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
            f.seek(1024 * 1024 * 100 - 1)  # 100 MB - 1 byte
            f.write(b"\0")
        with open("large_test_file.jpg", "rb") as img:
            response = self.client.post("/upload_image", data={"file": img})
        self.assertEqual(response.status_code, 413)
        os.remove("large_test_file.jpg")

    def test_FUN_root(self):
        """Vérifie que la route '/' retourne un statut 200 (OK)."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_FUN_public(self):
        """Vérifie que la route '/public/' retourne un statut 200 (OK)."""
        response = self.client.get("/public/")
        self.assertEqual(response.status_code, 200)

    def test_FUN_private(self):
        """Vérifie que la route '/private/' retourne un statut 200 (OK) pour un utilisateur connecté."""
        response = self.client.get("/private/")
        self.assertEqual(response.status_code, 200)

    def test_allowed_file(self):
        """Vérifie que la fonction 'allowed_file' retourne True pour des fichiers autorisés."""
        self.assertTrue(allowed_file("test.png"))
        self.assertTrue(allowed_file("test.jpg"))
        self.assertTrue(allowed_file("test.jpeg"))
        self.assertTrue(allowed_file("test.gif"))
        self.assertFalse(allowed_file("test.txt"))
        self.assertFalse(allowed_file("test.pdf"))

    def test_FUN_delete_user(self):
        """Vérifie que la suppression d'un utilisateur retourne un statut 302 (redirection)."""
        # Ajouter un utilisateur avant de le supprimer
        self.client.post("/add_user", data={"id": "Charlie", "pw": "password"})
        # Supprimer l'utilisateur ajouté
        response = self.client.get("/delete_user/Charlie/")
        self.assertEqual(response.status_code, 302)

    def test_FUN_add_user(self):
        """Vérifie que l'ajout d'un utilisateur retourne un statut 200"""
        response = self.client.post("/add_user", data={"id": "David", "pw": "password"})
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()