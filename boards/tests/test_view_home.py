from django.test import TestCase
from django.urls import reverse
from django.urls import resolve
from ..views import BoardListView
from ..models import Board

# Create your tests here.


class HomeTest(TestCase):
    def setUp(self):
        self.board = Board.objects.create(
            name='Django', description='Django Board')
        url = reverse('home')
        self.response = self.client.get(url)
        pass

    def test_home_view_contains_link_to_topics_page(self):
        board_topics_url = reverse(
            'board_topics', kwargs={'pk': self.board.pk})
        self.assertContains(
            self.response, 'href="{0}"'.format(board_topics_url))
        pass

    def test_home_view_status_code(self):
        self.assertEquals(self.response.status_code, 200)
        pass

    def test_home_url_resolves_home_view(self):
        view = resolve('/')
        self.assertEquals(view.func.view_class, BoardListView)
        pass
