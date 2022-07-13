from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from http import HTTPStatus

from ..models import Group, Post, User

User = get_user_model()


class CreatinoFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='tester')
        cls.group = Group.objects.create(
            title='Test title',
            slug='test',
            description='Test description',
        )
        cls.group_edit = Group.objects.create(
            title='Test title edit',
            slug='test-edit',
            description='Test description edit',
        )
        cls.post = Post.objects.create(
            text='Test text',
            group=cls.group,
            author=cls.user,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_valid_form_creates_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Text form',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        post_created = Post.objects.get(pk=2)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(post_created.text, 'Text form')
        self.assertEqual(post_created.group.title, 'Test title')
        self.assertRedirects(response, reverse(
            'posts:profile', args=(post_created.author,)
        )
        )

    def test_valid_form_edit_post(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'Text edit',
            'group': self.group_edit.id,
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit', args=(self.post.pk,)
            ),
            data=form_data,
            follow=True
        )
        post_edit = Post.objects.get(pk=self.post.pk)
        self.assertRedirects(response, reverse(
            'posts:post_detail', args=(post_edit.pk,)
        )
        )
        self.assertEqual(post_edit.author, self.user)
        self.assertEqual(post_edit.text, 'Text edit')
        self.assertEqual(post_edit.group.title, 'Test title edit')
        group_response = self.authorized_client.get(
            reverse(
                'posts:group_posts_page', args=(self.group.slug,)
            )
        )
        self.assertEqual(group_response.status_code, HTTPStatus.OK)
        self.assertEqual(
            group_response.context['page_obj'].object_list.count(),
            0
        )
        self.assertEqual(Post.objects.count(), post_count)

    def test_guest_cant_create_post(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'Guest text',
            'group': self.group.id,
        }
        self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count)
