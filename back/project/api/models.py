from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name'] # default sort order, without it, the order is unpredictable.

# Custom Model Manager
class MovieManager(models.Manager):

    def by_genre(self, genre_slug):
        return self.filter(genres__slug=genre_slug) # slug - genre column, __ - lookup field

    def by_year(self, year):
        return self.filter(release_year=year)

    def search(self, query):
        return self.filter(
            models.Q(title__icontains=query) |
            models.Q(description__icontains=query)
        )

    def top_rated(self):
        return self.annotate(
            avg_score=models.Avg('reviews__rating')
        ).filter(
            avg_score__gte=8.0
        ).order_by('-avg_score', '-imdb_rating')

class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    release_year = models.PositiveIntegerField()
    poster_url = models.URLField(blank=True)
    trailer_url = models.URLField(blank=True)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    imdb_id = models.CharField(max_length=20, unique=True, blank=True)
    imdb_rating = models.DecimalField(
        max_digits=3, decimal_places=1, null=True, blank=True
    )
    language = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    genres = models.ManyToManyField(Genre, related_name='movies', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = MovieManager()

    def __str__(self):
        return f"{self.title} ({self.release_year})"

    class Meta:
        ordering = ['-release_year']


# Custom Model Manager
class UserMovieManager(models.Manager):
    
    def for_movie(self, movie):
        return self.filter(movie=movie).select_related('user')

    def by_user(self, user):
        return self.filter(user=user).select_related('movie')

    def top_rated(self):
        return self.filter(rating__gte=8).order_by('-rating') # by rating descending order
    

class UserMovie(models.Model):

    class Status(models.TextChoices):
        WANT_TO_WATCH = 'want_to_watch', 'Want to Watch'
        WATCHING = 'watching', 'Watching'
        WATCHED = 'watched', 'Watched'
        DROPPED = 'dropped', 'Dropped'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_movies')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='user_movies')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.WANT_TO_WATCH)
    is_favourite = models.BooleanField(default=False)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    watched_at = models.DateField(null=True, blank=True)
    times_watched = models.PositiveIntegerField(default=0)

    objects = UserMovieManager()

    def __str__(self):
        return f"{self.user.username} - {self.movie.title} ({self.status})"

    class Meta:
        unique_together = ('user', 'movie') # combination of these two models must be unique
        ordering = ['-added_at']

# Custom Model Manager
class ReviewManager(models.Manager):

    def for_movie(self, movie):
        return self.filter(movie=movie).select_related('user')

    def by_user(self, user):
        return self.filter(user=user).select_related('movie')

    def top_rated(self):
        return self.filter(rating__gte=8).order_by('-rating')
    

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    title = models.CharField(max_length=255, blank=True)
    body = models.TextField()
    contains_spoilers = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ReviewManager()

    def __str__(self):
        return f"{self.user.username} reviewed {self.movie.title} — {self.rating}/10"

    class Meta:
        unique_together = ('user', 'movie')
        ordering = ['-created_at']


class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='notes')
    content = models.TextField()
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Note by {self.user.username} on {self.movie.title}"

    class Meta:
        ordering = ['-is_pinned', '-created_at']


class WatchList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlists')
    movies = models.ManyToManyField(Movie, related_name='watchlists', blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s list: {self.name}"

    class Meta:
        ordering = ['-created_at']


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar_url = models.URLField(blank=True)
    bio = models.TextField(blank=True, max_length=500)
    favourite_genre = models.ForeignKey(
        Genre, on_delete=models.SET_NULL, null=True, blank=True
    )
    is_private = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
    

# Some of the rare concepts that we used and their short definitions
"""
The Meta class is where you give Django instructions about the model itself, not about any individual field. 
Think of it as model-level configuration.

1. blank vs null  = True

null -  this is a database level setting. 
It tells the database that this column is allowed to store NULL

blank - this is a Django/form validation level setting. 
It tells Django that this field is allowed to be empty when validating a form or serializer. 
(Has nothing to do with the database)


2. auto_now_add vs auto_now

auto_now_add - sets the value once, at the moment the object is first created. Never changes after that.

auto_now - sets the value every time the object is saved( .save() operator). So it updates on every edit.
"""