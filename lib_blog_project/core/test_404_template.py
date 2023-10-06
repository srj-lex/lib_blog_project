from django.test import TestCase, Client


class TestTemplate404(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.guest_client = Client()

    def test_404_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        response = self.guest_client.get("/unexisting_page/")
        self.assertTemplateUsed(response, "core/404.html")
