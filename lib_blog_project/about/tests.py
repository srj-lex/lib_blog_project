from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_urls_exists_at_desired_location(self):
        """Тест доступности публичных страниц любому пользователю."""
        urls_for_test = ["/about/author/", "/about/tech/"]
        for url in urls_for_test:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        url_templates_names = {
            "/about/author/": "about/author.html",
            "/about/tech/": "about/tech.html",
        }
        for address, template in url_templates_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)


class AboutPagesTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_pages_uses_correct_templates(self):
        """URL-адреса приложения About используют корректные шаблоны."""
        templates_pages_names = {
            "about/author.html": reverse("about:author"),
            "about/tech.html": reverse("about:tech"),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
