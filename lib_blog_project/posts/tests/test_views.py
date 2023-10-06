from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Post, Group, Follow

User = get_user_model()


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username="test_user")
        cls.group_1 = Group.objects.create(
            title="Тестовая группа 1",
            slug="test_slug_1",
            description="Тестовое описание",
        )
        cls.group_2 = Group.objects.create(
            title="Тестовая группа 2",
            slug="test_slug_2",
            description="Тестовое описание",
        )
        cls.post_group_1 = Post.objects.create(
            group=cls.group_1, text="Текст Поста" * 5, author=cls.user
        )
        cls.post_group_2 = Post.objects.create(
            group=cls.group_2, text="Текст Поста" * 5, author=cls.user
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse("posts:index"): "posts/index.html",
            reverse(
                "posts:group_list", kwargs={"slug": self.group_1.slug}
            ): "posts/group_list.html",
            reverse(
                "posts:profile", kwargs={"username": self.user.username}
            ): "posts/profile.html",
            reverse(
                "posts:post_detail", kwargs={"post_id": self.post_group_1.id}
            ): "posts/post_detail.html",
            reverse("posts:post_create"): "posts/create_post.html",
            reverse(
                "posts:post_edit", kwargs={"post_id": self.post_group_1.id}
            ): "posts/create_post.html",
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("posts:index"))
        context_post_list = response.context["page_obj"].object_list
        db_post_list = Post.objects.all()
        self.assertQuerysetEqual(
            db_post_list, context_post_list, transform=lambda x: x
        )

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:group_list", kwargs={"slug": self.group_1.slug})
        )
        context_post_list = response.context["page_obj"].object_list
        db_post_list = self.group_1.posts.all()
        self.assertQuerysetEqual(
            db_post_list, context_post_list, transform=lambda x: x
        )

    def test_group_list_create_correct(self):
        """Посты в разных группах не совпадают."""
        response = self.authorized_client.get(
            reverse("posts:group_list", kwargs={"slug": self.group_1.slug})
        )
        context_post_list = response.context["page_obj"].object_list
        db_post_list = list(self.group_2.posts.all())
        self.assertNotEqual(context_post_list, db_post_list)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:profile", kwargs={"username": self.user.username})
        )
        context_post_list = response.context["page_obj"].object_list
        db_post_list = self.user.posts.all()
        self.assertQuerysetEqual(
            db_post_list, context_post_list, transform=lambda x: x
        )

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                "posts:post_detail", kwargs={"post_id": self.post_group_1.id}
            )
        )
        context_post_deatil = response.context["post"]
        db_post_list = Post.objects.get(pk=self.post_group_1.id)
        self.assertEqual(context_post_deatil, db_post_list)

    def test_create_page_show_correct_context(self):
        """Шаблон create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("posts:post_create"))
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_page_show_correct_context(self):
        """Шаблон edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                "posts:post_edit", kwargs={"post_id": self.post_group_1.id}
            )
        )
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertEqual(response.context["id"], self.post_group_1.id)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username="test_user")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test_slug",
            description="Тестовое описание",
        )
        for i in range(1, 14):
            Post.objects.create(
                group=cls.group, text=f"Текст Поста {i}", author=cls.user
            )

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        """Количество постов на первой странице соответсвует ожидаемому."""
        urls_list = [
            reverse("posts:index"),
            reverse("posts:group_list", kwargs={"slug": self.group.slug}),
            reverse("posts:profile", kwargs={"username": self.user.username}),
        ]
        for url in urls_list:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(len(response.context["page_obj"]), 10)

    def test_second_page_contains_three_records(self):
        """Количество постов на второй странице соответсвует ожидаемому."""
        urls_list = [
            reverse("posts:index"),
            reverse("posts:group_list", kwargs={"slug": self.group.slug}),
            reverse("posts:profile", kwargs={"username": self.user.username}),
        ]
        for url in urls_list:
            with self.subTest(url=url):
                response = self.client.get(url + "?page=2")
                self.assertEqual(len(response.context["page_obj"]), 3)


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user_1 = User.objects.create_user(username="test_user_1")
        cls.user_2 = User.objects.create_user(username="test_user_2")
        cls.author = User.objects.create_user(username="test_author")

    def setUp(self):
        self.client_1 = Client()
        self.client_1.force_login(self.user_1)
        self.client_2 = Client()
        self.client_2.force_login(self.user_2)

    def test_auth_user_follow(self):
        """Авторизованный пользователь может подписаться на автора."""
        follow_count_before = Follow.objects.filter(
            author=self.author, user=self.user_1
        ).count()
        self.client_1.get(
            reverse(
                "posts:profile_follow",
                kwargs={"username": self.author.username},
            )
        )
        follow_count_after = Follow.objects.filter(
            author=self.author, user=self.user_1
        ).count()
        self.assertNotEqual(follow_count_before, follow_count_after)

    def test_auth_user_unfollow(self):
        """Авторизованный пользователь может отписаться на автора."""
        self.client_1.get(
            reverse(
                "posts:profile_follow",
                kwargs={"username": self.author.username},
            )
        )

        follow_count_before = Follow.objects.filter(
            author=self.author, user=self.user_1
        ).count()
        self.client_1.get(
            reverse(
                "posts:profile_unfollow",
                kwargs={"username": self.author.username},
            )
        )

        follow_count_after = Follow.objects.filter(
            author=self.author, user=self.user_1
        ).count()

        self.assertNotEqual(follow_count_before, follow_count_after)

    def test_post_in_feed(self):
        """Новая запись пользователя появляется в ленте подписчика."""
        self.client_1.get(
            reverse(
                "posts:profile_follow",
                kwargs={"username": self.author.username},
            )
        )
        Post.objects.create(text="Тестовый текст поста", author=self.author)
        subscriber_feed = self.client_1.get(reverse("posts:follow_index"))
        sub_feed_list = subscriber_feed.context["page_obj"].object_list
        not_subscriber_feed = self.client_2.get(reverse("posts:follow_index"))
        not_sub_feed_list = not_subscriber_feed.context["page_obj"].object_list
        self.assertNotEqual(sub_feed_list, not_sub_feed_list)
