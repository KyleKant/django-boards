from django.contrib import admin
from .models import Board, Topic

# Register your models here.


class TopicInline(admin.TabularInline):

    list_filter = ['subject']

    search_fields = ['subject']

    model = Topic
    # extra = 5


class BoardAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'id')

    list_filter = ['name', 'description']

    search_fields = ['name']

    inlines = [TopicInline]


admin.site.register(Board, BoardAdmin)
