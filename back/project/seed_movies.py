import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from api.models import Movie, Genre

with open('movies.json', 'r') as f:
    data = json.load(f)

for item in data:
    genre_name = item.pop('genre_name')
    genre, _ = Genre.objects.get_or_create(name=genre_name, defaults={'slug': genre_name.lower().replace(' ', '-')})
    
    movie, created = Movie.objects.get_or_create(
        title=item['title'],
        defaults=item
    )
    movie.genres.add(genre)
    movie.save()
    print(f"Added: {movie.title}")
print("Done seeding movies!")
