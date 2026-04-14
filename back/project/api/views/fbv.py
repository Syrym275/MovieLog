from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..models import Review, Movie, UserMovie
from ..serializers.modelS import ReviewSerializer, MovieSerializer, UserMovieSerializer

from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from ..serializers.simpleS import LoginSerializer, RegisterSerializer

# FBV 1 — List all reviews for a movie + Create a review 
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def review_list_create(request, movie_id):
    movie = Movie.objects.get(id=movie_id)

    if request.method == 'GET':
        reviews = Review.objects.for_movie(movie)   # custom manager
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, movie=movie)  # link to authenticated user, r8
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# FBV 2 — List all movies
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def movie_list(request):
    query = request.query_params.get('search', None)
    genre = request.query_params.get('genre', None)

    movies = Movie.objects.all()

    if query:
        movies = Movie.objects.search(query)    # custom manager
    if genre:
        movies = Movie.objects.by_genre(genre)  # custom manager

    serializer = MovieSerializer(movies, many=True)
    return Response(serializer.data)


# FBV 3 — Get or update UserMovie status (want/watching/watched)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def user_movie_list_create(request):
    if request.method == 'GET':
        user_movies = UserMovie.objects.filter(user=request.user)
        serializer = UserMovieSerializer(user_movies, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = UserMovieSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # link to authenticated user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

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
