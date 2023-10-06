from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from posts.models import Post


User = get_user_model()


class PostsCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="test_user")
        cls.post = Post.objects.create(
            author=cls.user,
            text="Текст тестового поста",
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает новую запись в Post."""
        post_count = Post.objects.count()
        form_data = {
            "author": self.user.username,
            "text": "Тестовый текст",
        }
        self.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertEqual(Post.objects.count(), post_count + 1)

    def test_edit_post(self):
        """Валидная форма редактирует запись в Post."""
        posts_before_edit = Post.objects.count()
        form_data = {
            "text": "Новый тестовый текст",
        }
        self.authorized_client.post(
            reverse("posts:post_edit", args=(self.post.id,)),
            data=form_data,
            follow=True,
        )
        posts_after_edit = Post.objects.count()
        self.assertTrue(
            Post.objects.filter(
                text="Новый тестовый текст", author=self.user
            ).exists()
        )
        self.assertEqual(posts_before_edit, posts_after_edit)
