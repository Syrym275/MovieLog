from rest_framework import serializers
from ..models import Movie, Review, UserMovie, Genre


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'


class MovieSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()
    times_added = serializers.SerializerMethodField()

    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return None

    def get_total_reviews(self, obj):
        return obj.reviews.count()

    def get_times_added(self, obj):
        return obj.user_movies.count()

    class Meta:
        model = Movie
        fields = [
            'id', 'title', 'description', 'release_year',
            'poster_url', 'trailer_url', 'duration_minutes',
            'imdb_id', 'imdb_rating', 'language', 'country',
            'genres', 'average_rating', 'total_reviews', 'times_added',
            'created_at'
        ]

# The reason we didn't use __all__ here is because we added custom columns that 
# are not specified as model fields


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'username', 'movie', 'rating', 'title',
            'body', 'contains_spoilers', 'is_edited',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'movie', 'is_edited', 'created_at', 'updated_at']


class UserMovieSerializer(serializers.ModelSerializer):
    movie_title = serializers.CharField(source='movie.title', read_only=True)
    movie_poster = serializers.CharField(source='movie.poster_url', read_only=True)

    class Meta:
        model = UserMovie
        fields = [
            'id', 'movie', 'movie_title', 'movie_poster',
            'status', 'is_favourite', 'watched_at',
            'times_watched', 'added_at', 'updated_at'
        ]
        read_only_fields = ['user', 'added_at', 'updated_at']

