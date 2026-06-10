import google.generativeai as genai
import json
import re
import requests

GEMINI_KEY = ""
PEXELS_API_KEY = ""  # Free signup: pexels.com/api

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-3.5-flash')

def get_pexels_image(search_query):
    """Get a real image URL from Pexels API based on search query"""
    if not PEXELS_API_KEY or PEXELS_API_KEY == "YOUR_PEXELS_API_KEY_HERE":
        # Fallback to Lorem Picsum if no API key (always works)
        return f"https://picsum.photos/1600/900?random={hash(search_query) % 1000}"
    
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": search_query, "per_page": 1, "orientation": "landscape"}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('photos') and len(data['photos']) > 0:
            # Return large sized image (16:9 aspect ratio)
            return data['photos'][0]['src']['large2x']
        else:
            # Fallback to Lorem Picsum
            return f"https://picsum.photos/1600/900?random={hash(search_query) % 1000}"
    except Exception as e:
        print(f"Image fetch error: {e}")
        # Fallback to Lorem Picsum (always works, no API key needed)
        return f"https://picsum.photos/1600/900?random={hash(search_query) % 1000}"

def generate_thinking_blog(topic_idea):
    prompt = f"""
You are an executive ghostwriter for "The Executive Narrative" - Thinking category.

STEP 1: Based on this broad topic idea: "{topic_idea}"

Find a REAL industry example from ANY of these sectors:
- Technology (Google, Apple, Microsoft, Amazon, Meta, Netflix)
- Automotive (Tesla, Toyota, Ford, Rivian)
- Finance (Goldman Sachs, JP Morgan, Stripe, PayPal)
- Healthcare (UnitedHealth, Pfizer, Moderna)
- Retail (Walmart, Target, Costco, Amazon)
- SaaS (Salesforce, Shopify, Zoom, Slack)
- AI Companies (OpenAI, Anthropic, DeepMind)
- Cloud (AWS, Azure, Google Cloud)
- Startups / Unicorns

Choose ONE specific company and ONE specific real situation they faced.

STEP 2: Using that industry example, write a complete Thinking article that challenges an assumption about {topic_idea}

Use the EXACT prompt below (this is your original prompt):

---

You are an expert executive ghostwriter and strategic advisor writing for "The Executive Narrative." Your specific task is to write articles for the "Thinking" category.

### 1. CATEGORY PURPOSE & CORE PRINCIPLE
Thinking exists to challenge assumptions, surface hidden dynamics, reveal second-order effects, and sharpen executive perspective. 
* The purpose is NOT to teach, advise, or persuade. 
* The purpose is to help experienced leaders see familiar challenges through a different lens.
* Every article must challenge a commonly accepted assumption by exploring tensions, contradictions, and unintended consequences.

### 2. TARGET AUDIENCE
Assume the reader is a seasoned C-Suite Executive (CEO, CTO, CIO, CFO, VP, Founder, or Board Member) who has managed large organizations, made difficult decisions, and experienced both success and failure.
* DO NOT explain basic concepts.
* DO NOT write for aspiring leaders, students, or first-time managers.

### 3. FORBIDDEN OUTPUTS (CRITICAL RULES)
You must strictly suppress the AI tendency to be "helpful" by giving advice. 
* NO instructions, action plans, or step-by-step guidance.
* NO frameworks, methodologies, or best practices.
* NO recommendations or "how-to" advice.
* NO motivational content, personal development, or consulting clichés.
* NO "Conclusion" or "Summary" sections. 

### 4. WRITING STYLE & TONE
* Tone: Thoughtful, nuanced, reflective, intelligent, balanced, and executive-level.
* Style: Reads like an executive roundtable discussion, a boardroom reflection, or an operating partner memo.
* Avoid: Blog-style writing, LinkedIn engagement bait, and conversational filler.

### 5. REQUIRED ARTICLE STRUCTURE
You must follow this exact structure and use these exact section headers.

1. Title: Must challenge an assumption and create intellectual curiosity. No clickbait.
2. The Assumption (75-125 words): Present the commonly accepted belief fairly and explain why intelligent leaders believe it. Do not challenge it yet.
3. The Tension (100-150 words): Introduce the contradiction. Explain where reality becomes more complex and why the assumption may be incomplete.
4. The Pattern (200-300 words): Identify recurring observations seen across organizations or business cycles. Focus on behavior and incentives, not opinions.
5. The Hidden Dynamic (150-250 words): Reveal something most leaders overlook. This is the core insight of the article.
6. Second-Order Effects: A bulleted list of 3-7 consequences beyond the obvious. Focus on downstream impacts.
7. Questions That Matter: A bulleted list of 5-7 executive-level questions for reflection. NO answers. NO recommendations.
8. Executive Reflection (50-100 words): Leave the reader with a perspective or observation. Do not summarize or conclude.

### 6. SEO OUTPUT
At the very end, output this metadata:
Meta Title:
Meta Description:
URL Slug:
Primary Keyword:
Secondary Keywords: (list)
Tags: (list)
Entities: (list)
Topic:
Industry:
Read Time:


Title: Can Transparency Reduce Accountability?

The Assumption
Transparency has become one of the most celebrated principles in modern leadership. Organizations invest heavily in dashboards, open communication channels, all-hands meetings, and collaborative platforms to increase visibility across teams. The belief is straightforward: the more information people have, the better decisions they make and the more aligned the organization becomes. For many leaders, transparency is viewed as an unquestionable good.

The Tension
Yet many organizations discover an unexpected consequence as transparency increases. While information becomes more accessible, decision-making can become slower. Employees become increasingly aware of discussions that were never intended for them. Teams begin monitoring decisions rather than owning outcomes. Leaders spend more time explaining decisions than making them. The challenge is not transparency itself. The challenge is understanding when transparency begins serving awareness and when it begins creating dependency.

The Pattern
Across industries, growing organizations often follow a similar path. In the early stages, information is limited because speed matters more than visibility. As companies scale, leaders introduce more transparency to maintain alignment and trust. Initially, the results are positive. Teams feel informed. Silos are reduced. Collaboration improves. Over time, however, a different pattern can emerge. As more people gain access to more information, the distinction between awareness and involvement begins to blur. Employees start expecting visibility into decisions they do not own.

The Hidden Dynamic
Transparency reduces uncertainty. But it can also redistribute responsibility. When people have visibility into every discussion, they often feel connected to every decision. As a result, leaders may feel pressure to seek broader agreement before moving forward. The organization slowly shifts from accountability-driven behavior toward participation-driven behavior. The hidden dynamic is that transparency can reduce decision risk for leaders while simultaneously increasing decision latency for the organization. This is not a transparency problem. It is an ownership problem.

Second-Order Effects
- Decision cycles become longer
- Approval layers quietly increase
- Stakeholder groups expand unnecessarily
- Meetings become substitutes for ownership
- Leaders spend more time communicating than directing
- Consensus begins replacing judgment

Questions That Matter
- Are employees seeking clarity or permission?
- Where has visibility become involvement?
- Which decisions require alignment and which require ownership?
- Are we measuring transparency or effectiveness?
- Where is decision velocity slowing?

Executive Reflection
Transparency remains one of the most powerful tools available to leaders. But transparency is not the same as accountability. Organizations often become slower not because information is hidden, but because ownership becomes diluted. The challenge is not deciding how much information to share. The challenge is preserving accountability as visibility expands.

[End of Example]

### YOUR TASK
Generate a new "Thinking" article based on the following topic or prompt provided by the user. Strictly adhere to the structure, tone, and forbidden outputs defined above.
---

STEP 3: Return ONLY valid JSON with this EXACT structure:

{{
  "industry_example_used": {{
    "company": "company name",
    "situation": "what real situation this article is based on",
    "year": "approx year if known"
  }},
  "title": "",
  "assumption": "",
  "tension": "",
  "pattern": "",
  "hidden_dynamic": "",
  "second_order_effects": [],
  "questions": [],
  "executive_reflection": "",
  "seo": {{
    "meta_title": "",
    "meta_description": "",
    "url_slug": "",
    "primary_keyword": "",
    "secondary_keywords": [],
    "tags": [],
    "entities": [],
    "topic": "",
    "industry": "",
    "read_time": ""
  }}
}}

IMPORTANT: The article MUST reference or be inspired by the real industry example you chose. Mention the company and situation naturally within the article.
"""

    response = model.generate_content(prompt)
    text = response.text.strip()
    text = re.sub(r'```json\n?', '', text)
    text = re.sub(r'```\n?', '', text)
    result = json.loads(text)
    
    # Generate search query for image based on topic and company
    company = result.get('industry_example_used', {}).get('company', '')
    title = result.get('title', '')
    search_query = f"{company} {topic_idea} business leadership"
    
    # Get real image URL
    image_url = get_pexels_image(search_query)
    
    # Add image to JSON output
    result['featured_image'] = image_url
    result['seo']['og_image'] = image_url
    result['image_alt_text'] = f"{company} {topic_idea} - {title}"
    
    return result

# ==================== USE IT ====================

result = generate_thinking_blog("leadership decision making under pressure")
print(json.dumps(result, indent=2))

# Save to file
with open("thinking_blog_with_example.json", "w") as f:
    json.dump(result, f, indent=2)