from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth.models import User

from ..forms import PostForm
from ..models import Board, Topic, Post
from ..views import reply_topic


class ReplyTopicTestCase(TestCase):
    """
    Base test case to be used in all 'reply_topic' view tests
    """

    def setUp(self):
        self.board = Board.objects.create(
            name='Boards', description='Django Boards')
        self.username = 'john'
        self.password = '123'
        user = User.objects.create_user(
            username=self.username,
            email='john@doe.com',
            password=self.password)
        self.topic = Topic.objects.create(
            subject='Hello, world', board=self.board, starter=user)
        Post.objects.create(message='Hom nay mua chuoi',
                            topic=self.topic, created_by=user)
        self.url = reverse('reply_topic', kwargs={
                           'pk': self.board.pk, 'topic_pk': self.topic.pk})
        pass


class LoginRequiredReplyTopicTests(ReplyTopicTestCase):
    def test_redirection(self):
        login_url = reverse('login')
        self.response = self.client.get(self.url)
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(
            login_url=login_url, url=self.url))


class ReplyTopicTests(ReplyTopicTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.get(self.url)
        pass

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)
        pass

    def test_view_function(self):
        view = resolve('/boards/1/topics/1/reply/')
        self.assertEquals(view.func, reply_topic)
        pass

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')
        pass

    def test_contain_forms(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, PostForm)
        pass

    def test_form_inputs(self):
        '''
        The view must contain two inputs: csrf and message textarea
        '''
        self.assertContains(self.response, '<input', 1)
        self.assertContains(self.response, '<textarea', 1)
        pass


class SuccessfulReplyTopicTests(ReplyTopicTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(self.url, {'message': 'Hello world'})
        pass

    def test_redirection(self):
        '''
        A valid form submission should redirect the user
        '''
        url = reverse('topic_posts', kwargs={
            'pk': self.board.pk,
            'topic_pk': self.topic.pk
        })
        topic_posts_url = '{url}?page=1#2'.format(
            url=url
        )
        self.assertRedirects(self.response, topic_posts_url)
        pass

    def test_reply_created(self):
        '''
        The total post count should be 2
        The one created in the 'ReplyTopicTestCase' setUp
        and another created by the post data in this class
        [description]
        '''
        self.assertEquals(Post.objects.count(), 2)
        pass


class InvalidReplyTopicTests(ReplyTopicTestCase):
    def setUp(self):
        '''
        Submit an empty dict to the 'reply_topic' page
        '''
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(self.url, {})
        pass

    def test_status_code(self):
        '''
        An invalid form submission should return to the same page
        '''
        self.assertEquals(self.response.status_code, 200)
        pass

    def test_form_errors(self):
        form = self.response.context.get('form')
        self.assertTrue(form.errors)
        pass
