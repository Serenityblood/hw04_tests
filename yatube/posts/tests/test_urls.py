from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post, User

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200, 'Main page falls')


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='tester')
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
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

    def test_non_authorized_users_URLS(self):
        page_list = [
            '/',
            '/group/test/',
            '/profile/tester/',
            '/posts/' + str(PostsURLTests.post.pk) + '/',
        ]
        for url in page_list:
            with self.subTest(url=url):
                response = PostsURLTests.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_unexsting_page_check(self):
        response = PostsURLTests.guest_client.get('/unexisting_page/')
        self.assertEquals(response.status_code, 404)

    def test_authorized_users_URLS(self):
        page_list = [
            '/create/',
            '/posts/' + str(PostsURLTests.post.pk) + '/edit/'
        ]
        for url in page_list:
            with self.subTest(url=url):
                response = PostsURLTests.authorized_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_template_check(self):
        urls_templates = {
            '/': 'posts/index.html',
            '/group/test/': 'posts/group_list.html',
            '/posts/' + str(PostsURLTests.post.pk) + '/': (
                'posts/post_detail.html'
            ),
            '/posts/' + str(PostsURLTests.post.pk) + '/edit/': (
                'posts/create_post.html'
            ),
            '/create/': 'posts/create_post.html',
        }
        for url, template in urls_templates.items():
            with self.subTest(url=url):
                response = PostsURLTests.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
