from django.urls import path
from . import views

urlpatterns = [
    
    path('api_sentiments/', views.sentiment_api, name='sentiment_api'),
    path('all_news/', views.all_news, name='all_news')
]
