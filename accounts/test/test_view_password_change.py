from django.test import TestCase

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth import views as auth_view
from django.urls import reverse, resolve


class PasswordChangeTests(TestCase):
    def setUp(self):
        username = 'john'
        password = '1234asdf'
        user = User.objects.create_user(
            username=username, email='john@doe.com', password=password)
        url = reverse('password_change')
        self.client.login(username=username, password=password)
        self.response = self.client.get(url)
        pass

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)
        pass

    def test_url_resolves_correct_view(self):
        view = resolve('/setting/password/')
        self.assertEquals(view.func.view_class, auth_view.PasswordChangeView)
        pass

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')
        pass

    def test_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, PasswordChangeForm)
        pass

    def test_inputs_form(self):
        """
        The view must contain four inputs: csrf, old_password, new_password1,
        new_password2
        """
        self.assertContains(self.response, '<input', 4)
        self.assertContains(self.response, 'type="password', 3)
        pass


class LoginRequiredPasswordChangeTest(TestCase):
    def test_redirection(self):
        url = reverse('password_change')
        login_url = reverse('login')
        response = self.client.get(url)
        self.assertRedirects(response, f'{login_url}?next={url}'.format(
            login_url=login_url, url=url))
        pass


class PasswordChangeTestCase(TestCase):
    """
    Base test case for form processing
    accepts a 'data' dict to POST to the view
    """

    def setUp(self, data={}):
        self.user = User.objects.create_user(
            username='john', email='john@doe.com', password='old_password')
        self.url = reverse('password_change')
        self.client.login(username='john', password='old_password')
        self.response = self.client.post(self.url, data)
        pass


class SucessfulPasswordChangeTest(PasswordChangeTestCase):
    def setUp(self):
        super().setUp({
            'old_password': 'old_password',
            'new_password1': 'new_password',
            'new_password2': 'new_password',
        })
        pass

    def test_redirection(self):
        """
        A valid form submission should redirect the user
        """
        self.assertRedirects(self.response, reverse('password_change_done'))
        pass

    def test_password_changed(self):
        """
        refresh the user instance from to get new password
        hash updated by the change password view
        """
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('new_password'))
        pass

    def test_user_authentication(self):
        """
        Create a new request to an arbitrary page.
        The resulting response should now have an 'user' to its context,
        after a successful sign up.
        """
        response = self.client.get(reverse('home'))
        user = response.context.get('user')
        self.assertTrue(user.is_authenticated)
        pass


class InvalidPasswordChangeTest(PasswordChangeTestCase):
    def test_status_code(self):
        """
        An invalid form submission should return to the same page.
        """
        self.assertEquals(self.response.status_code, 200)
        pass

    def test_form_errors(self):
        form = self.response.context.get('form')
        self.assertTrue(form.errors)
        pass

    def test_didnt_change_password(self):
        """
        refresh the user instance from the database to make sure
        we have the latest data
        """
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('old_password'))
        pass
