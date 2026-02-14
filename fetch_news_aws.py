import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError

load_dotenv()

NEWS_API_KEY = os.getenv('NEWS_API_KEY')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
s3_client = boto3.client('s3', region_name=AWS_REGION)

def fetch_worldwide_news(query='technology', page_size=10):
    """
    Fetch worldwide news using NewsAPI
    """
    url = 'https://newsapi.org/v2/everything'
    
    params = {
        'apiKey': NEWS_API_KEY,
        'q': query,
        'language': 'en',
        'sortBy': 'publishedAt',
        'pageSize': page_size
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data['status'] == 'ok':
            articles = data['articles']
            print(f"\n✅ Successfully fetched {len(articles)} articles!\n")
            return articles
        else:
            print(f"❌ Error: {data.get('message', 'Unknown error')}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

def save_to_dynamodb(articles, table_name='NewsArticles'):
    """
    Save articles to DynamoDB
    """
    try:
        table = dynamodb.Table(table_name)
        
        saved_count = 0
        for idx, article in enumerate(articles):
            # Create unique ID using timestamp + index (more reliable)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            article_id = f"{timestamp}_{idx}"
            
            item = {
                'article_id': article_id,
                'title': article.get('title', 'No title'),
                'source': article['source']['name'],
                'author': article.get('author', 'Unknown'),
                'description': article.get('description', ''),
                'url': article.get('url', ''),
                'published_at': article.get('publishedAt', ''),
                'fetched_at': datetime.now().isoformat(),
                'content': article.get('content', '')[:1000]
            }
            
            table.put_item(Item=item)
            saved_count += 1
            print(f"  ✓ Saved: {article.get('title', 'No title')[:50]}...")
        
        print(f"\n✅ Saved {saved_count} articles to DynamoDB table: {table_name}")
        return True
        
    except ClientError as e:
        print(f"❌ DynamoDB Error: {e.response['Error']['Message']}")
        return False
    except Exception as e:
        print(f"❌ Error saving to DynamoDB: {e}")
        return False
def save_to_s3(articles, bucket_name='news-summarizer-bucket-faizan-2024'):
    """
    Save articles JSON to S3
    """
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'news_{timestamp}.json'
        
        # Convert to JSON
        json_data = json.dumps(articles, indent=2, ensure_ascii=False)
        
        # Upload to S3
        s3_client.put_object(
            Bucket=bucket_name,
            Key=f'raw-news/{filename}',
            Body=json_data,
            ContentType='application/json'
        )
        
        print(f"✅ Saved to S3: s3://{bucket_name}/raw-news/{filename}")
        return True
        
    except ClientError as e:
        print(f"❌ S3 Error: {e.response['Error']['Message']}")
        return False
    except Exception as e:
        print(f"❌ Error saving to S3: {e}")
        return False

def main():
    print("🗞️  Smart News Summarizer - AWS Version")
    print("=" * 80)
    
    # Step 1: Fetch news
    print("\n📰 Step 1: Fetching news from NewsAPI...")
    articles = fetch_worldwide_news(
        query='artificial intelligence',
        page_size=5
    )
    
    if not articles:
        print("❌ No articles fetched. Exiting.")
        return
    
    # Display articles
    for idx, article in enumerate(articles, 1):
        print(f"{idx}. {article['title']}")
        print(f"   Source: {article['source']['name']}")
        print("-" * 80)
    
    # Step 2: Save to DynamoDB
    print("\n💾 Step 2: Saving to DynamoDB...")
    save_to_dynamodb(articles)
    
    # Step 3: Save to S3
    print("\n☁️  Step 3: Saving to S3...")
    save_to_s3(articles)
    
    print("\n✅ All done! Check your AWS Console to see the data.")

if __name__ == "__main__":
    main()