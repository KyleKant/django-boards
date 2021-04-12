from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.models import User
from django.core import mail
from django.urls import resolve, reverse
from django.test import TestCase


class PasswordResetTests(TestCase):
    def setUp(self):
        url = reverse('password_reset')
        self.response = self.client.get(url)

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)
        pass

    def test_view_function(self):
        view = resolve('/reset/')
        self.assertEquals(view.func.view_class, auth_views.PasswordResetView)
        pass

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')
        pass

    def test_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, PasswordResetForm)
        pass

    def test_form_inputs(self):
        """
        The view must contain two inputs: csrf and email
        """
        self.assertContains(self.response, '<input', 2)
        self.assertContains(self.response, 'type="email"', 1)
        pass


class SuccessfulPasswordResetTests(TestCase):
    def setUp(self):
        url = reverse('password_reset')
        self.response = self.client.post(
            url, {'email': 'donotexist@email.com'})
        pass

    def test_redirection(self):
        """
        Even invalid emails in the database should redirect user to
        'password_reset_done' view
        """
        url = reverse('password_reset_done')
        self.assertRedirects(self.response, url)
        pass

    def test_no_reset_email_sent(self):
        self.assertEquals(0, len(mail.outbox))
        pass


class PasswordResetDoneTests(TestCase):
    def setUp(self):
        url = reverse('password_reset_done')
        self.response = self.client.get(url)
        pass

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)
        pass

    def test_view_function(self):
        view = resolve('/reset/done/')
        self.assertEquals(view.func.view_class,
                          auth_views.PasswordResetDoneView)
        pass


class PasswordResetConfirmTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(
            username='john', email='john@doe.com', password='123')
        """
        create a valid password reset token base on how django creates the
        token internally:
        https://github.com/django/django/blob/1.11.5/django/contrib/auth/forms.py#L280
        """
        self.uid = urlsafe_base64_encode(force_bytes(user.pk))
        self.token = default_token_generator.make_token(user)

        url = reverse('password_reset_confirm', kwargs={
                      'uidb64': self.uid, 'token': self.token})
        self.response = self.client.get(url, follow=True)
        pass

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)
        pass

    def test_view_function(self):
        view = resolve(
            '/reset/{uidb64}/{token}/'.format(
                uidb64=self.uid, token=self.token))
        self.assertEquals(view.func.view_class,
                          auth_views.PasswordResetConfirmView)
        pass

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')
        pass

    def test_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, SetPasswordForm)
        pass

    def test_form_inputs(self):
        """
        The view must contain two inputs: csrf and two password fields
        """
        self.assertContains(self.response, '<input', 3)
        self.assertContains(self.response, 'type="password"', 2)
        pass


class InvalidPasswordResetConfirmTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(
            username='john', email='john@doe.com', password='1234asdf')
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        """
        invalidate the token by changing the password
        """
        user.set_password('asdf1234')
        user.save()

        url = reverse('password_reset_confirm', kwargs={
                      'uidb64': uid, 'token': token})
        self.response = self.client.get(url)
        pass

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)
        pass

    def test_html(self):
        password_reset_url = reverse('password_reset')
        self.assertContains(self.response, 'invalid password reset link')
        self.assertContains(
            self.response, 'href="{0}"'.format(password_reset_url))
        pass


class PasswordResetCompleteTests(TestCase):
    def setUp(self):
        url = reverse('password_reset_complete')
        self.response = self.client.get(url)
        pass

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)
        pass

    def test_view_function(self):
        view = resolve('/reset/complete/')
        self.assertEquals(view.func.view_class,
                          auth_views.PasswordResetCompleteView)
        pass
