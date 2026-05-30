

import requests
from newspaper import Article
import google.generativeai as genai
from datetime import datetime
import json
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

NEWSAPI_KEY = "pub_95ac61eacf654ae797cd0fd2a5cb4b2f"
GEMINI_KEY = "Gemini API Key Here"

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

REQUESTS_PER_MINUTE = 5
DELAY_BETWEEN_ARTICLES = 35 

# ==================== FASTAPI APP ====================
app = FastAPI(title="Executive Intelligence Briefing API")

class ArticleResponse(BaseModel):
    headline: str
    topic: str
    impact_type: str
    geography: str
    signal_strength: str
    card_summary: str
    executive_summary: str
    key_development: str
    strategic_implication: str
    hidden_signal: str
    source: str
    source_url: str

class BriefingResponse(BaseModel):
    success: bool
    date: str
    articles: List[ArticleResponse]
    error: Optional[str] = None

# RETRY DECORATOR 
@retry(
    retry=retry_if_exception_type(Exception),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=30, max=120),
    reraise=True
)
def call_gemini_with_retry(prompt):
    """Call Gemini with automatic retry on rate limits - SAME AS YOUR WORKING CODE"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        if "429" in str(e) or "quota" in str(e).lower():
            print(f"   ⚠️ Rate limited. Waiting 30 seconds before retry...")
            time.sleep(30)
            raise
        raise

#  PROCESS ARTICLE 
def process_article(news_item):
    """Process entire article in ONE Gemini call - SAME AS YOUR WORKING CODE"""
    
    prompt = f"""
You are an executive intelligence analyst. Return ONLY valid JSON.

**Article:** {news_item['title']}
**Source:** {news_item['source']}
**Text:** {news_item['text'][:4000]}

**Return this EXACT JSON structure:**

{{
  "headlines": ["10 executive headlines, max 12 words each, no clickbait"],
  
  "card_summary": "40-60 word executive summary following: What happened + Why it matters + Hidden signal. No hype words.",
  
  "full_briefing": {{
    "executive_summary": "50-80 words",
    "key_development": "What actually happened (2-3 sentences)",
    "strategic_implication": "Why this matters to businesses, markets, leadership (2-3 sentences)",
    "hidden_signal": "What most people are missing (1-2 sentences)",
    "bottom_line": "One sharp concluding sentence, max 18 words"
  }},
  
  "bottom_lines": ["5 executive insights, max 18 words each"],
  
  "categories": {{
    "topic": "Choose from: Artificial Intelligence, Cybersecurity, Startups, Enterprise Technology, Finance, Healthcare, Cloud Computing, Data Privacy, Venture Capital, Layoffs",
    "impact_type": "Choose from: Market Shift, Funding Round, Acquisition, Data Breach, Product Launch, Leadership Move, Partnership, Layoffs",
    "geography": "Choose from: India, United States, United Kingdom, UAE, Singapore, Europe, Global",
    "relevance": "Choose from: Immediate, Emerging, Long-term, Strategic",
    "signal_strength": "Choose from: Weak Signal, Growing Trend, Strong Signal, Major Shift"
  }}
}}

**Rules:**
- No hype words: revolutionary, groundbreaking, massive, unprecedented, game-changing
- Use executive vocabulary: strategic, structural, market signal, capital allocation
- Sound like a senior analyst, not an AI
"""

    try:
        response = call_gemini_with_retry(prompt)
        json_str = response.strip('```json\n').strip('\n```')
        return json.loads(json_str)
    except Exception as e:
        print(f"   ❌ Processing failed: {e}")
        return None

def fetch_news():
    """Fetch news from API"""
    url = "https://newsdata.io/api/1/latest"
    params = {
        "apikey": NEWSAPI_KEY,
        "category": "technology",
        "language": "en",
        "size": 5
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        articles = data.get('results', [])[:4]
        return articles
    except Exception as e:
        print(f" Fetch failed: {e}")
        return []

def extract_article(article_meta):
    """Extract full article content"""
    url = article_meta.get('link')
    if not url:
        return None
    
    try:
        article = Article(url)
        article.config.request_timeout = 15
        article.download()
        article.parse()
        
        return {
            'title': article.title or article_meta.get('title'),
            'text': article.text[:5000],
            'url': url,
            'source': article_meta.get('source_name', 'Unknown'),
            'image': article.top_image or article_meta.get('image_url')
        }
    except Exception as e:
        print(f"    Extraction failed: {str(e)[:50]}")
        return None

# ==================== API ENDPOINT ====================
@app.get("/briefing", response_model=BriefingResponse)
async def get_briefing():
    """Main endpoint - returns executive briefing in JSON"""
    
    try:
        articles_meta = fetch_news()
        
        if not articles_meta:
            return BriefingResponse(
                success=False,
                date=datetime.now().strftime("%Y-%m-%d"),
                articles=[],
                error="No articles found from news API"
            )
        
        extracted = []
        for i, meta in enumerate(articles_meta, 1):
            content = extract_article(meta)
            if content and len(content.get('text', '')) > 300:
                extracted.append(content)
            time.sleep(2)
        
        if not extracted:
            return BriefingResponse(
                success=False,
                date=datetime.now().strftime("%Y-%m-%d"),
                articles=[],
                error="No articles could be extracted"
            )
        
        processed = []
        for i, article in enumerate(extracted, 1):
            result = process_article(article)
            
            if result:
                categories = result.get('categories', {})
                full_briefing = result.get('full_briefing', {})
                
                processed.append({
                    "headline": result.get('headlines', ['Untitled'])[0],
                    "topic": categories.get('topic', 'General'),
                    "impact_type": categories.get('impact_type', 'Market Shift'),
                    "geography": categories.get('geography', 'Global'),
                    "signal_strength": categories.get('signal_strength', 'Growing Trend'),
                    "card_summary": result.get('card_summary', ''),
                    "executive_summary": full_briefing.get('executive_summary', ''),
                    "key_development": full_briefing.get('key_development', ''),
                    "strategic_implication": full_briefing.get('strategic_implication', ''),
                    "hidden_signal": full_briefing.get('hidden_signal', ''),
                    "source": article.get('source', 'Unknown'),
                    "source_url": article.get('url', '#')
                })
            
            if i < len(extracted):
                time.sleep(DELAY_BETWEEN_ARTICLES)
        
        return BriefingResponse(
            success=True,
            date=datetime.now().strftime("%Y-%m-%d"),
            articles=processed,
            error=None
        )
        
    except Exception as e:
        return BriefingResponse(
            success=False,
            date=datetime.now().strftime("%Y-%m-%d"),
            articles=[],
            error=str(e)
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)