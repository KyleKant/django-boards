from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse, resolve

from ..views import new_topics
from ..models import Board, Topic, Post
from ..forms import NewTopicForm

# # Create your tests here.


class NewTopicTests(TestCase):
    def setUp(self):
        Board.objects.create(name='Django', description='Django Board')
        User.objects.create_user(
            username='john', email='join@doe.com', password='121')
        self.client.login(username='john', password='121')
        pass

    def test_new_topic_view_success_status_code(self):
        url = reverse('new_topics', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        pass

    def test_new_topic_view_not_found_status_code(self):
        url = reverse('new_topics', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)
        pass

    def test_new_topic_url_resolve_new_topic_view(self):
        view = resolve('/boards/1/new/')
        self.assertEquals(view.func, new_topics)
        pass

    def test_new_topic_view_contain_link_back_forward_board_topic_view(self):
        new_topic_url = reverse('new_topics', kwargs={'pk': 1})
        board_topics_url = reverse('board_topics', kwargs={'pk': 1})
        response = self.client.get(new_topic_url)
        self.assertContains(response, 'href="{0}"'.format(board_topics_url))
        pass

    def test_board_topics_view_contain_nagivation_link(self):
        board_topics_url = reverse('board_topics', kwargs={'pk': 1})
        homepage_url = reverse('home')
        new_topic_url = reverse('new_topics', kwargs={'pk': 1})
        response = self.client.get(board_topics_url)
        self.assertContains(response, 'href="{0}"'.format(homepage_url))
        self.assertContains(response, 'href="{0}"'.format(new_topic_url))
        pass

    def test_csrf(self):
        url = reverse('new_topics', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')
        pass

    def test_contains_form(self):
        url = reverse('new_topics', kwargs={'pk': 1})
        response = self.client.get(url)
        form = response.context.get('form')
        self.assertIsInstance(form, NewTopicForm)
        pass

    def test_new_topic_valid_post_data(self):
        url = reverse('new_topics', kwargs={'pk': 1})
        data = {
            'subject': 'Test title',
            'message': 'hom nay mua con ca chuoi'
        }
        self.client.post(url, data)
        # self.assertEquals(response.status_code, 200)
        self.assertTrue(Topic.objects.exists())
        self.assertTrue(Post.objects.exists())
        pass

    def test_new_topic_invalid_post_data(self):
        '''
        Invalid post data shouldn't redirect
        The expected behavior is to show the form again with validation errors
        '''
        url = reverse('new_topics', kwargs={'pk': 1})
        response = self.client.post(url, {})
        form = response.context.get('form')
        self. assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)
        pass

    def test_new_topic_invalid_post_data_empty_fields(self):
        '''
        Invalid post data shouldn't redirect
        The expected behavior sis to show the form again with validation errors
        '''
        url = reverse('new_topics', kwargs={'pk': 1})
        data = {
            'subject': '',
            'message': ''
        }
        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(Topic.objects.exists())
        self.assertFalse(Post.objects.exists())
        pass


class LoginRequiredNewTopicTests(TestCase):
    def setUp(self):
        Board.objects.create(name='Django', description='Boards')
        self.url = reverse('new_topics', kwargs={'pk': 1})
        self.response = self.client.get(self.url)
        pass

    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(
            login_url=login_url, url=self.url))
        pass
