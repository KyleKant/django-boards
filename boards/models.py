import math

from django.db import models
import uuid
from django.contrib.auth.models import User
from django.utils.text import Truncator
from django.utils.html import mark_safe
from markdown import markdown

# Create your models here.


class Board(models.Model):
    """
    Description: Model Description
    """
    name = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.name
        pass

    def get_posts_count(self):
        return Post.objects.filter(topic__board=self).count()
        pass

    def get_last_post(self):
        return Post.objects.filter(
            topic__board=self).order_by('-created_at').first()
        pass


class Topic(models.Model):
    """
    Description: Model Description
    """
    subject = models.CharField(max_length=255)
    last_updated = models.DateTimeField(auto_now_add=True)
    board = models.ForeignKey(
        Board, on_delete=models.CASCADE, related_name='topics')
    starter = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='topics')
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.subject

    def get_page_count(self):
        count = self.posts.count()
        pages = count / 5
        return math.ceil(pages)

    def has_many_pages(self, count=None):
        if count is None:
            count = self.get_page_count()
        return count > 6

    def get_page_range(self):
        count = self.get_page_count()
        if self.has_many_pages(count):
            return range(1, 5)
        return range(1, count + 1)

    def get_last_ten_posts(self):
        return Post.objects.order_by('-created_at')[:10]


class Post(models.Model):
    """
    Description: Model Description
    """
    message = models.CharField(max_length=4000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
    topic = models.ForeignKey(
        Topic, on_delete=models.CASCADE, related_name='posts')
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='posts')
    updated_by = models.ForeignKey(
        User, null=True, on_delete=models.CASCADE, related_name='+')

    def __str__(self):
        truncated_message = Truncator(self.message)
        return truncated_message.chars(30)
        pass

    def get_message_as_markdown(self):
        return mark_safe(markdown(self.message, safe_mode='escape'))
        pass
