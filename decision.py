import google.generativeai as genai
from datetime import datetime
import time
import re
import json
import requests

GEMINI_KEY = ""
PEXELS_API_KEY = ""  


genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

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

def generate_topic():
    topic_prompt = """You are writing for The Executive Narrative.

The Decisions category is designed for seasoned executives, senior decision-makers, board members, investors, and business leaders.

The objective is NOT to provide answers. The objective is to help leaders evaluate difficult business decisions by presenting context, competing perspectives, trade-offs, uncertainty, and executive judgment.

---

## TARGET AUDIENCE
Assume the reader is: CEO, Founder, President, Board Member, Managing Director, Investor, CIO, CTO, CISO, CFO, COO, VP.
Assume the reader has managed large teams, owned P&L responsibility, allocated budgets, made difficult decisions.
NEVER write for students, aspiring leaders, or entry-level professionals. Do NOT explain basic concepts.

---

## CORE PRINCIPLE
Every article must revolve around a real executive decision that is difficult, involves uncertainty, involves trade-offs, and has no universally correct answer.

Good examples:
- "Should companies invest aggressively in AI right now?"
- "Should security leaders prioritize resilience over prevention?"
- "Is market expansion worth the operational complexity?"

---

## NOW GENERATE A TOPIC
Generate a SINGLE Decisions topic on a NEW executive-level issue relevant to CEOs, CTOs, CISOs, or Board Members.
The topic MUST be framed as a question.
Output ONLY the question text. No quotation marks, no intro text."""

    response = model.generate_content(topic_prompt)
    topic = response.text.strip().strip('"')
    
    if not topic.endswith('?'):
        topic = topic + '?'
    
    return topic

def generate_article_from_topic(topic):
    article_prompt = f"""
You are an elite Corporate Strategy Facilitator writing for "The Executive Narrative."
Generate a Decisions article based on this exact topic: {topic}

**Target Audience:** CEOs, CTOs, CISOs, Board Members, PE Partners. Assume deep executive experience.
**Core Principle:** The decision must be difficult, involve uncertainty, and trade-offs.

**MANDATORY FRAMING (CRITICAL):**
Do not frame problems as "IT, HR, or Marketing" issues. Frame every problem as a Capital Allocation, Enterprise Risk, or Operational P&L issue.
- Instead of "patching vulnerabilities," use "mitigating structural enterprise risk."
- Instead of "buying software," use "deploying capital."
Speak the language of Wall Street, Boardrooms, and Private Equity.

**What to AVOID:** No conclusions, prescriptions, recommendations, frameworks, or step-by-step guidance. NO buzzwords.

**OUTPUT SCHEMA:**
You MUST output a strictly valid JSON object matching the exact structure below. Do not include any text outside the JSON.

{{
  "headline": "The exact topic question.",
  "executive_summary": "50-80 words. Explain the decision, why it matters, and why it is difficult. NO answer.",
  "the_situation": "100-200 words. Macro business context, capital/market realities.",
  "why_smart_leaders_disagree": "100-150 words. The core intellectual and strategic division.",
  "perspective_a": "150-250 words. Strongest case for ONE side. Defend it like a respected CEO. Use financial/risk framing.",
  "perspective_b": "150-250 words. Strongest case for the OPPOSING side. Equally persuasive.",
  "what_makes_this_decision_difficult": "150-250 words. Discuss uncertainty, timing, organizational constraints, competing incentives.",
  "context_changes_the_answer": {{
    "option_a_name": "Short name for Perspective A",
    "option_a_conditions": [
      "Condition 1",
      "Condition 2",
      "Condition 3"
    ],
    "option_b_name": "Short name for Perspective B",
    "option_b_conditions": [
      "Condition 1",
      "Condition 2",
      "Condition 3"
    ]
  }},
  "signals_leaders_should_watch": [
    "Observable indicator 1",
    "Observable indicator 2",
    "Observable indicator 3",
    "Observable indicator 4",
    "Observable indicator 5"
  ],
  "the_executive_lens": "30-60 words. Final perspective framing. DO NOT conclude."
}}
"""
    
    response = model.generate_content(
        article_prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.4
        )
    )
    
    try:
        article_json = json.loads(response.text)
        return article_json
    except json.JSONDecodeError:
        return None

def generate_decision_article():
    topic = generate_topic()
    article_dict = generate_article_from_topic(topic)
    
    if article_dict:
        search_query = topic.replace('?', '').replace(' ', '+')[:50]
        image_url = get_pexels_image(search_query)
        article_dict['featured_image'] = image_url
        article_dict['image_alt_text'] = topic[:100]
    
    return topic, article_dict

def save_article_json(topic, article_dict, filename=None):
    if not article_dict:
        return None
        
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = re.sub(r'[^a-zA-Z0-9]', '_', topic[:40]).strip('_')
        filename = f"executive_narrative_{safe_topic}_{timestamp}.json"
    
    final_output = {
        "_metadata": {
            "generated_at": datetime.now().isoformat(),
            "topic_original": topic
        },
        **article_dict
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, indent=4, ensure_ascii=False)
    
    return filename

if __name__ == "__main__":
    topic, article_dict = generate_decision_article()
    
    if article_dict:
        filename = save_article_json(topic, article_dict)
        
        output = {
            "success": True,
            "filename": filename,
            "topic": topic,
            "article": article_dict
        }
        
        print(json.dumps(output, indent=2))
    else:
        print(json.dumps({"success": False, "error": "Failed to generate article"}, indent=2))