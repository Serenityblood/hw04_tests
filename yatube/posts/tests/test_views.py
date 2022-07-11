from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Group, Post, User

User = get_user_model()


class PostPagesTest(TestCase):
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
            description='Test description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test text',
            group=cls.group,
        )

    def test_correct_templates_on_pages(self):
        tepmlates_page_names = {
            reverse(
                'posts:main_page'
            ): (
                'posts/index.html'
            ),
            reverse(
                'posts:group_posts_page',
                kwargs={'slug': 'test'}
            ): (
                'posts/group_list.html'
            ),
            reverse(
                'posts:profile',
                kwargs={'username': PostPagesTest.user}
            ): (
                'posts/profile.html'
            ),
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostPagesTest.post.pk}
            ): (
                'posts/post_detail.html'
            ),
            reverse(
                'posts:post_create'
            ): (
                'posts/create_post.html'
            ),
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostPagesTest.post.pk}
            ): (
                'posts/create_post.html'
            ),
        }
        for reverse_name, template in tepmlates_page_names.items():
            with self.subTest(template=template):
                response = PostPagesTest.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_context(self):
        response = (
            PostPagesTest.authorized_client.get(reverse('posts:main_page'))
        )
        first_obj = response.context['page_obj'][0]
        task_text_0 = first_obj.text
        self.assertEqual(task_text_0, 'Test text')

    def test_group_list_context(self):
        response = (
            PostPagesTest.authorized_client.
            get(reverse('posts:group_posts_page', kwargs={'slug': 'test'}))
        )
        self.assertEqual(response.context['group'].title, 'Test title')
        self.assertIsInstance(
            response.context['page_obj'][0].group, type(PostPagesTest.group)
        )

    def test_profile_contex(self):
        response = (
            PostPagesTest.authorized_client.
            get(reverse('posts:profile', kwargs={'username': 'tester'}))
        )
        self.assertEqual(
            response.context['page_obj'][0].author, PostPagesTest.post.author
        )

    def test_post_detail_context(self):
        response = (
            PostPagesTest.authorized_client.
            get(reverse(
                'posts:post_detail', kwargs={'post_id': PostPagesTest.post.pk}
            )
            )
        )
        self.assertEqual(response.context['post'].pk, PostPagesTest.post.pk)

    def test_create_post_context(self):
        response = (
            PostPagesTest.authorized_client.
            get(reverse('posts:post_create'))
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_edit_post_context(self):
        response = (
            PostPagesTest.authorized_client.
            get(reverse(
                'posts:post_edit', kwargs={'post_id': PostPagesTest.post.pk}
            )
            )
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
        self.assertEqual(
            response.context['form'].instance.pk, PostPagesTest.post.pk
        )


class PaginatorViewsTest(TestCase):
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
        for i in range(0, 13):
            Post.objects.create(
                author=cls.user,
                text=('Test title' + str(i)),
                group=cls.group,
            )

    def test_first_page_contains_ten_records(self):
        response = PaginatorViewsTest.authorized_client.get(
            reverse('posts:main_page')
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        response = PaginatorViewsTest.authorized_client.get(
            reverse('posts:main_page') + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_page_group_list(self):
        response = PaginatorViewsTest.authorized_client.get(
            reverse('posts:group_posts_page', kwargs={'slug': 'test'})
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_group_list(self):
        response = PaginatorViewsTest.authorized_client.get(
            reverse(
                'posts:group_posts_page', kwargs={'slug': 'test'}) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_page_profile(self):
        response = PaginatorViewsTest.authorized_client.get(
            reverse(
                'posts:profile', kwargs={'username': 'tester'}
            )
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_profile(self):
        response = PaginatorViewsTest.authorized_client.get(
            reverse(
                'posts:profile', kwargs={'username': 'tester'})
            + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)


class ExistinPostTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='tester')
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group_1 = Group.objects.create(
            title='Test title1',
            slug='test1',
            description='Test description1',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test text',
            group=cls.group_1,
        )
        cls.group_2 = Group.objects.create(
            title='Test title2',
            slug='test2',
            description='Test description2',
        )

    def test_post_exists_on_index(self):
        response = ExistinPostTest.authorized_client.get(
            reverse('posts:main_page')
        )
        self.assertEqual(len(response.context['page_obj'].object_list), 1)

    def test_post_exists_on_group(self):
        response = ExistinPostTest.authorized_client.get(
            reverse('posts:group_posts_page', kwargs={'slug': 'test1'})
        )
        self.assertEqual(len(response.context['page_obj']), 1)

    def test_post_exists_on_profile(self):
        response = ExistinPostTest.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'tester'})
        )
        self.assertEqual(len(response.context['page_obj'].object_list), 1)

    def test_post_exist_on_right_group(self):
        response = ExistinPostTest.authorized_client.get(
            reverse('posts:group_posts_page', kwargs={'slug': 'test2'})
        )
        self.assertEqual(len(response.context['page_obj']), 0)
