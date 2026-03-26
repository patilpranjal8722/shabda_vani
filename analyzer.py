from groq import Groq
import json
from config import GROQ_API_KEY

# connect to Groq
client = Groq(api_key=GROQ_API_KEY)

def analyze_verse(verse):
    prompt = f"""
You are a Sanskrit linguistics expert.

Analyze this Sanskrit verse: "{verse}"

Return ONLY a JSON object. No explanation, no extra text, just JSON.

The JSON must look exactly like this:
{{
  "meter": "name of the meter (e.g. Anushtubh)",
  "syllables": [
    {{
      "text": "the syllable",
      "type": "laghu",
      "svara": "anudatta"
    }}
  ]
}}

Rules:
- type must be either "laghu" or "guru"
- svara must be either "udatta", "anudatta", or "svarita"
- split the verse into individual syllables
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    # clean the response and parse JSON
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    result = json.loads(raw)
    return result


# TEST
if __name__ == "__main__":
    test_verse = "धर्मक्षेत्रे कुरुक्षेत्रे"
    print("Sending to Groq AI...")
    data = analyze_verse(test_verse)
    print("Got back:")
    print(json.dumps(data, ensure_ascii=False, indent=2))