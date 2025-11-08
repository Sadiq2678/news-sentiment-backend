from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils import get_sentiment_analysis, get_sentiment_analysis_enhanced, fetch_all_news
from django.shortcuts import render
from django.http import JsonResponse




def all_news(request):
    result = fetch_all_news()
    return JsonResponse({'data': result})


def sentiment_api(request):
    # Use enhanced function to get more articles
    results = get_sentiment_analysis_enhanced()
    return JsonResponse({'data': results, 'count': len(results)})