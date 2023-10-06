from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase, Client


User = get_user_model()


class PostURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username="HasNoName")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_exists_at_desired_location(self):
        """Тест доступности публичных страниц любому пользователю."""
        urls_for_test = [
            "/auth/signup/",
            "/auth/login/",
            "/auth/password_reset/",
        ]
        for url in urls_for_test:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_redirect_anonymous(self):
        """Тест перенаправления с приватных страниц анонимного пользователя."""
        urls_for_test = {
            "/auth/password_change/": (
                "/auth/login/?next=/" "auth/password_change/"
            ),
            "/auth/password_change/done/": (
                "/auth/login/?next=/" "auth/password_change/done/"
            ),
        }
        for url, url_redirect in urls_for_test.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, url_redirect)

    def test_urls_exists_at_desired_location_authorized(self):
        """Тест доступности приватных страниц авторизованному пользователю."""
        urls_for_test = [
            "/auth/password_change/",
            "/auth/password_change/done/",
        ]
        for url in urls_for_test:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template_anonymous(self):
        """URL-адрес использует нужный шаблон для публичных страниц."""
        url_templates_names = {
            "/signup/": "users/signup.html",
            "/login/": "users/login.html",
            "/password_change/": "users/password_change_form.html",
            "/password_change/done/": "users/password_change_done.html",
            "/logout/": "users/logged_out.html",
            "/password_reset/": "users/password_reset_form.html",
            "/password_reset/done/": "users/password_reset_done.html",
            "/reset/done/": "users/password_reset_complete.html",
        }
        for address, template in url_templates_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get("/auth" + address)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template_authorized(self):
        """URL-адрес использует нужный шаблон для приватных страниц."""
        url_templates_names = {
            "/password_change/": "users/password_change_form.html",
            "/password_change/done/": "users/password_change_done.html",
        }
        for address, template in url_templates_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get("/auth" + address)
                self.assertTemplateUsed(response, template)
