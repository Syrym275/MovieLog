import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Movie, Review, UserMovie } from '../interfaces/movie.interface';

@Injectable({ providedIn: 'root' })
export class MovieService {
  private apiUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  getMovies(search?: string, genre?: string, topRated?: boolean): Observable<Movie[]> {
    let params = new HttpParams();
    if (search) params = params.set('search', search);
    if (genre) params = params.set('genre', genre);
    if (topRated) params = params.set('top_rated', 'true');
    return this.http.get<Movie[]>(`${this.apiUrl}/movies/`, { params });
  }

  getReviews(movieId: number): Observable<Review[]> {
    return this.http.get<Review[]>(`${this.apiUrl}/movies/${movieId}/reviews/`);
  }

  createReview(movieId: number, body: string, rating: number): Observable<Review> {
    return this.http.post<Review>(`${this.apiUrl}/movies/${movieId}/reviews/`, { body, rating });
  }

  updateReview(reviewId: number, body: string, rating: number): Observable<Review> {
    return this.http.put<Review>(`${this.apiUrl}/reviews/${reviewId}/`, { body, rating });
  }

  deleteReview(reviewId: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/reviews/${reviewId}/`);
  }

  getUserMovies(): Observable<UserMovie[]> {
    return this.http.get<UserMovie[]>(`${this.apiUrl}/user-movies/`);
  }

  trackMovie(movieId: number, status: string): Observable<UserMovie> {
    return this.http.post<UserMovie>(`${this.apiUrl}/user-movies/`, { movie: movieId, status });
  }

  updateUserMovieStatus(userMovieId: number, status: string): Observable<UserMovie> {
    return this.http.put<UserMovie>(`${this.apiUrl}/user-movies/${userMovieId}/`, { status });
  }

  deleteUserMovie(userMovieId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/user-movies/${userMovieId}/`);
  }
}
