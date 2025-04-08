"""
Performance tests for the web application using Locust.
"""

from locust import HttpUser, TaskSet, task, between

class UserBehavior(TaskSet):
    """
    Defines the behavior of a simulated user.
    """

    def on_start(self):
        """
        Méthode appelée lorsqu'un utilisateur Locust commence à s'exécuter.
        Elle permet de connecter l'utilisateur pour configurer la session.
        """
        self.login()

    def login(self):
        """
        Simule l'action de connexion pour configurer la session.
        """
        self.client.post("/login", data={"id": "test_user", "pw": "password"})

    @task(1)
    def index(self):
        """
        Tâche pour charger la page d'accueil.
        """
        self.client.get("/")

    @task(2)
    def public(self):
        """
        Tâche pour charger la page publique.
        """
        self.client.get("/public/")

    @task(3)
    def private(self):
        """
        Tâche pour charger la page privée.
        """
        self.client.get("/private/")

    @task(4)
    def write_note(self):
        """
        Tâche pour simuler l'écriture d'une note.
        """
        self.client.post(
            "/write_note",
            data={"text_note_to_take": "Performance test note"}
        )

    @task(5)
    def delete_note(self):
        """
        Tâche pour simuler la suppression d'une note.
        """
        # Cela suppose qu'une note avec l'ID '1' existe pour l'utilisateur
        self.client.get("/delete_note/1")

    @task(6)
    def upload_image(self):
        """
        Tâche pour simuler le téléchargement d'une image.
        """
        with open("test.jpg", "rb") as image_file:
            self.client.post(
                "/upload_image",
                files={"file": ("test.jpg", image_file, "image/jpeg")}
            )

    @task(7)
    def delete_image(self):
        """
        Tâche pour simuler la suppression d'une image.
        """
        # Cela suppose qu'une image avec l'UID 'fakehash' existe pour l'utilisateur
        self.client.get("/delete_image/fakehash")

    @task(8)
    def admin(self):
        """
        Tâche pour charger la page d'administration.
        """
        self.client.get("/admin/")

class WebsiteUser(HttpUser):
    """
    Defines a simulated website user.
    """
    tasks = [UserBehavior]
    wait_time = between(1, 5)
    host = "http://localhost:5000"  # Ajoutez votre hôte de base ici
    