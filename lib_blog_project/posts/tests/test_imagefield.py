import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model

from posts.models import Post, Group


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ImageViewsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username="test_user")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test_slug",
            description="Тестовое описание",
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.byte_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        cls.image = SimpleUploadedFile(
            name="small.gif", content=cls.byte_gif, content_type="image/gif"
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Test text post",
            image=cls.image,
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_image_in_page_context(self):
        """Изображение присутствует в контексте страниц."""
        url_context_list = [
            (
                "posts:index",
                {},
            ),
            (
                "posts:profile",
                {"username": self.user.username},
            ),
            (
                "posts:group_list",
                {"slug": self.group.slug},
            ),
        ]
        for url, kwargs in url_context_list:
            with self.subTest(url=url):
                response = self.authorized_client.get(
                    reverse(url, kwargs=kwargs)
                )
                context_image = (
                    response.context["page_obj"].object_list[0].image
                )
                self.assertEqual(context_image, self.post.image)

    def test_image_in_post_detail_context(self):
        """Изображение присутствует в контексте страницы post_detail."""
        response = self.authorized_client.get(
            reverse("posts:post_detail", kwargs={"post_id": self.post.id})
        )
        context_image = response.context["post"].image
        self.assertEqual(context_image, self.post.image)

    def test_create_post(self):
        """Валидная форма создает новую запись в Post."""
        post_count = Post.objects.count()
        form_data = {
            "author": self.user.username,
            "text": "Тестовый текст",
            "image": self.image,
        }
        self.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
