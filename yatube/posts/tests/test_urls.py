from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from http import HTTPStatus

from ..models import Group, Post, User

User = get_user_model()


class StaticURLTests(TestCase):
    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(
            response.status_code, HTTPStatus.OK, 'Main page falls'
        )


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='tester')
        cls.user2 = User.objects.create_user(username='tester2')
        cls.group = Group.objects.create(
            title='Test title',
            slug='test',
            description='Test description'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test text' * 10,
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.just_client = Client()
        self.just_client.force_login(self.user2)

    def test_hardcore_urls_names_match(self):
        name_args_urls = (
            (
                'posts:main_page',
                (),
                '/'
            ), (
                'posts:group_posts_page',
                (self.group.slug,),
                '/group/test/'
            ), (
                'posts:profile',
                (self.user.username,),
                '/profile/tester/'
            ), (
                'posts:post_detail',
                (self.post.pk,),
                '/posts/' + str(self.post.pk) + '/'
            ), (
                'posts:post_edit',
                (self.post.pk,),
                '/posts/' + str(self.post.pk) + '/edit/'
            ), (
                'post:post_create',
                (),
                '/create/'
            )
        )
        for name, arg, url in name_args_urls:
            with self.subTest(url=url):
                hardcore_response = self.authorized_client.get(url)
                reverse_response = self.authorized_client.get(
                    reverse(name, args=arg)
                )
                self.assertEqual(
                    hardcore_response.resolver_match.url_name,
                    reverse_response.resolver_match.url_name
                )

    def test_non_authorized_users_URLS(self):
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
            ), (
                'posts:post_detail',
                (self.post.pk,)
            ), (
                'posts:post_edit',
                (self.post.pk,)
            ), (
                'posts:post_create',
                ()
            )
        )
        for name, arg in names_args:
            with self.subTest(name=name):
                response = self.client.get(reverse(name, args=arg))
                if name == 'posts:post_edit' or name == 'posts:post_create':
                    self.assertEqual(response.status_code, HTTPStatus.FOUND)
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexsting_page_check(self):
        response = self.client.get('/unexisting_page/')
        self.assertEquals(response.status_code, HTTPStatus.NOT_FOUND)

    def test_author_user_urls(self):
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
            ), (
                'posts:post_detail',
                (self.post.pk,)
            ), (
                'posts:post_edit',
                (self.post.pk,)
            ), (
                'posts:post_create',
                ()
            )
        )
        for name, arg in names_args:
            with self.subTest(name=name):
                response = self.authorized_client.get(reverse(name, args=arg))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authorized_users_URLS(self):
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
            ), (
                'posts:post_detail',
                (self.post.pk,)
            ), (
                'posts:post_edit',
                (self.post.pk,)
            ), (
                'posts:post_create',
                ()
            )
        )
        for name, arg in names_args:
            with self.subTest(name=name):
                response = self.just_client.get(reverse(name, args=arg))
                if name == 'posts:post_edit':
                    self.assertRedirects(response, reverse(
                        'posts:post_detail', args=arg
                    )
                    )
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_template_check(self):
        names_templates = (
            (
                'posts:main_page',
                (),
                'posts/index.html'
            ), (
                'posts:group_posts_page',
                (self.group.slug,),
                'posts/group_list.html'
            ), (
                'posts:profile',
                (self.user.username,),
                'posts/profile.html'
            ), (
                'posts:post_detail',
                (self.post.pk,),
                'posts/post_detail.html'
            ), (
                'posts:post_edit',
                (self.post.pk,),
                'posts/create_post.html'
            ), (
                'post:post_create',
                (),
                'posts/create_post.html'
            )
        )
        for name, arg, template in names_templates:
            with self.subTest(name=name):
                response = self.authorized_client.get(reverse(name, args=arg))
                self.assertTemplateUsed(response, template)
