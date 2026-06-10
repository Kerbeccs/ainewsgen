import google.generativeai as genai
from datetime import datetime
import json
import time
import re
import requests

GEMINI_KEY = ""
PEXELS_API_KEY = ""  # Free signup: pexels.com/api

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-3.5-flash')

def get_pexels_image(search_query):
    if not PEXELS_API_KEY or PEXELS_API_KEY == "YOUR_PEXELS_API_KEY_HERE":
        return f"https://picsum.photos/1200/800?random={hash(search_query) % 1000}"
    
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": search_query, "per_page": 1, "orientation": "landscape"}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('photos') and len(data['photos']) > 0:
            return data['photos'][0]['src']['large2x']
    except Exception:
        pass
    
    return f"https://picsum.photos/1200/800?random={hash(search_query) % 1000}"

def call_gemini_with_retry(prompt, retry_count=0):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        if "429" in str(e) or "quota" in str(e).lower():
            if retry_count < 3:
                wait_time = 30
                time.sleep(wait_time)
                return call_gemini_with_retry(prompt, retry_count + 1)
            else:
                raise
        raise

def generate_topic_and_deep_dive():
    prompt = f"""
You are an elite corporate strategy analyst and senior advisor writing exclusively for an audience of CEOs, founders, and institutional investors.

FIRST, select a company and topic from these examples or choose a similar high-profile company:
- Netflix: why they won the streaming war
- Apple: the strategy behind their services business
- Microsoft: how they pivoted to cloud and AI
- Nvidia: how they built the AI infrastructure layer
- Amazon: how they built the AWS moat
- Tesla: vertical integration strategy
- Google: why search dominance is under threat
- Meta: the pivot to AI infrastructure
- Salesforce: enterprise SaaS consolidation strategy

Choose ONE company and ONE specific strategic angle. Make it relevant for 2026 context.

THEN, generate a complete Deep Dive analysis.

**Category:** Deep Dive Strategic Brief
**Current Year Context:** The current year is 2026. Ensure all market metrics, valuations, and data footprints are accurately projected or grounded up to 2026.

**Objective:** Deconstruct this case study into an executive-level strategic brief explaining the high-stakes decisions, underlying business mechanics, and structural levers that drove the outcome.

**Tone & Style Requirements:**
- **Zero Fluff:** Eliminate introductory pleasantries, narrative filler, and superficial adjectives.
- **Corporate Finance & Strategy Focus:** Frame events using hard business concepts: CAC, LTV, Switching Costs, Moats, Gross Margins, Network Effects, TAM.
- **High Information Density:** Every sentence must deliver concrete asset, platform, or capital allocation insights.
- **Elite Vocabulary Lock:** Speak the language of Wall Street, Private Equity, and the Boardroom. Replace generic business terms with enterprise-grade terminology (e.g., instead of "they made a new product," use "they deployed capital into adjacent TAMs"; instead of "they grew fast," use "hyper-accelerated revenue velocity and margin expansion").
**Return ONLY valid JSON with this EXACT structure:**

{{
  "selected_company": "company name",
  "selected_angle": "the strategic angle chosen",
  "headline": "max 12 words, clinical and strategic",
  "meta_title": "50-60 characters, professional and keyword-optimized",
  "meta_description": "140-160 characters, clear summary",
  "url_slug": "url-friendly-version-of-headline",
  "primary_keyword": "main strategic keyword",
  "secondary_keywords": ["keyword2", "keyword3", "keyword4"],
  "executive_snapshot": "50-80 words. Bottom Line Up Front. Summarize core thesis, capital/strategic pivot, net economic outcome.",
  "key_takeaways": [
    "Strategic leverage point 1",
    "Financial or operational moat insight 2",
    "Market diversification or scalability insight 3",
    "Fourth high-impact takeaway"
  ],
  "the_story": "400-800 words. Break down chronologically using clear milestone markers. Focus on cash flow redirection, asset commoditization, infrastructure scale.",
  "key_turning_point": "50-100 words. Isolate exact contrarian capital allocation or platform decision.",
  "lessons": [
    "Actionable structural lesson 1",
    "Operational/Strategic framework lesson 2",
    "Platform-play lesson 3"
  ],
  "tags": ["CorporateStrategy", "BusinessModel", "PlatformEcosystem"],
  "entities": ["CoreCompany", "KeyExecutives", "PrimaryCompetitors"],
  "topic": "One word executive vertical",
  "industry": "Specific industry sector",
  "region": "Market geography impact",
  "sources": ["Official Investor Relations Data", "Tier-1 Financial Intelligence"]
}}

**CRITICAL RULES:**
1. Executive Snapshot must act as independent executive brief.
2. Lessons must be operational business frameworks, never generic leadership quotes.
3. 2026 Accuracy: Ensure financial scale and market metrics reflect 2025/2026.
4. ** Quality Control Filter:** If the analysis reads like a Wikipedia summary or a basic tech blog, it fails. It MUST read like a highly confidential, premium Private Equity operating review.
Return ONLY valid JSON. No markdown wrappers.
"""

    response = call_gemini_with_retry(prompt)
    json_str = response.strip('```json\n').strip('\n```').strip()
    result = json.loads(json_str)
    
    search_query = f"{result.get('selected_company', '')} {result.get('selected_angle', '')} business strategy"
    image_url = get_pexels_image(search_query)
    result['featured_image'] = image_url
    
    return result

def save_deep_dive(result):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    company = result.get('selected_company', 'company').lower().replace(' ', '_')
    filename = f"deepdive_{company}_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    return filename

if __name__ == "__main__":
    result = generate_topic_and_deep_dive()
    filename = save_deep_dive(result)
    
    output = {
        "success": True,
        "filename": filename,
        "data": result
    }
    
    print(json.dumps(output, indent=2))