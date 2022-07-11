from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='tester')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост' * 10,
        )

    def test_models_have_correct_objects_name(self):
        """Проверяем что у моделей корректно работает __str__"""
        group = PostModelTest.group
        post = PostModelTest.post
        post_str_exp = post.text[:settings.TEXT_SIZE_NUMBER]
        group_str_exp = group.title
        self.assertEqual(post_str_exp, str(post))
        self.assertEqual(group_str_exp, str(group))
