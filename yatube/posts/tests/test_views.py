from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Group, Post, User
from ..forms import PostForm

User = get_user_model()


class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='tester')
        cls.group = Group.objects.create(
            title='Test title',
            slug='test',
            description='Test description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test text',
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.new_group = Group.objects.create(
            title='Test title 2',
            slug='testing',
            description='Test description 2',
        )
        self.new_post = Post.objects.create(
            author=self.user,
            text='Test text 2',
            group=self.group
        )

    def pages_tests(self, response, some_bool=False):
        if not some_bool:
            context_data = response.context['page_obj'][1]
            value_exp = {
                context_data.text: self.post.text,
                context_data.group.title: self.post.group.title,
                context_data.pub_date: self.post.pub_date
            }
            for value, expected in value_exp.items():
                with self.subTest(value=value):
                    self.assertEqual(value, expected)
        if some_bool:
            context_data = response.context['post']
            value_exp = {
                context_data.text: self.post.text,
                context_data.group.title: self.post.group.title,
                context_data.pub_date: self.post.pub_date
            }
            for value, expected in value_exp.items():
                with self.subTest(value=value):
                    self.assertEqual(value, expected)

    def test_index_context(self):
        response = (
            self.authorized_client.get(reverse('posts:main_page'))
        )
        self.pages_tests(response)

    def test_group_list_context(self):
        response = (
            self.authorized_client.
            get(reverse('posts:group_posts_page', args=(self.group.slug,)))
        )
        self.pages_tests(response)
        self.assertIsInstance(
            response.context['page_obj'][1].group, type(self.group)
        )

    def test_profile_contex(self):
        response = (
            self.authorized_client.
            get(reverse('posts:profile', args=(self.user.username,)))
        )
        self.pages_tests(response)
        self.assertEqual(
            response.context['page_obj'][1].author, self.post.author
        )

    def test_post_detail_context(self):
        response = (
            self.authorized_client.
            get(reverse(
                'posts:post_detail', args=(self.post.pk,)
            )
            )
        )
        self.pages_tests(response, True)
        self.assertEqual(response.context['post'].pk, self.post.pk)

    def test_right_group_with_post(self):
        response_1 = self.authorized_client.get(
            reverse('posts:group_posts_page', args=(self.new_group.slug,))
        )
        self.assertEqual(
            len(response_1.context['page_obj'].object_list), 0
        )
        response_2 = self.authorized_client.get(
            reverse('posts:group_posts_page', args=(self.group.slug,))
        )
        self.assertEqual(
            len(response_2.context['page_obj'].object_list), 2
        )

    def test_post_create_edit_context(self):
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        names_args = (
            (
                'posts:post_create',
                ()
            ), (
                'posts:post_edit',
                (self.post.pk,)
            )
        )
        for name, arg in names_args:
            with self.subTest(name=name):
                response = self.authorized_client.get(
                    reverse(name, args=arg)
                )
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], PostForm)
                for value, expected in form_fields.items():
                    with self.subTest(value=value):
                        form_field = response.context['form'].fields[value]
                        self.assertIsInstance(form_field, expected)
                        if name == 'posts:post_edit':
                            self.assertEqual(
                                response.context['form'].instance.pk,
                                self.post.pk
                            )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='tester')
        cls.group = Group.objects.create(
            title='Test title',
            slug='test',
            description='Test description'
        )
        for post_number in range(0, settings.POSTS_NUMBER):
            Post.objects.create(
                author=cls.user,
                text=(f'Test title {post_number}'),
                group=cls.group,
            )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_records_on_pages(self):
        names_args = (
            (
                'posts:main_page',
                ()
            ), (
                'posts:group_posts_page',
                (self.group.slug,)
            ), (
                'posts:profile',
                (self.user.username,)
            )
        )
        pages_posts = (
            ('?page=1', settings.PAGE_NUMBER),
            ('?page=2', 3)
        )
        for name, arg in names_args:
            with self.subTest(name=name):
                for page, posts in pages_posts:
                    with self.subTest(page=page):
                        response = self.authorized_client.get(
                            reverse(name, args=arg) + page
                        )
                        self.assertEqual(
                            len(response.context['page_obj']), posts
                        )
