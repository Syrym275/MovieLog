from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from ..models import Review, UserMovie
from ..serializers.modelS import ReviewSerializer, UserMovieSerializer


# CBV 1 — Retrieve, Update, Delete a single Review (completes CRUD for Review)
class ReviewDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, review_id, user):
        try:
            return Review.objects.get(id=review_id, user=user)
        except Review.DoesNotExist:
            return None

    def get(self, request, review_id):
        review = self.get_object(review_id, request.user)
        if not review:
            return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ReviewSerializer(review)
        return Response(serializer.data)

    def put(self, request, review_id):
        review = self.get_object(review_id, request.user)
        if not review:
            return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ReviewSerializer(review, data=request.data)
        if serializer.is_valid():
            serializer.save(is_edited=True)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, review_id):
        review = self.get_object(review_id, request.user)
        if not review:
            return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# CBV 2 — Retrieve, Update, Delete a single UserMovie entry
class UserMovieDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return UserMovie.objects.get(id=pk, user=user)
        except UserMovie.DoesNotExist:
            return None

    def get(self, request, pk):
        user_movie = self.get_object(pk, request.user)
        if not user_movie:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserMovieSerializer(user_movie)
        return Response(serializer.data)

    def put(self, request, pk):
        user_movie = self.get_object(pk, request.user)
        if not user_movie:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserMovieSerializer(user_movie, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user_movie = self.get_object(pk, request.user)
        if not user_movie:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        user_movie.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)