from django.contrib import admin
from .models import *


# Register your models here.
@admin.register(Subscriber)
class Subscriber(admin.ModelAdmin):
    list_display = ['email', 'subscribed_at']


@admin.register(Profile)
class Profile(admin.ModelAdmin):
    list_display = ['user', 'date_of_birth', 'photo']
    raw_id_fields = ['user']


@admin.register(SwimmingSpot)
class SwimmingSpotAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'slug', 'category', 'longitude', 'latitude', 'average_rating',
                    'average_temperature']
    list_filter = ['user', 'created', 'updated', 'category']
    search_fields = ['user', 'title', 'body']
    raw_id_fields = ['user', 'category']
    date_hierarchy = 'created'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['swimming_spot', 'text']
    list_filter = ['swimming_spot', 'text']
    search_fields = ['swimming_spot__title', 'text']
    raw_id_fields = ['swimming_spot']


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'swimming_spot', 'rating']
    list_filter = ['user', 'swimming_spot', 'rating']
    search_fields = ['user__username', 'swimming_spot__title']
    raw_id_fields = ['user', 'swimming_spot']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug']
    search_fields = ['name']


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'swimming_spot']
    search_fields = ['swimming_spot']
