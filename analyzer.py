from groq import Groq
import json
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

def analyze_verse(verse):
    prompt = f"""
You are Dr. Panini — the greatest Sanskrit grammarian who ever lived. You have perfect mastery of:
- Ashtadhyayi (Panini's grammar rules)
- Chandas Shastra (Pingala's prosody system)
- Vedic accent system (Udatta, Anudatta, Svarita)
- All 26 classical Sanskrit meters

ANALYZE THIS SANSKRIT VERSE: "{verse}"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK 1: PERFECT SYLLABIFICATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Follow these rules with ABSOLUTE PRECISION:

RULE 1 — ONE VOWEL PER SYLLABLE
Every syllable contains exactly ONE vowel sound.
Devanagari vowels: अ आ इ ई उ ऊ ए ऐ ओ औ ऋ ॠ
Vowel markers (matras): ा ि ी ु ू े ै ो ौ ृ

RULE 2 — ONSET CONSONANTS
A consonant or consonant cluster BEFORE a vowel is the ONSET of that vowel's syllable.
Example: "क्ष" before "ए" → क्षे is ONE syllable

RULE 3 — CODA CONSONANTS
After a vowel, if ONE consonant follows before the next vowel → it joins the NEXT syllable (open syllable = laghu if short vowel)
After a vowel, if TWO OR MORE consonants follow → the FIRST joins THIS syllable (making it a closed syllable = GURU)

RULE 4 — HALANT (्)
A halant joins consonants. The entire cluster is ONE unit.
क्ष = one consonant | त्र = one consonant | ज्ञ = one consonant | ष्ट = one consonant | न्त = one consonant | र्म = one consonant

RULE 5 — LAGHU vs GURU classification
LAGHU (light, short, 1 matra):
  → Short vowel (अ इ उ ऋ) + at most ONE following consonant before next vowel
  → Examples: क, कि, कु, कृ followed by single consonant

GURU (heavy, long, 2 matras):
  → ANY long vowel: आ ई ऊ ए ऐ ओ औ ॠ
  → Short vowel + TWO OR MORE following consonants (conjunct cluster)
  → Short vowel + Anusvara (ं)
  → Short vowel + Visarga (ः)
  → End of a pada (line) — always GURU

RULE 6 — SPECIAL CHARACTERS
Anusvara (ं) = makes preceding syllable GURU, belongs to that syllable
Visarga (ः) = makes preceding syllable GURU, belongs to that syllable
Chandrabindu (ँ) = nasalizes, does NOT make GURU

CONCRETE EXAMPLE — "धर्मक्षेत्रे":
- ध + short अ + र्म (conjunct) → धर्म = GURU (short vowel + conjunct)
- क्ष + long ए + त्र (conjunct) → क्षेत्रे = GURU (long vowel)
Result: [धर्म=G, क्षेत्रे=G]

CONCRETE EXAMPLE — "कुरुक्षेत्रे":
- क + short उ → कु, followed by single र → LAGHU
- र + short उ → रु, followed by cluster क्ष → GURU
- क्ष + long ए + त्र → क्षेत्रे = GURU
Result: [कु=L, रु=G, क्षेत्रे=G]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK 2: ACCURATE METER IDENTIFICATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Count syllables per line (pada). Match the pattern:

SAMAVRITTA meters (equal padas):
| Meter              | Syllables/pada | LG Pattern of pada                |
|--------------------|---------------|-----------------------------------|
| Gayatri            | 8             | L G L G L L G G (3 padas only)   |
| Anushtubh/Shloka   | 8             | any 5-6, then G L G _ (4 padas)  |
| Brihati            | 9             | L L G L G L L G G                |
| Pankti             | 10            | L G L G L G L G L G              |
| Trishtubh          | 11            | G G L G L L L G L G G            |
| Jagati             | 12            | G G L G L L L G L G G G          |
| Vasantatilaka      | 14            | G G L G L L L G L G G L G G      |
| Malini             | 15            | L L L L L L G G L G L L G L G    |
| Mandakranta        | 17            | G G G G L L L L G L G L L G L G G|
| Shardula           | 19            | G G G L L G L G G L G G L G L L G G G|
| Sragdhara          | 21            | G G G L L L G L L L G G L L L G G L G G G|

HOW TO IDENTIFY:
1. Split verse into lines at ।, ॥, or natural pauses
2. Count syllables per line
3. Map the L/G pattern
4. Match against table above
5. If 4 lines of 8 syllables → likely Anushtubh (check positions 5,6,7,8 of each pada)
   - Anushtubh pathya (normal): positions 5=L, 6=G, 7=L, 8=G
   - If only 3 lines → Gayatri
6. DO NOT default to Anushtubh. Count carefully. Be precise.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK 3: SVARA (PITCH ACCENT) ASSIGNMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Rules for Vedic pitch accents:
- udatta = raised, HIGH pitch — the primary accent of a word. Usually on the root syllable or the syllable carrying semantic stress. Every content word has at most one udatta.
- anudatta = LOW pitch — syllables IMMEDIATELY BEFORE an udatta syllable are anudatta
- svarita = FALLING pitch — syllables IMMEDIATELY AFTER an udatta are svarita, then return to anudatta

Pattern: anudatta(s) → UDATTA → svarita → anudatta → anudatta → UDATTA → svarita...

Ensure VARIETY — do not assign the same svara to all syllables.
Typical distribution in a shloka: ~25% udatta, ~50% anudatta, ~25% svarita

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK 4: GANA GROUPING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Group syllables in sets of 3. Name each gaṇa:
GGG=ma | LLL=na | GLL=bha | LGG=ja | LLG=sa | GLG=ra | LGL=ya | GGL=ta

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT FORMAT — ONLY valid JSON, zero extra text:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{{
  "meter": "exact meter name",
  "pada_count": 4,
  "syllables_per_pada": 8,
  "lg_pattern": "G-L-G-L-G-G-L-G",
  "ganas": ["bha","ra","na","ya"],
  "syllables": [
    {{
      "text": "धर्म",
      "type": "guru",
      "svara": "anudatta"
    }},
    {{
      "text": "क्षेत्रे",
      "type": "guru",
      "svara": "udatta"
    }}
  ]
}}

CRITICAL REMINDERS:
- Every syllable text must be in Devanagari
- type must be ONLY "laghu" or "guru"
- svara must be ONLY "udatta", "anudatta", or "svarita"
- Do NOT write any explanation — ONLY the JSON object
- Do NOT use markdown code blocks
- Syllable splitting must be phonetically perfect
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a world-class Sanskrit prosody expert. You return ONLY valid JSON with perfect Sanskrit syllabification. Never add explanation or markdown. Your syllable splitting follows Paninian grammar rules with 100% accuracy."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.0,
        max_tokens=4000
    )

    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json","").replace("```","").strip()

    # find JSON object in response
    start = raw.find("{")
    end   = raw.rfind("}") + 1
    if start != -1 and end > start:
        raw = raw[start:end]

    result = json.loads(raw)

    # auto-generate lg_pattern if missing
    if "lg_pattern" not in result or not result["lg_pattern"]:
        result["lg_pattern"] = "-".join(
            ["G" if s["type"]=="guru" else "L" for s in result["syllables"]]
        )

    if "ganas" not in result:
        result["ganas"] = []

    return result


if __name__ == "__main__":
    tests = [
        "ॐ भूर्भुवः स्वः \nतत्सवितुर्वरेण्यं \nभर्गो देवस्य धीमहि \nधियो यो नः प्रचोदयात्"
    ]
    for verse in tests:
        print(f"\nVerse: {verse}")
        data = analyze_verse(verse)
        print(f"Meter: {data['meter']}")
        print(f"LG:    {data['lg_pattern']}")
        print(f"Syllables: {[s['text'] for s in data['syllables']]}")