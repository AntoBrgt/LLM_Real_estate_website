import json
from langchain.prompts import PromptTemplate
from typing import Dict, Any

# Example of output
EXAMPLE_LISTING = """
<title>T3 Apartment for Sale in Campo de Ourique</title>
<meta name="description" content="Bright 3-bedroom T3 apartment in Lisbon with balcony. Perfect for families.">
<h1>Bright T3 Apartment with Balcony in Campo de Ourique</h1>
<section id="description">
<p>Located in Campo de Ourique, Lisbon, this spacious T3 apartment of approx 120 sqm offers 3 bedrooms, 2 bathrooms, and a private balcony. Recently renovated, it blends modern comfort with a prime location. Local shops, cafés, and public transport are all within walking distance, making it ideal for families or professionals. Enjoy the vibrant neighborhood and easy access to Lisbon's cultural attractions.</p>
</section>
<ul id="key-features">
<li>120 sqm of living space</li>
<li>3 bedrooms and 2 bathrooms</li>
<li>Private balcony</li>
<li>Elevator access</li>
</ul>
<section id="neighborhood">
<p>Campo de Ourique is known for its lively cafés, boutique shops, and green parks, offering a village-like atmosphere in the heart of Lisbon.</p>
</section>
<p class="call-to-action">Don't miss this opportunity—schedule your visit today.</p>
"""

# Example of tone
FEW_SHOT_SEEDS = {
    "friendly": ["T3 apartment for sale in Campo de Ourique, Lisbon — bright 3-bedroom with balcony. Great for families."],
    "formal": ["Apartment for sale in Lisbon (Campo de Ourique). Three-bedroom T3, 120 sqm. Suitable for professionals."],
    "luxury": ["Exclusive T3 apartment in Campo de Ourique, Lisbon. Designer finishes, private balcony, prime location."],
    "investor": ["Investment opportunity: T3 apartment in Campo de Ourique, Lisbon. Strong rental demand, 120 sqm, well-located."]
}

# -------- Prompt template  --------
BASE_PROMPT = """
You are a skilled real estate copywriter and HTML formatter.

YOUR GOAL: Output **exactly one** valid, final HTML listing on the first try — no extra text.

=============================
STRICT RULES (MUST FOLLOW)
=============================
1. Output exactly 7 HTML blocks in this exact order, with tags unchanged:
   <title>...</title>
   <meta name="description" content="...">
   <h1>...</h1>
   <section id="description"><p>...</p></section>
   <ul id="key-features"> ... <li>...</li> ... </ul>
   <section id="neighborhood"><p>...</p></section>
   <p class="call-to-action">...</p>

2. Constraints:
   - Title length: ≤ 60 characters. If too long, shorten it without losing key info.
   - Meta description length: ≤ 155 characters. If too long, shorten it without losing key info.
   - Description paragraph length: between 500 and 700 characters. If too long, shorten it without losing key info.
   - Key features: between 3 and 5 <li> items.
   - Preserve HTML tags exactly, do not rename, reorder, or add new ones.
   - If any input field is missing, use neutral phrasing like "details not listed" — never invent data.

3. Pricing format:
   - English and others: €650,000 → "€650,000"
   - Portuguese: €650.000 → "650.000€"

4. SEO:
   - Include natural phrases like "apartment for sale in {city}", "T3 apartment in {neighborhood}", "real estate in Portugal" when possible, but do NOT keyword-stuff.

=============================
THINK-THEN-OUTPUT METHOD
=============================
Before you write HTML:
1. Decide each section's text content.
2. Check length rules for title, meta, description.
3. Count <li> items to ensure exactly 3-5.
4. Self-correct if any rule is broken.
5. THEN output the final HTML in one single block.

=============================
GOOD EXAMPLE (format + style)
=============================

{EXAMPLE_LISTING}

=============================
STYLE & TONE
=============================
Tone: {tone}
Use these seed examples for tone guidance:
{few_shot}

=============================
INPUT DATA
=============================
INPUT_JSON:
{data}

TARGET_LANGUAGE: {language}

=============================
FINAL INSTRUCTION
=============================
Output ONLY the valid HTML with correct tags, correct order, and constraints respected.
Do not include explanations, notes, or multiple versions.

If TARGET_LANGUAGE is 'fr', output all HTML text in French.
If TARGET_LANGUAGE is 'pt', output all HTML text in Portuguese.
If TARGET_LANGUAGE is 'sp', output all HTML text in Spanish.
If TARGET_LANGUAGE is 'it', output all HTML text in Italian.
If TARGET_LANGUAGE is 'en', output all HTML text in English.

IMPORTANT: The <p> description MUST be between 500 and 700 characters inclusive.  
- Count all characters including spaces and punctuation.  
- If the description is too short, add more relevant details to reach the minimum length.  
- If too long, shorten without losing key information.  
- Do NOT produce text outside these length constraints.  
- Output exactly one valid HTML block with tags in order, no extra text.  
- Confirm description length before finishing.

"""

LANGUAGE_MAP = {
    "en": "English",
    "fr": "French",
    "pt": "Portuguese",
    "sp": "Spanish",
    "it": "Italian"
}

PROMPT = PromptTemplate(
    input_variables=["few_shot", "data", "language", "tone", "EXAMPLE_LISTING"],
    template=BASE_PROMPT
)

def build_prompt(data: Dict[str, Any], language: str, tone: str) -> str:
    seeds = FEW_SHOT_SEEDS.get(tone, [])
    few_shot = "\n".join(f"- {s}" for s in seeds)
    language_name = LANGUAGE_MAP.get(language, "English")
    city = data.get("location", {}).get("city", "")
    neighborhood = data.get("location", {}).get("neighborhood", "")

    return PROMPT.format(
        few_shot=few_shot,
        data=json.dumps(data, ensure_ascii=False),
        language=language,
        tone=tone,
        EXAMPLE_LISTING=EXAMPLE_LISTING,
        city=city,
        language_name=language_name,
        neighborhood=neighborhood
    )
