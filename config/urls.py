# config/urls.py
from django.contrib import admin
from django.urls import path, include
from movies import views as movie_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', movie_views.home_view, name='home'),
    path('search/', movie_views.search_view, name='search'),
    path('movie/<int:movie_id>/', movie_views.movie_detail_view, name='movie_detail'),
    path('api/live-search/', movie_views.live_search_api, name='live_search_api'),
]