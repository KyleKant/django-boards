from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth.models import User

from django.forms import ModelForm

from ..models import Board, Topic, Post
from ..views import PostUpdateView


class PostUpdateViewTestCase(TestCase):
    """
    Base test case to be used in all 'PostUpdateView' view tests
    """

    def setUp(self):
        self.board = Board.objects.create(
            name='Django', description='Django Boards')
        self.username = 'john'
        self.password = '123'
        user = User.objects.create_user(
            username=self.username, email='john@doe.com', password=self.password)
        self.topic = Topic.objects.create(
            subject='Hello world', board=self.board, starter=user)
        self.post = Post.objects.create(
            message='Today i buy bananas', topic=self.topic, created_by=user)
        self.url = reverse('edit_post', kwargs={
            'pk': self.board.pk,
            'topic_pk': self.topic.pk,
            'post_pk': self.post.pk
        })
        pass


class LoginRequiredPostUpdateViewTests(PostUpdateViewTestCase):
    def test_redirection(self):
        """[summary]
        Test if only logged in users can edit the posts
        [description]
        """
        login_url = reverse('login')
        response = self.client.get(self.url)
        self.assertRedirects(response, '{login_url}?next={url}'.format(
            login_url=login_url, url=self.url))
        pass


class UnauthorizedPostUpdateViewTests(PostUpdateViewTestCase):
    def setUp(self):
        """[summary]
        create a new user different from the one who posted
        [description]
        """
        super().setUp()
        username = 'jane'
        password = '121'
        User.objects.create_user(
            username=username, email='jane@doe.com', password=password)
        self.client.login(username=username, password=password)
        self.response = self.client.get(self.url)
        pass

    def test_status_code(self):
        """[summary]
        A topic should be edited only by the ower
        Unauthorized users should get a 404 response (Page Not Found)
        [description]
        """
        self.assertEquals(self.response.status_code, 404)
        pass


class PostUpdateViewTests(PostUpdateViewTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.get(self.url)
        pass

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)
        pass

    def test_view_class(self):
        view = resolve('/boards/1/topics/1/posts/1/edit/')
        self.assertEquals(view.func.view_class, PostUpdateView)
        pass

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')
        pass

    def test_contain_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, ModelForm)
        pass

    def test_form_inputs(self):
        """[summary]
        The view must contain two inputs: csrf, message textarea
        [description]
        """
        self.assertContains(self.response, '<input', 2)
        self.assertContains(self.response, 'type="text"', 1)
        pass


class SuccessfulPostUpdateViewTests(PostUpdateViewTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(
            self.url, {'message': 'edited message'})
        pass

    def test_redirection(self):
        """[summary]
        A valid form submission should redirect the user
        [description]
        """
        topic_posts_url = reverse('topic_posts', kwargs={
            'pk': self.board.pk, 'topic_pk': self.topic.pk})
        self.assertRedirects(self.response, topic_posts_url)
        pass

    def test_post_change(self):
        self.post.refresh_from_db()
        self.assertEquals(self.post.message, 'edited message')
        pass


class InvalidPostUpdateViewTests(PostUpdateViewTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(self.url, {})
        pass

    def test_status_code(self):
        """[summary]
        An invalid form submission should return to the same page
        [description]
        """
        self.assertEquals(self.response.status_code, 200)
        pass

    def test_form_errors(self):
        form = self.response.context.get('form')
        self.assertTrue(form.errors)
        pass
