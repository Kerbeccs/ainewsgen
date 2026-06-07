import google.generativeai as genai
from datetime import datetime
import json
import time
from typing import List, Optional
from pydantic import BaseModel

# ==================== CONFIGURATION ====================

GEMINI_KEY = ""
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')  # Using 2.5 Flash


DELAY_BETWEEN_REQUESTS = 12  # 5 requests per minute = 12 seconds


# ==================== DEEP DIVE PROMPT ====================
def generate_deep_dive(company_name: str, topic_description: str = ""):
    """
    Generate a complete Deep Dive analysis for any company/topic
    
    Args:
        company_name: Name of company (e.g., "Nvidia", "Netflix")
        topic_description: Optional context (e.g., "their AI infrastructure strategy")
    """
    
    if topic_description:
        full_topic = f"{company_name}: {topic_description}"
    else:
        full_topic = company_name
    
    prompt = f"""
You are an elite corporate strategy analyst and senior advisor writing exclusively for an audience of CEOs, founders, and institutional investors. 

**Category:** Deep Dive Strategic Brief
**Topic:** {full_topic}
**Current Year Context:** The current year is 2026. Ensure all market metrics, valuations, and data footprints are accurately projected or grounded up to 2026. Do not wrap historical analysis in pre-2024 metrics.

**Objective:** Deconstruct this case study into an executive-level strategic brief explaining the high-stakes decisions, underlying business mechanics, and structural levers that drove the outcome. 

**Tone & Style Requirements:**
- **Zero Fluff:** Eliminate introductory pleasantries, narrative filler, and superficial adjectives ("revolutionary", "amazing"). 
- **Corporate Finance & Strategy Focus:** Frame events using hard business concepts: Customer Acquisition Cost (CAC), Customer Lifetime Value (LTV), Switching Costs, Moats, Gross Margins, Network Effects, Counter-Cyclical Diversification, and Total Addressable Market (TAM).
- **High Information Density:** Every sentence must deliver concrete asset, platform, or capital allocation insights.

---

**Return ONLY valid JSON with this EXACT structure. Do not change any keys:**

{{
  "headline": "max 12 words, clinical and strategic, focused on business mechanics",
  
  "meta_title": "50-60 characters, professional and keyword-optimized for C-suite search intent",
  
  "meta_description": "140-160 characters, clear summary highlighting the core business transformation",
  
  "url_slug": "url-friendly-version-of-headline",
  
  "primary_keyword": "main strategic keyword this analysis targets",
  
  "secondary_keywords": ["keyword2", "keyword3", "keyword4"],
  
  "executive_snapshot": "50-80 words. The 'Bottom Line Up Front' (BLUF). Summarize the core thesis, the capital/strategic pivot, and the net economic outcome. No introductory fluff.",
  
  "key_takeaways": [
    "Strategic leverage point 1 (e.g., how they weaponized a proprietary software layer)",
    "Financial or operational moat insight 2 (e.g., switching costs or ecosystem lock-in)",
    "Market diversification or scalability insight 3",
    "Fourth high-impact takeaway if applicable"
  ],
  
  "the_story": "400-800 words total. Do not output a single wall of text. Break it down chronologically using clear, implicit milestone markers or phases (e.g., '1. The Core Asset:', '2. The Strategic Pivot:', '3. Building the Moat:', '4. The Modern Payoff [2026]'). Focus heavily on cash flow redirection, asset commoditization, and infrastructure scale. Keep paragraphs short (2-4 sentences).",
  
  "key_turning_point": "50-100 words. Isolate the exact contrarian capital allocation or platform decision that altered the company's trajectory. Explain the systemic 'why' behind its success.",
  
  "lessons": [
    "Actionable structural lesson 1 (e.g., 'Monetizing the Installed Base via Proprietary Layering')",
    "Operational/Strategic framework lesson 2 (e.g., 'Counter-Cyclical Hedging via Recurring Subscription Revenue')",
    "Platform-play lesson 3 (e.g., 'Artificially Inflating Switching Costs via Multi-Device Friction')"
  ],
  
  "tags": ["CorporateStrategy", "BusinessModel", "PlatformEcosystem", "EnterpriseCompute"],
  
  "entities": ["CoreCompany", "KeyExecutives", "PrimaryCompetitors/Frameworks"],
  
  "topic": "One word executive vertical (e.g., Infrastructure, Infrastructure, FinTech, SaaS, Subscriptions)",
  
  "industry": "Specific industry sector",
  
  "region": "Market geography impact",
  
  "sources": ["Official Investor Relations Data", "Tier-1 Financial Intelligence (e.g., Bloomberg, Gartner, Financial Times)"]
}}

---

**CRITICAL RULES FOR EXECUTIVE VALIDATION:**
1. **BLUF Rule:** The Executive Snapshot must act as an independent executive brief. A CEO reading only this section must grasp the entire strategic mechanics of the case study immediately.
2. **No Motivational Advice:** The 'lessons' must be operational business frameworks, *never* generic leadership quotes. They should describe corporate strategy maneuvers that a CEO could theoretically execute in their own firm.
3. **2026 Accuracy:** Ensure that financial scale, user base numbers, and market dominance metrics are updated to reflect recent years (up to 2025/2026), rather than ending historical data points abruptly at 2023.

Return ONLY valid JSON. No markdown wrappers around the JSON if possible, no trailing explanations.
"""

    try:
        response = call_gemini_with_retry(prompt)
        json_str = response.strip('```json\n').strip('\n```').strip()
        return json.loads(json_str)
    except Exception as e:
        print(f"❌ Deep dive generation failed: {e}")
        return None

# ==================== RETRY DECORATOR ====================

def call_gemini_with_retry(prompt, retry_count=0):

    """Call Gemini with retry logic for rate limits"""

    try:

        response = model.generate_content(prompt)

        return response.text

    except Exception as e:

        if "429" in str(e) or "quota" in str(e).lower():

            if retry_count < 3:

                wait_time = 30

                print(f"   ⚠️ Rate limited. Waiting {wait_time} seconds before retry {retry_count + 1}/3...")

                time.sleep(wait_time)

                return call_gemini_with_retry(prompt, retry_count + 1)

            else:

                raise

        raise



# ==================== SAVE OUTPUT ====================

def save_deep_dive(result, company_name):

    """Save deep dive to JSON file"""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"deepdive_{company_name.lower().replace(' ', '_')}_{timestamp}.json"

   

    with open(filename, 'w', encoding='utf-8') as f:

        json.dump(result, f, indent=2, ensure_ascii=False)

   

    print(f"✅ Saved to: {filename}")

    return filename



# ==================== MAIN FUNCTION ====================

def create_deep_dive(company_name: str, topic_description: str = ""):

    """

    Main function to create a Deep Dive analysis

   

    Example usage:

        create_deep_dive("Nvidia", "how they built the AI infrastructure layer")

        create_deep_dive("Netflix", "why they won the streaming war")

        create_deep_dive("Apple", "the strategy behind their services business")

    """

   

    print("=" * 70)

    print(f"🎯 DEEP DIVE: {company_name}")

    print("=" * 70)

   

    print(f"\n📝 Generating analysis for: {company_name}")

    if topic_description:

        print(f"   Context: {topic_description}")

   

    # Generate deep dive

    result = generate_deep_dive(company_name, topic_description)

   

    if not result:

        print("❌ Failed to generate deep dive")

        return None

   

    # Save to file

    filename = save_deep_dive(result, company_name)

   

    # Print preview

    print("\n" + "=" * 70)

    print("📱 PREVIEW")

    print("=" * 70)

    print(f"\n Headline: {result.get('headline')}")

    print(f"\n Executive Snapshot:\n{result.get('executive_snapshot', '')[:200]}...")

    print(f"\n Key Takeaways:\n" + "\n".join(f"   • {t}" for t in result.get('key_takeaways', [])[:3]))

    print(f"\n Turning Point: {result.get('key_turning_point', '')[:150]}...")

    print(f"\n Lessons:\n" + "\n".join(f"   • {l}" for l in result.get('lessons', [])[:3]))

   

    return result



# ==================== BATCH DEEP DIVES ====================

def create_multiple_deep_dives(topics: list):

    """

    Generate multiple deep dives with rate limiting

   

    Example:

        topics = [

            ("Nvidia", "how they built the AI infrastructure layer"),

            ("Netflix", "why they won the streaming war"),

            ("Apple", "the strategy behind their services business")

        ]

    """

    results = []

   

    for i, (company, description) in enumerate(topics, 1):

        print(f"\n{'='*70}")

        print(f"Processing {i}/{len(topics)}: {company}")

        print(f"{'='*70}")

       

        result = create_deep_dive(company, description)

        if result:

            results.append(result)

       

        # Wait between requests to respect rate limits

        if i < len(topics):

            print(f"\n⏳ Waiting {DELAY_BETWEEN_REQUESTS} seconds before next deep dive...")

            time.sleep(DELAY_BETWEEN_REQUESTS)

   

    return results



# ==================== RUN EXAMPLES ====================

if __name__ == "__main__":

    # Example 1: Single company

    create_deep_dive("Netflix", "why they won the streaming war")

   

    # Example 2: Multiple companies (uncomment to use)

    # topics = [

    #     ("Netflix", "why they won the streaming war"),

    #     ("Apple", "the strategy behind their services business"),

    #     ("Microsoft", "how they pivoted to cloud and AI")

    # ]

    # create_multiple_deep_dives(topics) 

