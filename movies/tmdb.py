# movies/tmdb.py
import requests
from django.conf import settings

TMDB_BASE = 'https://api.themoviedb.org/3'


def tmdb_get(endpoint, params=None):
    if params is None:
        params = {}
    params['api_key'] = settings.TMDB_API_KEY
    params['language'] = 'en-US'

    try:
        response = requests.get(f'{TMDB_BASE}{endpoint}', params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"TMDB error: {e}")
        return None


def search_movies(query, page=1):
    return tmdb_get('/search/movie', {'query': query, 'page': page})


def get_movie_details(movie_id):
    return tmdb_get(f'/movie/{movie_id}', {'append_to_response': 'videos,credits'})


def get_trending_movies():
    return tmdb_get('/trending/movie/day')


def get_movie_trailer(movie_id):
    details = get_movie_details(movie_id)
    if not details:
        return None
    videos = details.get('videos', {}).get('results', [])
    trailers = [v for v in videos if v.get('type') == 'Trailer' and v.get('site') == 'YouTube']
    if trailers:
        return trailers[0].get('key')
    return None