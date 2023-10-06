from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user_1 = User.objects.create_user(username="test_user_1")
        cls.user_2 = User.objects.create_user(username="test_user_2")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test_slug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user_1, text="Тестовый пост" * 3, group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_1 = Client()
        self.authorized_client_1.force_login(self.user_1)
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)

    def test_urls_exists_at_desired_location(self):
        """Тест доступности публичных страниц любому пользователю."""
        urls_for_test = [
            "/",
            f"/group/{self.group.slug}/",
            f"/profile/{self.user_1.username}/",
            f"/posts/{self.post.id}/",
        ]
        for url in urls_for_test:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_redirect_anonymous(self):
        """Тест перенаправления с приватных страниц анонимного пользователя."""
        post_id = self.post.id
        urls_for_test = {
            "/create/": "/auth/login/?next=/create/",
            f"/posts/{post_id}/edit/": (
                "/auth/login/?next=/" f"posts/{post_id}/edit/"
            ),
        }
        for url, url_redirect in urls_for_test.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, url_redirect)

    def test_create_url_exists_at_desired_location_authorized(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client_1.get("/create/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_url_exists_at_desired_location_authorized(self):
        """Страница /posts/post_id/edit/ доступна автору поста."""
        post_id = self.post.id
        response = self.authorized_client_1.get(f"/posts/{post_id}/edit/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_url_redirect_authorized(self):
        """Страница /posts/post_id/edit/ не доступна авторизованному
        пользователю и перенаправляет его."""
        post_id = self.post.id
        response = self.authorized_client_2.get(
            f"/posts/{post_id}/edit/", follow=True
        )
        self.assertRedirects(response, f"/posts/{post_id}/")

    def test_unexisting_page_get_404(self):
        """Несуществующая страница /unexisting_page/ вернет ошибку 404."""
        response = self.authorized_client_1.get("/unexisting_page/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        url_templates_names = {
            "/": "posts/index.html",
            f"/group/{self.group.slug}/": "posts/group_list.html",
            f"/profile/{self.user_1.username}/": "posts/profile.html",
            f"/posts/{self.post.id}/": "posts/post_detail.html",
            "/create/": "posts/create_post.html",
            f"/posts/{self.post.id}/edit/": "posts/create_post.html",
        }
        for address, template in url_templates_names.items():
            with self.subTest(address=address):
                response = self.authorized_client_1.get(address)
                self.assertTemplateUsed(response, template)
