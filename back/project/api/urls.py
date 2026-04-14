from django.urls import path
from .views.fbv import (
login_view, logout_view, register_view,
    review_list_create, movie_list, user_movie_list_create
)
from .views.cbv import ReviewDetailView, UserMovieDetailView

urlpatterns = [
    # auth
    path('auth/register/', register_view),
    path('auth/login/', login_view),
    path('auth/logout/', logout_view),

    # movies
    path('movies/', movie_list),

    # reviews
    path('movies/<int:movie_id>/reviews/', review_list_create),
    path('reviews/<int:review_id>/', ReviewDetailView.as_view()),

    # user movies
    path('user-movies/', user_movie_list_create),
    path('user-movies/<int:pk>/', UserMovieDetailView.as_view()),
]