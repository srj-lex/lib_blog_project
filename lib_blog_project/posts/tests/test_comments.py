from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from posts.models import Post, Comment


User = get_user_model()


class CommentWriteTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create(username="test_user")
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.test_post = Post.objects.create(
            text="Тестовый текст тестового поста", author=cls.user
        )

    def test_create_comment_anon_user(self):
        """Анонимный пользователь не может добавлять комментарии."""
        comment_count = Comment.objects.count()
        form_data = {
            "post": self.test_post.id,
            "text": "Тестовый комментарий",
        }
        self.guest_client.post(
            reverse("posts:add_comment", args=(self.test_post.id,)),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), comment_count)

    def test_create_comment_auth_user(self):
        """Авторизованный пользователь может добавлять комментарии."""
        comment_count = Comment.objects.count()
        form_data = {
            "author": self.user.username,
            "post": self.test_post.id,
            "text": "Тестовый комментарий",
        }
        self.authorized_client.post(
            reverse("posts:add_comment", args=(self.test_post.id,)),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)

        response = self.authorized_client.get(
            reverse("posts:post_detail", args=(self.test_post.id,))
        )
        self.assertIn("comments", response.context.keys())
