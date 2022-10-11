from django.test import TestCase, SimpleTestCase
from django.urls import reverse


class HomeViewTestCase(SimpleTestCase):
    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('tests:home'))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse('tests:home'))
        self.assertEqual(resp.status_code, 200)

        self.assertTemplateUsed(resp, 'main_app/home.html')


class ShowAllTestsListVIewTestCase(TestCase):
    # create 13 tests, with questions and users
    def setUpTestData(cls):
        pass
