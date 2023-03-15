from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UserURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create(username='test_u')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_urls_authorized_redirects(self):
        addresses_redirects = {
            reverse(
                'users:password_change'
            ): '/auth/login/?next=/auth/password_change/',
            reverse(
                'users:password_change_done'
            ): '/auth/login/?next=/auth/password_change/done/'
        }
        for address, redirect in addresses_redirects.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertRedirects(response, redirect)
        response = self.guest_client.get('/auth/logout/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_user_guest_urls_exists_at_desired_location(self):
        templates_pages_names = {
            reverse('users:signup'): HTTPStatus.OK,
            reverse('users:login'): HTTPStatus.OK,
            reverse('users:logout'): HTTPStatus.OK,
            reverse('users:password_reset'): HTTPStatus.OK,
            reverse('users:password_reset_done'): HTTPStatus.OK,
            reverse('users:reset_complete'): HTTPStatus.OK,
        }

        for page, code in templates_pages_names.items():
            with self.subTest(status_code=code):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, code)

    def test_user_authorized_urls_exists_at_desired_location(self):
        templates_pages_names = {
            reverse('users:password_change_done'): HTTPStatus.OK,
            reverse('users:password_change'): HTTPStatus.OK,
        }

        for page, code in templates_pages_names.items():
            with self.subTest(status_code=code):
                response = self.authorized_client.get(page)
                self.assertEqual(response.status_code, code)

    def test_user_pages_use_correct_template(self):
        templates_pages_names = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
            reverse('users:logout'): 'users/logged_out.html',
            reverse('users:password_reset'): 'users/password_reset_form.html',
            reverse('users:password_reset_done'):
                'users/password_reset_done.html',
            reverse('users:reset_complete'):
                'users/password_reset_complete.html',
            reverse(
                'users:reset_confirm', args=['uidb64', 'token']
            ): 'users/password_reset_confirm.html',
        }

        for page, template in templates_pages_names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(page)
                self.assertTemplateUsed(response, template)

    def test_user_authorized_pages_use_correct_template(self):
        templates_pages_names = {
            reverse('users:password_change_done'):
                'users/password_change_done.html',
            reverse('users:password_change'):
                'users/password_change_form.html',
        }

        for page, template in templates_pages_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(page)
                self.assertTemplateUsed(response, template)
