from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse, resolve

from ..models import Board
from ..views import new_board
from ..forms import NewBoardForm


class NewBoardTests(TestCase):
    def setUp(self):
        username = 'testuser'
        password = '123'
        User.objects.create_user(
            username=username, email='testuser@doe.com', password=password)
        self.client.login(username=username, password=password)
        pass

    def test_new_board_view_success_status_code(self):
        url = reverse('new_board')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        pass

    def test_new_board_url_resolve_new_board_view(self):
        view = resolve('/board/new_board/')
        self.assertEquals(view.func, new_board)
        pass

    def test_new_board_view_contain_link_back_forward_home_view(self):
        new_board_url = reverse('new_board')
        home_url = reverse('home')
        response = self.client.get(new_board_url)
        self.assertContains(response, 'href={0}'.format(home_url))
        pass

    def test_csrf(self):
        url = reverse('new_board')
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')
        pass

    def test_new_board_valid_post_data(self):
        url = reverse('new_board')
        data = {
            'name': 'new board test',
            'description': 'discuss about new board test'
        }
        self.client.post(url, data)
        self.assertTrue(Board.objects.exists())
        pass

    def test_new_board_invalid_post_data(self):
        url = reverse('new_board')
        data = {}
        response = self.client.post(url, data)
        form = response.context.get('form')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)
        pass

    def test_new_board_invalid_post_data_empty_fields(self):
        url = reverse('new_board')
        data = {
            'name': '',
            'description': ''
        }
        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(Board.objects.exists())
        pass
