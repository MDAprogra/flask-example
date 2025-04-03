import unittest
from flask import Flask, session, request, url_for
from app import app

# Classe de test pour l'API utilisateur
class TestUserAPI(unittest.TestCase):
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
        """Vérifie que l'ajout d'un utilisateur retourne un statut 302 (redirection)."""
        response = self.client.post("/add_user", data={"id": "Alice", "pw": "password"})
        self.assertEqual(response.status_code, 302)

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

if __name__ == "__main__":
    unittest.main()