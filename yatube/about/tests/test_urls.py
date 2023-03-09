from django.test import TestCase, Client


class StaticPagesURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test1_about_url_exists_at_desired_location(self):
        response = self.guest_client.get('/page/about/author')
        self.assertEqual(response.status_code, 200)

    def test1_about_url_uses_correct_template(self):
        response = self.guest_client.get('/page/about/author')
        self.assertTemplateUsed(response, 'about/author.html')

    def test2_about_url_exists_at_desired_location(self):
        response = self.guest_client.get('/page/about/tech')
        self.assertEqual(response.status_code, 200)

    def test2_about_url_uses_correct_template(self):
        response = self.guest_client.get('/page/about/tech')
        self.assertTemplateUsed(response, 'about/tech.html')
