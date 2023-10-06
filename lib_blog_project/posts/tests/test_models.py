from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post, CHARS_IN_STR


User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username="test_user")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="Тестовый слаг",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user, text="Тестовый пост" * 3, group=cls.group
        )

    def test_model_group_have_correct_object_names(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        group = self.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_group_verbose_name(self):
        """verbose_name в полях Group совпадает с ожидаемым."""
        group = self.group
        field_verboses = {
            "title": "Имя",
            "slug": "Адрес",
            "description": "Описание",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value
                )

    def test_group_help_text(self):
        """help_text в полях Group совпадает с ожидаемым."""
        group = self.group
        field_help_texts = {
            "title": "Имя группы",
            "slug": "Ссылка для доступа к группе",
            "description": "Описание группы",
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).help_text, expected_value
                )

    def test_model_post_have_correct_object_names(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        post = self.post
        expected_object_name = post.text[:CHARS_IN_STR]
        self.assertEqual(expected_object_name, str(post))

    def test_post_verbose_name(self):
        """verbose_name в полях Post совпадает с ожидаемым."""
        post = self.post
        field_verboses = {
            "text": "Текст",
            "pub_date": "Дата публикации",
            "author": "Автор",
            "group": "Группа",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value
                )

    def test_post_help_text(self):
        """help_text в полях Post совпадает с ожидаемым."""
        post = self.post
        field_help_texts = {
            "text": "Введите текст поста",
            "author": "Автор поста",
            "group": "Группа, к которой будет относиться пост",
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value
                )
