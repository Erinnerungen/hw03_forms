from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()
POSTS_FOR_TEST = 15
POST_NUM = 10
REMAINING_POSTS = 5


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        demanded_list = []
        cls.user = User.objects.create_user(username='user1')
        cls.group = Group.objects.create(
            title='Заголовок',
            description='Текст',
            slug='slugtest'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )

        for i in range(POSTS_FOR_TEST):
            demanded_list.append(
                Post(
                    text=f'Текстик {i}',
                    group=cls.group,
                    author=cls.user,
                )
            )
        Post.objects.bulk_create(demanded_list)

        cls.unique_gr = Group.objects.create(
            title='Уникальная группа',
            description='Уникальное описание',
            slug='uniqueslug'
        )
        cls.unique_post = Post.objects.create(
            text='Уникалочка',
            group=cls.unique_gr,
            author=cls.user
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_page_uses_correct_template(self):
        templates_pages = {
            reverse(
                'posts:post_create'
            ): 'posts/create_post.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:index'
            ): 'posts/index.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ): 'posts/create_post.html',
        }
        for address, template in templates_pages.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_index(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertIn('page_obj', response.context)
        self.assertEqual(len(response.context['page_obj']), POST_NUM)

    def test_post_create(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }

        for value, anothervalue in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, anothervalue)

    def test_group_list(self):
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': 'slugtest'}
            )
        )
        self.assertEqual(response.context.get('group').title, 'Заголовок')
        self.assertEqual(response.context.get('group').description, 'Текст')
        self.assertEqual(response.context.get('group').slug, 'slugtest')

    def test_post_detail(self):
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )
        posts = response.context['post']
        self.assertEqual(posts, self.post)

    def test_post_correct_addition_3pages(self):
        post = Post.objects.create(
            text='Текст',
            author=self.user,
            group=self.group
        )
        response_index = self.authorized_client.get(reverse('posts:index'))
        response_group = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            )
        )
        response_profile = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            )
        )
        index = response_index.context['page_obj']
        group = response_group.context['page_obj']
        profile = response_profile.context['page_obj']
        self.assertIn(post, index)
        self.assertIn(post, group)
        self.assertIn(post, profile)

    def test_post_added_correctly_not_in(self):
        posts_count = Post.objects.filter(group=self.group).count()
        post = self.unique_post
        response_profile = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}))
        group = Post.objects.filter(group=self.group).count()
        profile = response_profile.context['page_obj']
        self.assertEqual(group, posts_count)
        self.assertIn(post, profile)


class PaginatorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        demanded_list = []
        cls.guest_client = Client()
        cls.user = User.objects.create(username='user1')
        cls.authorized_user = Client()
        cls.authorized_user.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Тест группа',
            slug='slugtest',
            description='Тест описание'
        )

        for i in range(POSTS_FOR_TEST):
            demanded_list.append(
                Post(
                    text=f'Текстик {i}',
                    group=cls.group,
                    author=cls.user,
                )
            )
        Post.objects.bulk_create(demanded_list)

    def test_correct_page_context_non_login(self):
        pages = (
            reverse('posts:index'),
            reverse('posts:profile', kwargs={'username': self.user.username}),
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        for page in pages:
            response1 = self.guest_client.get(page)
            response2 = self.guest_client.get(page + '?page=2')
            count_posts1 = len(response1.context['page_obj'])
            count_posts2 = len(response2.context['page_obj'])
            self.assertEqual(count_posts1, POST_NUM)
            self.assertEqual(count_posts2, POSTS_FOR_TEST - POST_NUM)
