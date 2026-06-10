
import google.generativeai as genai
from datetime import datetime
import json
import time
import re
import requests

GEMINI_KEY = ""
PEXELS_API_KEY = "" 

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
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            if retry_count < 3:
                wait_time = 30
                time.sleep(wait_time)
                return call_gemini_with_retry(prompt, retry_count + 1)
            else:
                raise
        else:
            raise

def get_playbook_prompt(topic: str) -> str:
    return f"""
You are an elite Executive Content Architect specializing in production-ready strategic intelligence for C-suite leaders (CEOs, Founders, Managing Directors, CXOs). Your task is to generate an "Executive Playbook" based on the provided [TOPIC]: {topic}

The output MUST be highly pragmatic, deeply analytical, and strictly formatted as a valid JSON object. Do not provide any introductory or concluding text outside the JSON block.

### ROLE & TARGET AUDIENCE
Your reader is a seasoned senior executive managing multi-million dollar budgets, large business units, complex strategic initiatives, and leadership teams. 
- Assume executive-level business acumen.
- NEVER explain basic management concepts, leadership fundamentals, or workplace etiquette.
- Write with extreme precision, high density of thought, and zero fluff.

### CORE CONTENT FILTER & PHILOSOPHY
Every playbook must answer: "How should a senior leader operate and allocate capital/resources in this specific high-stakes situation?"

1. FORCE TRADEOFF TENSION: Every topic must navigate a "Good vs. Good" or "Bad vs. Bad" operational dilemma (e.g., Speed vs. Control, Autonomy vs. Alignment). If no tension exists, reject generic execution.
2. EXECUTIVE QUALITY FILTER: Before writing any sentence, validate:
   - Would a CEO care?
   - Does this directly impact macro business outcomes or execution velocity?
   - If the answer is NO, omit it.

### STYLE & DICTION RULES
- Paragraph Length: Maximum 3 sentences per paragraph. Crispy, scannable, punchy syntax.
- Reading Level: Sharp, professional, authoritative, and corporate-vetted.
- FORBIDDEN WORDS & PHRASES: revolutionary, game-changing, groundbreaking, transformative, next-generation, disruption, paradigm shift, "communication is key", "trust is the foundation", "great leaders listen". Eliminate all motivational LinkedIn-style hype.

### OUTPUT JSON SCHEMA SPECIFICATION
You must output a strictly valid JSON object containing exactly the following keys. Failure to follow this structure or inserting prose outside the JSON markdown block will break the production pipeline.

{{
  "headline": "8-12 words. High-level, zero clickbait, no listicles, no hype.",
  "summary": "50-80 words summarizing the core execution challenge and strategic objective. Purely objective; no opinions, no predictions.",
  "executive_question": "A single, sharp question framing the operational trade-off.",
  "executive_context": "100-150 words outlining the macro business situation and organizational complexity. No storytelling or anecdotes.",
  "why_this_is_hard": "100-150 words breaking down the core tensions, systemic constraints, and competing priorities. Focus heavily on why standard approaches fail.",
  "core_challenge": "75-125 words pinpointing exactly ONE primary operational bottleneck or strategic vulnerability.",
  "operating_principles": [
    "Principle 1: Must be deeply actionable, tactical, and contrarian/strategic.",
    "Principle 2",
    "Principle 3",
    "Principle 4",
    "Principle 5"
  ],
  "playbook_steps": [
    {{
      "step_number": 1,
      "title": "Action-oriented phase title",
      "explanation": "Granular operating guidance for execution.",
      "expected_outcome": "Measurable institutional or financial result."
    }}
  ],
  "decision_triggers": [
    "Trigger 1: Hard operational metrics or behavioral indicators showing when to deploy this playbook.",
    "Trigger 2",
    "Trigger 3"
  ],
  "failure_signals": [
    "Signal 1: Clear, early-warning operational friction points showing the current model is failing.",
    "Signal 2",
    "Signal 3"
  ],
  "execution_checklist": {{
    "before": ["3-5 clear pre-execution checklist actions"],
    "during": ["3-5 real-time operational monitoring actions"],
    "after": ["3-5 post-execution auditing/refinement actions"]
  }},
  "one_principle": "Maximum 20 words. A ruthless, memorable executive truth.",
  "seo_metadata": {{
    "meta_title": "SEO optimized headline, max 60 chars.",
    "meta_description": "High-CTR executive summary, max 155 chars.",
    "url_slug": "Kebab-case URL path.",
    "primary_keyword": "Format: [Topic] + [Challenge]",
    "secondary_keywords": ["4-6 high-intent professional search phrases"],
    "tags": ["3-6 high-level industry categorization tags"],
    "entities": ["Core business frameworks, concepts, or structural terms extracted"],
    "topic": "The macro focus area",
    "industry": "Cross-Industry or specific sector if applicable",
    "read_time": "Estimated reading time (e.g., '6 min')"
  }}
}}

Return ONLY valid JSON. No markdown wrappers, no explanations outside the JSON.
"""

def generate_playbook(topic: str, industry: str = ""):
    full_topic = f"{topic} in {industry}" if industry else topic
    
    prompt = get_playbook_prompt(full_topic)
    
    response = call_gemini_with_retry(prompt)
    
    json_str = response.strip()
    if json_str.startswith('```json'):
        json_str = json_str[7:]
    if json_str.startswith('```'):
        json_str = json_str[3:]
    if json_str.endswith('```'):
        json_str = json_str[:-3]
    json_str = json_str.strip()
    
    result = json.loads(json_str)
    
    image_url = get_pexels_image(f"{topic} {industry} business strategy")
    result['image_url'] = image_url
    result['seo_metadata']['og_image'] = image_url
    
    return result

def save_playbook(playbook: dict, topic: str):
    safe_topic = re.sub(r'[^a-zA-Z0-9]', '_', topic.lower())[:40]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"playbook_{safe_topic}_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(playbook, f, indent=2, ensure_ascii=False)
    
    return filename

if __name__ == "__main__":
    topic = "managing organizational scaling during hyper-growth"
    industry = "Technology"
    
    result = generate_playbook(topic, industry)
    
    filename = save_playbook(result, topic)
    
    print(json.dumps(result, indent=2))