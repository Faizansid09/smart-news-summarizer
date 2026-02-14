import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv('NEWS_API_KEY')
NEWS_API_URL = 'https://newsapi.org/v2/top-headlines'

def fetch_top_news(category='technology', country='in', page_size=5):
    params = {
        'apiKey': NEWS_API_KEY,
        'category': category,
        'country': country,
        'pageSize': page_size
    }
    
    try:
        response = requests.get(NEWS_API_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        print(f"DEBUG: API Response Status: {data['status']}")
        print(f"DEBUG: Total Results: {data.get('totalResults', 0)}")
        
        if data['status'] == 'ok':
            articles = data['articles']
            print(f"\n✅ Successfully fetched {len(articles)} articles!\n")
            
            for idx, article in enumerate(articles, 1):
                print(f"{idx}. {article['title']}")
                print(f"   Source: {article['source']['name']}")
                print(f"   Published: {article['publishedAt']}")
                print(f"   URL: {article['url']}")
                
                description = article.get('description', 'No description')
                if description:
                    print(f"   Description: {description[:100]}...")
                print("-" * 80)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'news_{timestamp}.json'
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(articles, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Saved articles to {filename}")
            return articles
            
        else:
            print(f"❌ Error: {data.get('message', 'Unknown error')}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

if __name__ == "__main__":
    print("🗞️  Smart News Summarizer - News Fetcher")
    print("=" * 80)
    
    articles = fetch_top_news(
        category='general',
        country='us',
        page_size=10
    )