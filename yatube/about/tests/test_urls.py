from http import HTTPStatus

from django.test import Client, TestCase


class StaticPagesURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_urls_exist_at_desired_location(self):
        urls = [
            '/about/author/',
            '/about/tech/'
        ]
        for address in urls:
            response = self.guest_client.get(address)
            self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_urls_use_correct_template(self):
        templates_urls = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/'
        }

        for template, address in templates_urls.items():
            response = self.guest_client.get(address)
            self.assertTemplateUsed(response, template)
