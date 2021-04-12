from django.test import TestCase
from django.urls import reverse
from django.urls import resolve
from ..views import TopicListView
from ..models import Board

# Create your tests here.


class BoardTopicsTests(TestCase):
    def setUp(self):
        Board.objects.create(name='Django', description='Django Board')
        pass

    def test_board_topics_view_contains_link_to_home_page(self):
        board_topics_url = reverse('board_topics', kwargs={'pk': 1})
        response = self.client.get(board_topics_url)
        homepage_url = reverse('home')
        self.assertContains(response, 'href="{0}"'.format(homepage_url))
        pass

    def test_board_topics_view_success_status_code(self):
        url = reverse('board_topics', kwargs={'pk': 1})
        response = self.client.get(url)
        return self.assertEquals(response.status_code, 200)
        pass

    def test_board_topics_view_not_found_status_code(self):
        url = reverse('board_topics', kwargs={'pk': 99})
        response = self.client.get(url)
        return self.assertEquals(response.status_code, 404)
        pass

    def test_board_topics_urls_resolse_board_topics_view(self):
        view = resolve('/boards/1/')
        self.assertEquals(view.func.view_class, TopicListView)
        pass
