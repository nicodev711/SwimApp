from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class FeedItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feed_items')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d/', blank=True)

    def __str__(self):
        return f'Profile of {self.user.username}'


class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class SwimmingSpot(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='swimming_spots')
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    longitude = models.FloatField()
    latitude = models.FloatField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='spots')
    average_rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    average_temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def update_average_rating(self):
        ratings = Rating.objects.filter(swimming_spot=self)
        total_ratings = ratings.aggregate(models.Sum('rating'))['rating__sum']
        num_ratings = ratings.count()
        if num_ratings > 0:
            self.average_rating = total_ratings / num_ratings
        else:
            self.average_rating = 0
        self.save()

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created'])
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('mysite:spot_detail', args=[self.slug])


class Image(models.Model):
    swimming_spot = models.ForeignKey(SwimmingSpot, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='spot_images/')
    ordering = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordering']


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    swimming_spot = models.ForeignKey(SwimmingSpot, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    image = models.ImageField(upload_to='comment_images/', blank=True, null=True)  # Add this field
    created = models.DateField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.swimming_spot.title}"


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    swimming_spot = models.ForeignKey(SwimmingSpot, on_delete=models.CASCADE, related_name='ratings')
    rating = models.DecimalField(max_digits=2, decimal_places=1)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.swimming_spot.update_average_rating()

    def __str__(self):
        return f"Rating {self.rating} for {self.swimming_spot.title}"


class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
