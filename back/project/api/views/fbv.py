from django.db import models
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from ..models import Review, Movie, UserMovie
from ..serializers.modelS import ReviewSerializer, MovieSerializer, UserMovieSerializer

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from ..serializers.simpleS import LoginSerializer, RegisterSerializer

# FBV 1 — List all reviews for a movie + Create a review 
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def review_list_create(request, movie_id):
    try:
        movie = Movie.objects.get(id=movie_id)
    except Movie.DoesNotExist:
        return Response({'error': 'Movie not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        reviews = Review.objects.for_movie(movie)   # custom manager
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        if not request.user or not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
            
        if Review.objects.filter(user=request.user, movie=movie).exists():
            return Response({'non_field_errors': ['You have already reviewed this movie.']}, status=status.HTTP_400_BAD_REQUEST)
            
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, movie=movie)  # link to authenticated user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# FBV 2 — List all movies
@api_view(['GET'])
@permission_classes([AllowAny])
def movie_list(request):
    query = request.query_params.get('search', None)
    genre = request.query_params.get('genre', None)
    is_top = request.query_params.get('top_rated', None)

    # Base query depending on 'top_rated' manager
    if is_top == 'true':
        movies = Movie.objects.top_rated()
    else:
        movies = Movie.objects.all()

    # Chain other filters
    if query:
        movies = movies.filter(
            models.Q(title__icontains=query) |
            models.Q(description__icontains=query)
        )
    if genre:
        # Since Movie.objects.by_genre is on manager, we apply filter directly 
        # to allow chaining with top_rated()
        movies = movies.filter(genres__slug=genre)

    serializer = MovieSerializer(movies, many=True)
    return Response(serializer.data)


# FBV 3 — Get or create UserMovie status
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def user_movie_list_create(request):
    if request.method == 'GET':
        user_movies = UserMovie.objects.filter(user=request.user)
        serializer = UserMovieSerializer(user_movies, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        movie_id = request.data.get('movie')
        status_val = request.data.get('status', 'want_to_watch')
        
        # Prevent duplicates, update existing instead
        obj, created = UserMovie.objects.update_or_create(
            user=request.user, 
            movie_id=movie_id,
            defaults={'status': status_val}
        )
        serializer = UserMovieSerializer(obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

# FBV 4 — Update or Delete specific UserMovie entry
@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def user_movie_detail(request, pk):
    try:
        user_movie = UserMovie.objects.get(pk=pk, user=request.user)
    except UserMovie.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = UserMovieSerializer(user_movie, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        user_movie.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

# ---------------------- Token Based Authentication -----------------------------

@api_view(['POST'])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    request.user.auth_token.delete()  # deletes the token from DB
    return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = User.objects.create_user(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        token = Token.objects.create(user=user)
        return Response({'token': token.key}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
