from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class CreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='anon')
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.user_no_author = User.objects.create(username='noauth')
        cls.authorized_client_no_author = Client()
        cls.authorized_client_no_author.force_login(cls.user_no_author)
        cls.group = Group.objects.create(
            title='Тест заголовок',
            description='Тест текст',
            slug='first'
        )

    def test_createdpost_auth(self):
        post_content = {
            'text': 'Пост',
            'group': self.group.pk
        }

        posts_before_creating = Post.objects.count()

        self.authorized_client.post(
            reverse('posts:post_create'),
            data=post_content,
        )
        posts_after_creating = Post.objects.count()
        post = Post.objects.select_related('group', 'author').get()

        self.assertEqual(post_content['text'], post.text)
        self.assertEqual(post_content['group'], post.group.pk)
        self.assertEqual(self.user, post.author)
        self.assertEqual(
            posts_before_creating + 1,
            posts_after_creating
        )

    def test_auth_post_without_gr(self):
        post_content = {
            'text': 'Безгрупный пост'
        }

        posts_before_creating = Post.objects.count()

        self.authorized_client.post(
            reverse('posts:post_create'),
            data=post_content
        )

        posts_after_creating = Post.objects.count()
        post = Post.objects.select_related('group', 'author').get()

        self.assertEqual(post_content['text'], post.text)
        self.assertEqual(post.group, None)
        self.assertEqual(self.user, post.author)
        self.assertEqual(
            posts_before_creating + 1,
            posts_after_creating
        )

    def test_createpost_noauth(self):
        post_content = {
            'text': 'Пост',
            'group': self.group.pk
        }

        posts_before_creating = Post.objects.count()

        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=post_content
        )
        posts_after_creating = Post.objects.count()

        self.assertEqual(
            posts_before_creating,
            posts_after_creating
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.FOUND
        )

    def test_postauth(self):
        crpost = Post.objects.create(
            text='Текст',
            author=self.user,
            group=self.group
        )

        post_edited = {
            'text': 'редактировано',
            'group': self.group.pk
        }

        self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': crpost.id}),
            data=post_edited
        )

        edited_post = Post.objects.select_related('group', 'author').get()

        self.assertEqual(edited_post.pub_date, crpost.pub_date)
        self.assertEqual(edited_post.author, crpost.author)
        self.assertEqual(edited_post.text, post_edited['text'])
        self.assertEqual(edited_post.group.pk, post_edited['group'])

    def test_post_notauth(self):
        crpost = Post.objects.create(
            text='Текст',
            author=self.user,
            group=self.group
        )

        post_edited = {
            'text': 'редактировано',
            'group': self.group.pk
        }

        response = self.guest_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': crpost.id}),
            data=post_edited
        )

        edited_post = Post.objects.select_related('group', 'author').get()

        self.assertEqual(edited_post.pub_date, crpost.pub_date)
        self.assertEqual(edited_post.author, crpost.author)
        self.assertEqual(edited_post.text, crpost.text)
        self.assertEqual(edited_post.group.pk, crpost.group.pk)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_auth(self):
        crpost = Post.objects.create(
            text='Текст',
            author=self.user,
            group=self.group
        )

        post_edited = {
            'text': 'редактировано',
            'group': self.group.pk
        }

        response = self.guest_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': crpost.id}),
            data=post_edited
        )

        edited_post = Post.objects.select_related('group', 'author').get()

        self.assertEqual(edited_post.pub_date, crpost.pub_date)
        self.assertEqual(edited_post.author, crpost.author)
        self.assertEqual(edited_post.text, crpost.text)
        self.assertEqual(edited_post.group.pk, crpost.group.pk)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
