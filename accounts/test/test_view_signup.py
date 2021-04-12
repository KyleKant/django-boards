from django.test import TestCase
from django.urls import reverse, resolve
from ..views import signup
from ..forms import SignUpForm
from django.contrib.auth.models import User
# Create your tests here.


class SignUpTests(TestCase):
    def test_sign_up_status_code(self):
        url = reverse('signup')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        pass

    def test_sign_up_urls_resolves_sign_up_view(self):
        view = resolve('/signup/')
        self.assertEquals(view.func, signup)
        pass

    def setUp(self):
        url = reverse('signup')
        self.response = self.client.get(url)
        pass

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')
        pass

    def test_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, SignUpForm)
        pass

    def test_forms_inputs(self):
        '''
        The view must contain five inputs: csrf, username, email, password1,
        password2
        '''
        self.assertContains(self.response, '<input', 5)
        self.assertContains(self.response, 'type="text"', 1)
        self.assertContains(self.response, 'type="email"', 1)
        self.assertContains(self.response, 'type="password"', 2)
        pass


class SuccessfulSignUpTests(TestCase):
    def setUp(self):
        url = reverse('signup')
        data = {
            'username': 'john',
            'email': 'john@doe.com',
            'password1': 'asdf1234!',
            'password2': 'asdf1234!'
        }
        self.response = self.client.post(url, data)
        self.home_url = reverse('home')
        pass

    def test_redirection(self):
        '''
        A valid form submission should redirect the user to the home page
        '''
        self.assertRedirects(self.response, self.home_url)
        pass

    def test_user_creation(self):
        self.assertTrue(User.objects.exists())
        pass

    def test_user_authentication(self):
        '''
        Create a new request to an arbitrary page
        The resulting response should now have a 'user' to its context,
        after a successful sign up.
        '''
        response = self.client.get(self.home_url)
        user = response.context.get('user')
        self.assertTrue(user.is_authenticated)
        pass


class InvalidSignUpTest(TestCase):
    def setUp(self):
        url = reverse('signup')
        self.response = self.client.post(url, {}) # submit an empty dictionary
        pass

    def test_signup_status_code(self):
        '''
        An invalid form submission should return to the same page
        '''
        self.assertEquals(self.response.status_code, 200)
        pass

    def test_form_errors(self):
        form = self.response.context.get('form')
        self.assertTrue(form.errors)
        pass

    def test_dont_create_user(self):
        self.assertFalse(User.objects.exists())
        pass
