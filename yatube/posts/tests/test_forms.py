from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User

User = get_user_model()


class CreatinoFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='tester')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Test title',
            slug='test',
            description='Test description',
        )
        cls.post = Post.objects.create(
            text='Test text',
            author=cls.user,
            group=cls.group,
        )

    def test_valid_form_creates_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Text form',
            'group': CreatinoFormTest.group.id,
        }
        CreatinoFormTest.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_valid_form_edit_post(self):
        form_data = {
            'text': 'Text edit',
            'group': CreatinoFormTest.group.id,
        }
        CreatinoFormTest.authorized_client.post(
            reverse(
                'posts:post_edit', kwargs={'post_id': CreatinoFormTest.post.pk}
            ),
            data=form_data,
            follow=True
        )
        self.assertEqual(
            Post.objects.get(pk=CreatinoFormTest.post.pk).text, 'Text edit'
        )
