from groq import Groq
import json
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

def analyze_verse(verse):
    prompt = f"""
You are an expert in Sanskrit prosody and Vedic linguistics.

Analyze this Sanskrit verse written in Devanagari script: "{verse}"

Follow these STRICT Sanskrit syllabification rules:
- A syllable is ONE vowel sound with its surrounding consonants
- Every Devanagari vowel (अ आ इ ई उ ऊ ए ऐ ओ औ) starts a new syllable
- A consonant before a vowel belongs to THAT syllable
- Anusvara (ं) and Visarga (ः) make the syllable GURU
- A short vowel (अ इ उ ऋ) followed by ONE consonant = LAGHU
- A long vowel (आ ई ऊ ए ऐ ओ औ) = always GURU
- A short vowel followed by TWO or more consonants = GURU
- Conjunct consonants (like क्ष त्र ज्ञ) count as TWO consonants

For svaras follow these rules:
- Udatta = the main accented syllable (usually the root syllable)
- Anudatta = unaccented syllable just before udatta
- Svarita = syllable immediately after udatta

Return ONLY a valid JSON object. No explanation. No markdown. Just raw JSON like this:
{{
  "meter": "name of meter (e.g. Anushtubh)",
  "lg_pattern": "G-L-G-G-L-G (use G for guru, L for laghu, separated by -)",
  "ganas": ["ma", "ta", "ra"],
  "syllables": [
    {{
      "text": "exact Devanagari syllable",
      "type": "laghu or guru",
      "svara": "udatta or anudatta or svarita"
    }}
  ]
}}

For ganas — group every 3 syllables into one gana and name it:
- G G G = ma gana
- L L L = na gana  
- G L L = bha gana
- L G G = ja gana
- L L G = sa gana
- G L G = ra gana
- L G L = ya gana
- G G L = ta gana
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )

    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    result = json.loads(raw)

    # make sure all fields exist even if AI missed them
    if "lg_pattern" not in result:
        pattern = "-".join(["G" if s["type"] == "guru" else "L" for s in result["syllables"]])
        result["lg_pattern"] = pattern

    if "ganas" not in result:
        result["ganas"] = []

    return result


# TEST
if __name__ == "__main__":
    test_verse = "धर्मक्षेत्रे कुरुक्षेत्रे"
    print("Sending to Groq AI...")
    data = analyze_verse(test_verse)
    print("Got back:")
    print(json.dumps(data, ensure_ascii=False, indent=2))

import json
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

def analyze_verse(verse):
    prompt = f"""
You are an expert in Sanskrit prosody and Vedic linguistics.

Analyze this Sanskrit verse written in Devanagari script: "{verse}"

Follow these STRICT Sanskrit syllabification rules:
- A syllable is ONE vowel sound with its surrounding consonants
- Every Devanagari vowel (अ आ इ ई उ ऊ ए ऐ ओ औ) starts a new syllable
- A consonant before a vowel belongs to THAT syllable
- Anusvara (ं) and Visarga (ः) make the syllable GURU
- A short vowel (अ इ उ ऋ) followed by ONE consonant = LAGHU
- A long vowel (आ ई ऊ ए ऐ ओ औ) = always GURU
- A short vowel followed by TWO or more consonants = GURU
- Conjunct consonants (like क्ष त्र ज्ञ) count as TWO consonants

For svaras follow these rules:
- Udatta = the main accented syllable (usually the root syllable)
- Anudatta = unaccented syllable just before udatta
- Svarita = syllable immediately after udatta

Return ONLY a valid JSON object. No explanation. No markdown. Just raw JSON like this:
{{
  "meter": "name of meter (e.g. Anushtubh)",
  "lg_pattern": "G-L-G-G-L-G (use G for guru, L for laghu, separated by -)",
  "ganas": ["ma", "ta", "ra"],
  "syllables": [
    {{
      "text": "exact Devanagari syllable",
      "type": "laghu or guru",
      "svara": "udatta or anudatta or svarita"
    }}
  ]
}}

For ganas — group every 3 syllables into one gana and name it:
- G G G = ma gana
- L L L = na gana  
- G L L = bha gana
- L G G = ja gana
- L L G = sa gana
- G L G = ra gana
- L G L = ya gana
- G G L = ta gana
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )

    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    result = json.loads(raw)

    # make sure all fields exist even if AI missed them
    if "lg_pattern" not in result:
        pattern = "-".join(["G" if s["type"] == "guru" else "L" for s in result["syllables"]])
        result["lg_pattern"] = pattern

    if "ganas" not in result:
        result["ganas"] = []

    return result


# TEST
if __name__ == "__main__":
    test_verse = "धर्मक्षेत्रे कुरुक्षेत्रे"
    print("Sending to Groq AI...")
    data = analyze_verse(test_verse)
    print("Got back:")
    print(json.dumps(data, ensure_ascii=False, indent=2))
