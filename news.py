#!/usr/bin/env python3
"""
Executive Intelligence Briefing - Terminal Only, No File Save
"""

import requests
from newspaper import Article
import google.generativeai as genai
from datetime import datetime
import json
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

NEWSAPI_KEY = "you will get this free one on news data.io"
GEMINI_KEY = ""

TECH_KEYWORDS = [
    'ai', 'artificial intelligence', 'machine learning', 'deep learning',
    'cyber', 'security', 'hack', 'breach', 'data leak', 'ransomware',
    'startup', 'venture capital', 'funding', 'series a', 'series b',
    'saas', 'cloud', 'aws', 'azure', 'google cloud',
    'software', 'app', 'mobile', 'ios', 'android',
    'fintech', 'blockchain', 'crypto', 'web3',
    'semiconductor', 'chip', 'processor', 'gpu', 'nvidia', 'amd', 'intel',
    'telecom', '5g', 'broadband', 'fiber',
    'digital', 'ecommerce', 'e-commerce', 'online',
    'data center', 'server', 'infrastructure',
    'automation', 'robotics', 'autonomous'
]

BLOCKED_KEYWORDS = [
    'bollywood', 'actor', 'actress', 'celebrity', 'film', 'movie', 'khan',
    'cricket', 'sports', 'football', 'match', 'tournament',
    'election', 'politics', 'minister', 'prime minister', 'modi',
    'wedding', 'marriage', 'divorce', 'baby', 'child', 'birthday'
]

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

def is_tech_article(title, description=""):
    """Strictly filter out non-tech articles"""
    text = (str(title) + " " + str(description)).lower()
    
    for blocked in BLOCKED_KEYWORDS:
        if blocked in text:
            return False
    
    for tech in TECH_KEYWORDS:
        if tech in text:
            return True
    
    return False

def fetch_news(limit=10):
    """Fetch from newsdata.io"""
    url = "https://newsdata.io/api/1/latest"
    params = {
        "apikey": NEWSAPI_KEY,
        "category": "technology",
        "language": "en",
        "size": limit
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code != 200:
            return []
        
        data = response.json()
        
        if data.get('status') == 'error':
            return []
        
        results = data.get('results', [])
        if not results:
            return []
        
        # Filter for tech
        tech_articles = []
        for article in results:
            title = article.get('title', '')
            desc = article.get('description', '')
            if is_tech_article(title, desc):
                tech_articles.append(article)
        
        return tech_articles[:3]  # LIMIT TO 3 ARTICLES
        
    except Exception as e:
        print(f"  Fetch failed: {str(e)[:100]}")
        return []

def process_article(article_data):
    """Process article with Gemini"""
    
    prompt = f"""
You are a tech executive analyst. Return ONLY valid JSON, no other text.

**Article:** {article_data['title']}
**Source:** {article_data['source']}
**Text:** {article_data['text'][:3500]}

**Return EXACTLY this JSON:**

{{
  "headline": "tech executive headline max 12 words",
  "card_summary": "40-60 word tech-focused summary",
  "executive_summary": "50-80 words - tech/business impact",
  "key_development": "What happened (2-3 sentences)",
  "strategic_implication": "Why this matters (2-3 sentences)",
  "hidden_signal": "What most miss (1-2 sentences)",
  "topic": "Artificial Intelligence|Cybersecurity|Startups|Enterprise Tech|Cloud|Fintech",
  "impact_type": "Market Shift|Funding|Acquisition|Data Breach|Product Launch",
  "geography": "India|US|UK|Europe|Global|UAE",
  "signal_strength": "Weak|Growing|Strong|Major Shift"
}}
"""

    try:
        response = model.generate_content(prompt)
        json_str = response.text.strip()
        
        if '```json' in json_str:
            json_str = json_str.split('```json')[1].split('```')[0]
        elif '```' in json_str:
            json_str = json_str.split('```')[1].split('```')[0]
        
        result = json.loads(json_str.strip())
        result['source'] = article_data['source']
        result['source_url'] = article_data['url']
        result['image_url'] = article_data.get('image_url')
        return result
        
    except Exception as e:
        print(f"   Failed: {str(e)[:100]}")
        return None

def extract_article(article_meta):
    """Extract article content"""
    url = article_meta.get('link')
    if not url:
        return None
    
    try:
        article = Article(url)
        article.config.request_timeout = 10
        article.download()
        article.parse()
        
        title = article.title or article_meta.get('title', '')
        if not is_tech_article(title, article.text[:500]):
            return None
        
        return {
            'title': title,
            'text': article.text[:3500],
            'url': url,
            'source': article_meta.get('source_name', 'Unknown'),
            'image_url': article.top_image or article_meta.get('image_url')
        }
    except Exception as e:
        return None

def display_briefing(articles):
    """Display briefing in terminal - NO FILE SAVE"""
    
    print("\n" + "="*70)
    print(f" TECH EXECUTIVE BRIEFING")
    print(f"{datetime.now().strftime('%B %d, %Y at %H:%M')}")
    print("="*70)
    
    for i, article in enumerate(articles, 1):
        print(f"\n{'─'*70}")
        print(f" {i}. {article.get('headline', 'No title')}")
        print(f"{'─'*70}")
        print(f"\n Summary:")
        print(f"   {article.get('card_summary', 'N/A')}")
        
        print(f"\n Key Development:")
        print(f"   {article.get('key_development', 'N/A')}")
        
        print(f"\n Strategic Implication:")
        print(f"   {article.get('strategic_implication', 'N/A')}")
        
        print(f"\n Hidden Signal:")
        print(f"   {article.get('hidden_signal', 'N/A')}")
        
        print(f"\n  Topic: {article.get('topic', 'N/A')}")
        print(f" Impact: {article.get('signal_strength', 'N/A')}")
        print(f" Geography: {article.get('geography', 'N/A')}")
        print(f" Source: {article.get('source', 'Unknown')}")
        
        if article.get('image_url'):
            print(f"  Image: {article.get('image_url')}")
    
    print("\n" + "="*70)
    print(f"Briefing complete! {len(articles)} tech articles")
    print("="*70 + "\n")

def generate_briefing():
    """Main function - NO FILE SAVE, JUST TERMINAL OUTPUT"""
    
    start_time = time.time()
    
    print("\n" + "="*70)
    print(f" FETCHING TECH NEWS...")
    print("="*70 + "\n")
    
    # Fetch news (already limited to 3)
    news_items = fetch_news(limit=10)
    
    if not news_items:
        print(" No tech news found")
        return None
    
    print(f"📥 Extracting {len(news_items)} articles...")
    extracted = []
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(extract_article, item): item for item in news_items}
        for future in as_completed(futures):
            result = future.result()
            if result:
                extracted.append(result)
                print(f"    Extracted: {result['title'][:60]}...")
    
    if not extracted:
        print(" No articles could be extracted")
        return None
    
    print(f"\n Analyzing with AI...")
    processed = []
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(process_article, article): article for article in extracted}
        for future in as_completed(futures):
            result = future.result()
            if result:
                processed.append(result)
            time.sleep(1)
    
    if processed:
        # Just display, no file save
        display_briefing(processed)
        print(f"⏱  Time taken: {time.time() - start_time:.1f} seconds")
        return processed
    
    return None

if __name__ == "__main__":
    generate_briefing()