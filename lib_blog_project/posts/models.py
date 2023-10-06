from django.db import models
from django.contrib.auth import get_user_model

from core.models import CreatedModel


User = get_user_model()

CHARS_IN_STR = 15


class Group(models.Model):
    title = models.CharField(
        max_length=200, verbose_name="Имя", help_text="Имя группы"
    )
    slug = models.SlugField(
        unique=True,
        verbose_name="Адрес",
        help_text="Ссылка для доступа к группе",
    )
    description = models.TextField(
        verbose_name="Описание", help_text="Описание группы"
    )

    class Meta:
        verbose_name = "сообщество"
        verbose_name_plural = "сообщества"

    def __str__(self) -> str:
        return self.title


class Post(CreatedModel):
    text = models.TextField(
        verbose_name="Текст",
        help_text="Введите текст поста",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Автор",
        help_text="Автор поста",
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="posts",
        verbose_name="Группа",
        help_text="Группа, к которой будет относиться пост",
    )
    image = models.ImageField(
        verbose_name="Картинка", upload_to="posts/", blank=True
    )

    class Meta:
        verbose_name = "запись"
        verbose_name_plural = "записи"
        ordering = ["-pub_date"]

    def __str__(self) -> str:
        return self.text[:CHARS_IN_STR]


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Пост",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор поста",
    )
    text = models.TextField(
        verbose_name="Текст комментария",
    )

    class Meta:
        verbose_name = "комментарий"
        verbose_name_plural = "комментарии"
        ordering = ["-pub_date"]

    def __str__(self) -> str:
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписчик",
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Автор",
    )

    class Meta:
        verbose_name = "Подписки"
        verbose_name_plural = "Подписки"
        ordering = ["-user"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], name="uq_user_author"
            )
        ]

    def __str__(self) -> str:
        return self.author.username
