from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


User = get_user_model()


class UsersSignUpFormTest(TestCase):
    def setUp(self) -> None:
        self.guest_client = Client()

    def test_signup_client(self):
        """Валидная форма создает нового пользователя в User."""
        tasks_count = User.objects.count()
        print(tasks_count)
        form_data = {
            "first_name": "Ivan",
            "last_name": "Ivanov",
            "username": "default_example",
            "email": "default_example@google.com",
            "password1": "Karabas67T",
            "password2": "Karabas67T",
        }
        self.guest_client.post(
            reverse("users:signup"), data=form_data, follow=True
        )
        self.assertEqual(User.objects.count(), tasks_count + 1)
