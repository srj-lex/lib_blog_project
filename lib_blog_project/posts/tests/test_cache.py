from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache

from posts.models import Post


User = get_user_model()


class CommentWriteTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create(username="test_user")
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.post = Post.objects.create(
            text="Тестовый текст тестового поста", author=cls.user
        )

    def test_cache_index_page(self):
        """Кэш главной страницы сохраняется."""
        post_count = Post.objects.count()
        response = self.authorized_client.get(reverse("posts:index"))
        self.post.delete()
        res = len(response.context["page_obj"])
        self.assertEqual(post_count, res)

        cache.clear()
        response = self.authorized_client.get(reverse("posts:index"))
        res = len(response.context["page_obj"])
        self.assertNotEqual(post_count, res)
