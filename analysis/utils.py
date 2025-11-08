import requests
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col, concat, lit
from pyspark.sql.types import StringType
from django.http import JsonResponse

def sentiment_view(request):
    return JsonResponse({'message': 'Sentiment endpoint works!'})

nltk.download('vader_lexicon')

def get_sentiment_analysis():
    analyzer = SentimentIntensityAnalyzer()
    spark = SparkSession.builder.master("local[*]").appName("NewsSentiment").getOrCreate()
    
    def get_sentiment(text):

        if not text:
            return "Neutral"
        score = analyzer.polarity_scores(text)['compound']
        if score >= 0.05:
            return "Positive"
        elif score <= -0.05:
            return "Negative"
        else:
            return "Neutral"
    
    sentiment_udf = udf(get_sentiment, StringType())
    url = "https://newsdata.io/api/1/latest"

# Parameters - removing size as it may not be supported in free tier
    params = {
    "apikey": "pub_0623eb3fbe6a42f89077c65a8860fe24",  
    "language": "en"
}

    response = requests.get(url, params=params)
    data = response.json()
    articles_raw = data.get("results", [])

    seen_titles = set()
    new_articles = []
    for article in articles_raw:
        title = article.get("title", "")
        if title and title not in seen_titles:
            seen_titles.add(title)
            new_articles.append({
                "title": title,
                "description": article.get("description", "")
            })

    if not new_articles:
        return []

    df = spark.createDataFrame(new_articles)
    df = df.withColumn("text", concat(col("title"), lit(" "), col("description")))
    df = df.withColumn("sentiment", sentiment_udf(col("text")))

    results = df.select("title", "sentiment").toPandas().to_dict(orient="records")
    spark.stop()
    return results

def fetch_all_news():
     url = "https://newsdata.io/api/1/latest"

# Parameters - removing size as it may not be supported in free tier
     params = {
    "apikey": "pub_0623eb3fbe6a42f89077c65a8860fe24",  
    "language": "en"
} 
     response = requests.get(url, params=params)
     data = response.json()
     return data

def get_sentiment_analysis_enhanced():
    """Get sentiment analysis for multiple pages of articles"""
    analyzer = SentimentIntensityAnalyzer()
    spark = SparkSession.builder.master("local[*]").appName("NewsSentiment").getOrCreate()
    
    def get_sentiment(text):
        if not text:
            return "Neutral"
        score = analyzer.polarity_scores(text)['compound']
        if score >= 0.05:
            return "Positive"
        elif score <= -0.05:
            return "Negative"
        else:
            return "Neutral"
    
    sentiment_udf = udf(get_sentiment, StringType())
    url = "https://newsdata.io/api/1/latest"
    
    all_articles = []
    seen_titles = set()
    next_page = None
    max_pages = 3  # Limit to 3 pages to avoid hitting API limits
    
    print(f"Starting pagination to fetch {max_pages} pages of articles...")
    
    for page in range(max_pages):
        print(f"\n--- Fetching Page {page + 1} ---")
        
        params = {
            "apikey": "pub_0623eb3fbe6a42f89077c65a8860fe24",  
            "language": "en"
        }
        
        # Add pagination token for pages 2, 3, etc.
        if next_page:
            params["page"] = next_page
            print(f"Using nextPage token: {next_page[:20]}...")
        else:
            print("First page - no pagination token needed")
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data.get("status") != "success":
            print(f"API error on page {page + 1}: {data}")
            break
            
        articles_raw = data.get("results", [])
        next_page = data.get("nextPage")
        
        print(f"API returned {len(articles_raw)} articles")
        print(f"NextPage token available: {'Yes' if next_page else 'No'}")
        
        articles_added_this_page = 0
        for article in articles_raw:
            title = article.get("title", "")
            if title and title not in seen_titles:
                seen_titles.add(title)
                all_articles.append({
                    "title": title,
                    "description": article.get("description", "")
                })
                articles_added_this_page += 1
        
        print(f"Added {articles_added_this_page} unique articles from page {page + 1}")
        print(f"Total unique articles so far: {len(all_articles)}")
        
        # Stop if no more pages available
        if not next_page:
            print("No more pages available - stopping pagination")
            break
    
    if not all_articles:
        spark.stop()
        return []

    df = spark.createDataFrame(all_articles)
    df = df.withColumn("text", concat(col("title"), lit(" "), col("description")))
    df = df.withColumn("sentiment", sentiment_udf(col("text")))

    results = df.select("title", "sentiment").toPandas().to_dict(orient="records")
    spark.stop()
    return results
