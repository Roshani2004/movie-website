# movies/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .tmdb import search_movies, get_movie_details, get_trending_movies, get_movie_trailer
from django.http import JsonResponse

@login_required
def home_view(request):
    data = get_trending_movies()
    movies = data.get('results', []) if data else []
    return render(request, 'movies/home.html', {'movies': movies})


@login_required
def search_view(request):
    query = request.GET.get('q', '').strip()
    movies = []
    if query:
        data = search_movies(query)
        movies = data.get('results', []) if data else []
    return render(request, 'movies/search.html', {'movies': movies, 'query': query})


@login_required
def movie_detail_view(request, movie_id):
    details = get_movie_details(movie_id)
    if not details:
        return render(request, 'movies/detail.html', {'movie': None}, status=404)

    trailer_key = get_movie_trailer(movie_id)
    return render(request, 'movies/detail.html', {
        'movie': details,
        'trailer_key': trailer_key,
    })


@login_required
def live_search_api(request):
    """AJAX endpoint for live search dropdown"""
    query = request.GET.get('q', '').strip()
    results = []
    if query:
        data = search_movies(query)
        if data and 'results' in data:
            # Get top 5 results for dropdown
            for movie in data['results'][:5]:
                results.append({
                    'id': movie.get('id'),
                    'title': movie.get('title'),
                    'year': movie.get('release_date', '')[:4] if movie.get('release_date') else 'N/A',
                    'rating': movie.get('vote_average', 'N/A'),
                    'poster': f"https://image.tmdb.org/t/p/w92{movie.get('poster_path')}" if movie.get('poster_path') else 'https://via.placeholder.com/92x138?text=No+Img'
                })
    return JsonResponse({'results': results})

@login_required
def search_view(request):
    query = request.GET.get('q', '').strip()
    
    if query:
        data = search_movies(query)
    else:
        # Show trending if no search query
        data = get_trending_movies()
        
    movies = data.get('results', []) if data else []
    
    # Fetch genres for display
    genre_map = {28: 'Action', 12: 'Adventure', 16: 'Animation', 35: 'Comedy', 80: 'Crime', 99: 'Documentary', 18: 'Drama', 10751: 'Family', 14: 'Fantasy', 36: 'History', 27: 'Horror', 10402: 'Music', 9648: 'Mystery', 10749: 'Romance', 878: 'Sci-Fi', 10770: 'TV Movie', 53: 'Thriller', 10752: 'War', 37: 'Western'}
    for movie in movies:
        if 'genre_ids' in movie and movie['genre_ids']:
            movie['genre_name'] = genre_map.get(movie['genre_ids'][0], 'Movie')
        else:
            movie['genre_name'] = 'Movie'

    return render(request, 'movies/search.html', {'movies': movies, 'query': query})

@login_required
def home_view(request):
    data = get_trending_movies()
    movies = data.get('results', []) if data else []
    
    # Take the top 5 movies to feature in the Hero Banner
    featured_movies = movies[:5] if len(movies) >= 5 else movies
    
    return render(request, 'movies/home.html', {
        'movies': movies,
        'featured_movies': featured_movies
    })