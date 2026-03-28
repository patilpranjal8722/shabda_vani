import streamlit as st
import numpy as np
import io
import wave
import time
import os
import plotly.graph_objects as go
from scipy.signal import butter, filtfilt, resample
from analyzer import analyze_verse

st.set_page_config(page_title="ShrutiLaya", page_icon="🕉️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Crimson+Text:ital,wght@0,400;0,600;1,400&display=swap');
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
        background: linear-gradient(160deg, #f5b942 0%, #e8922a 35%, #d4701a 65%, #c8601a 100%) !important;
    }
    [data-testid="stHeader"] { background: rgba(160,70,10,0.92) !important; width: 100% !important; }
    .main .block-container { background: transparent !important; padding: 1rem 2rem 2rem 2rem; max-width: 1100px; margin: 0 auto; }
    [data-testid="stAppViewContainer"]::before {
        content: ''; position: fixed; top: 0; left: 0; right: 0; bottom: 0;
        background-image:
            radial-gradient(circle at 10% 20%, rgba(120,50,5,0.12) 0%, transparent 50%),
            radial-gradient(circle at 90% 80%, rgba(120,50,5,0.12) 0%, transparent 50%),
            radial-gradient(circle at 50% 50%, rgba(120,50,5,0.08) 0%, transparent 60%),
            radial-gradient(circle at 10% 80%, rgba(120,50,5,0.10) 0%, transparent 40%),
            radial-gradient(circle at 90% 20%, rgba(120,50,5,0.10) 0%, transparent 40%);
        pointer-events: none; z-index: 0;
    }
    .mandala-border { width:100%; text-align:center; color:rgba(80,25,0,0.45); font-size:1.3rem; letter-spacing:6px; padding:6px 0; border-bottom:1.5px solid rgba(100,40,5,0.3); margin-bottom:1rem; overflow:hidden; white-space:nowrap; }
    h1 { font-family:'Cinzel',serif !important; color:#2a0e00 !important; text-align:center; font-size:3rem !important; font-weight:700 !important; text-shadow:1px 1px 0px rgba(255,220,150,0.4); letter-spacing:6px; }
    h2,h3 { font-family:'Cinzel',serif !important; color:#2a0e00 !important; }
    p,label,div { color:#2a0e00 !important; }
    .stMarkdown p { color:#2a0e00 !important; }
    .subtitle { text-align:center; color:#3a1200 !important; font-family:'Crimson Text',serif; font-size:1.3rem; font-style:italic; letter-spacing:3px; }
    .om-divider { text-align:center; color:rgba(70,20,0,0.5); font-size:1.1rem; letter-spacing:8px; margin:0.8rem 0; }
    .stat-card { background:rgba(255,230,160,0.45); border:1.5px solid rgba(120,50,10,0.5); border-radius:12px; padding:14px 10px; text-align:center; box-shadow:3px 4px 10px rgba(100,30,0,0.25); }
    .stat-num { font-size:1.8rem; font-weight:bold; color:#2a0e00 !important; font-family:'Cinzel',serif; }
    .stat-label { font-size:0.8rem; color:#4a1a00 !important; margin-top:4px; font-family:'Crimson Text',serif; }
    .meter-badge { background:rgba(100,35,5,0.75); border:1.5px solid rgba(255,200,100,0.6); border-radius:20px; padding:8px 24px; color:#fde8b0 !important; font-family:'Cinzel',serif; font-size:1rem; font-weight:bold; display:inline-block; margin-bottom:1rem; box-shadow:3px 4px 12px rgba(80,20,0,0.4); }
    .pattern-box { background:rgba(255,230,160,0.35); border:1px solid rgba(100,40,5,0.5); border-radius:10px; padding:10px 16px; color:#2a0e00 !important; font-size:1.2rem; letter-spacing:4px; font-family:monospace; display:inline-block; box-shadow:inset 0 1px 4px rgba(0,0,0,0.1); }
    .gana-box { background:rgba(255,230,160,0.35); border:1px solid rgba(150,80,20,0.5); border-radius:10px; padding:8px 16px; color:#2a0e00 !important; font-size:1.1rem; letter-spacing:6px; font-family:monospace; display:inline-block; }
    .info-box { background:rgba(255,230,160,0.3); border-left:3px solid rgba(120,50,10,0.7); border-radius:0 8px 8px 0; padding:0.8rem 1rem; margin:0.5rem 0; color:#2a0e00 !important; font-family:'Crimson Text',serif; font-size:1rem; line-height:1.7; font-style:italic; }
    .shruti-badge { background:rgba(80,25,5,0.80); border:1.5px solid rgba(255,200,80,0.7); border-radius:10px; padding:10px 18px; color:#fde8b0 !important; font-family:'Crimson Text',serif; font-size:0.95rem; line-height:1.8; margin-bottom:0.8rem; }
    .learn-card { background:rgba(255,235,175,0.55); border:1.5px solid rgba(120,55,10,0.5); border-radius:14px; padding:18px 20px; margin-bottom:1rem; box-shadow:3px 5px 14px rgba(80,20,0,0.2); }
    .learn-card h4 { font-family:'Cinzel',serif !important; color:#2a0e00 !important; font-size:1.05rem; margin-bottom:0.5rem; letter-spacing:2px; }
    .learn-card p { color:#2a0e00 !important; font-family:'Crimson Text',serif; font-size:1.05rem; line-height:1.75; }
    .learn-highlight { background:rgba(100,35,5,0.12); border-left:3px solid rgba(150,60,10,0.8); border-radius:0 8px 8px 0; padding:8px 14px; margin:6px 0; color:#2a0e00 !important; font-family:'Crimson Text',serif; font-size:1rem; line-height:1.7; }
    .syl-learn-card { background:rgba(255,225,140,0.5); border:1px solid rgba(120,50,10,0.4); border-radius:10px; padding:10px 8px; text-align:center; box-shadow:2px 3px 7px rgba(100,30,0,0.18); }
    .syl-learn-text { font-size:1.15rem; font-weight:bold; color:#2a0e00 !important; font-family:serif; }
    .syl-learn-sub { font-size:0.65rem; color:#4a1a00 !important; margin-top:3px; font-family:'Crimson Text',serif; }
    .pronunciation-row { background:rgba(255,230,160,0.4); border:1px solid rgba(130,60,10,0.4); border-radius:10px; padding:12px 16px; margin:6px 0; font-family:'Crimson Text',serif; }

    /* ── Mode buttons — styled like generate button ── */
    .mode-wrap { display:flex; justify-content:center; gap:16px; margin:0.6rem 0 0.4rem; }
    .mode-btn-active {
        background: linear-gradient(145deg,#b04a08,#d06820,#b04a08);
        color: #fde8b0 !important;
        font-family: 'Cinzel', serif;
        font-weight: 600; font-size: 0.95rem;
        border: 2px solid rgba(255,200,100,0.8);
        border-radius: 12px;
        padding: 10px 28px;
        letter-spacing: 2px;
        box-shadow: 3px 5px 14px rgba(70,20,0,0.5), inset 0 1px 2px rgba(255,220,150,0.25);
        text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
        cursor: pointer; transition: all 0.2s ease;
    }
    .mode-btn-inactive {
        background: rgba(255,225,150,0.35);
        color: #3a1000 !important;
        font-family: 'Cinzel', serif;
        font-weight: 600; font-size: 0.95rem;
        border: 2px solid rgba(120,50,10,0.55);
        border-radius: 12px;
        padding: 10px 28px;
        letter-spacing: 2px;
        box-shadow: 2px 3px 8px rgba(80,20,0,0.25);
        cursor: pointer; transition: all 0.2s ease;
    }
    .mode-btn-inactive:hover { background: rgba(255,210,120,0.55); }

    /* ── Main buttons ── */
    .stButton > button { background:linear-gradient(145deg,#b04a08,#d06820,#b04a08) !important; color:#fde8b0 !important; font-family:'Cinzel',serif !important; font-weight:600 !important; font-size:1rem !important; border:2px solid rgba(255,200,100,0.65) !important; border-radius:12px !important; padding:0.65rem 1.5rem !important; width:100% !important; letter-spacing:2px !important; box-shadow:3px 5px 14px rgba(70,20,0,0.5),inset 0 1px 2px rgba(255,220,150,0.25) !important; text-shadow:1px 1px 3px rgba(0,0,0,0.5) !important; transition:all 0.2s ease !important; }
    .stButton > button:hover { background:linear-gradient(145deg,#d06820,#e07830,#d06820) !important; transform:translateY(-2px) !important; }
    .stButton > button:active { transform:translateY(1px) !important; }
    .stDownloadButton > button { background:linear-gradient(145deg,#7a2e08,#a04818) !important; color:#fde8b0 !important; border:2px solid rgba(255,200,100,0.6) !important; border-radius:10px !important; box-shadow:3px 4px 10px rgba(60,15,0,0.45) !important; font-family:'Cinzel',serif !important; text-shadow:1px 1px 2px rgba(0,0,0,0.4) !important; }
    .stDownloadButton > button:hover { transform:translateY(-2px) !important; }
    .stTextArea textarea { background:rgba(255,235,175,0.5) !important; color:#1a0800 !important; border:1.5px solid rgba(120,50,10,0.5) !important; font-size:1.3rem !important; font-family:'Crimson Text',serif !important; border-radius:10px !important; }
    .stSelectbox > div > div { background:rgba(255,235,175,0.45) !important; color:#1a0800 !important; border:1.5px solid rgba(120,50,10,0.5) !important; border-radius:8px !important; }
    [data-testid="stAlert"] { background:rgba(255,235,175,0.4) !important; border:1px solid rgba(120,60,10,0.4) !important; color:#1a0800 !important; border-radius:10px !important; }
    [data-testid="stRadio"] { display:none !important; }
    hr { border-color:rgba(100,40,5,0.3) !important; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# AUDIO ENGINE
# ═══════════════════════════════════════════════════════════════

SR       = 44100
BASE_SA  = 130.81
SHRUTI_FREQS = {
    "anudatta": BASE_SA,
    "svarita":  BASE_SA * (4/3),
    "udatta":   BASE_SA * (3/2),
}
DURATION_MS = {"laghu": 420, "guru": 840}
PITCH_LABELS = {
    "anudatta": BASE_SA,
    "svarita":  BASE_SA * (4/3),
    "udatta":   BASE_SA * (3/2),
}
ALL_GANAS = ["ma", "na", "bha", "ja", "sa", "ra", "ya", "ta"]

def make_shruti_tone(freq, dur_ms, svara="svarita"):
    n  = int(SR * dur_ms / 1000)
    t  = np.linspace(0, dur_ms/1000, n)
    harmonics = [(1,1.00),(2,0.72),(3,0.50),(4,0.32),(5,0.20),(6,0.12),(7,0.07),(8,0.04),(9,0.02)]
    sig = np.zeros(n)
    for h, amp in harmonics:
        sig += amp * np.sin(2*np.pi*freq*h*t)
    if svara == "udatta":
        sig += 0.16 * np.sin(2*np.pi*freq*2.5*t)
    elif svara == "anudatta":
        sig += 0.13 * np.sin(2*np.pi*freq*1.5*t)
    att = int(SR*0.055); dec = int(SR*0.09); rel = int(SR*0.16)
    sus = max(0, n-att-dec-rel)
    env = np.concatenate([np.linspace(0,1,att), np.linspace(1,0.86,dec), np.full(sus,0.86), np.linspace(0.86,0,rel)])
    sig *= env[:n]
    onset = int(n*0.15)
    ramp  = np.concatenate([np.zeros(onset), np.linspace(0,1,n-onset)])
    sig  *= 1 + 0.011*ramp*np.sin(2*np.pi*5.8*t)
    gn = int(SR*0.055)
    if gn < n:
        gt   = np.linspace(0, 0.055, gn)
        gsig = np.sin(2*np.pi*freq*0.96*gt)
        blend = np.linspace(0,1,gn)
        sig[:gn] = sig[:gn]*blend + gsig*(1-blend)*env[:gn]
    mx = np.max(np.abs(sig))
    return sig/mx if mx>0 else sig

def make_tanpura_drone(n_samples):
    t = np.linspace(0, n_samples/SR, n_samples)
    drone = np.zeros(n_samples)
    strings = [(BASE_SA*1.5,1.00,0.00),(BASE_SA,0.90,0.04),(BASE_SA,0.88,0.09),(BASE_SA*2,0.55,0.15)]
    for freq, amp, phase in strings:
        for h, hw in [(1,1.0),(2,0.50),(3,0.28),(4,0.14),(5,0.07)]:
            drone += amp*hw*np.sin(2*np.pi*freq*h*t+phase*SR)
    b, a = butter(2, 1400/(SR/2), btype='low')
    drone = filtfilt(b, a, drone)
    mx = np.max(np.abs(drone))
    return drone/mx*0.20 if mx>0 else drone

def apply_temple_reverb(sig):
    delays_ms=[41,79,113,157,199]; decays=[0.42,0.28,0.18,0.10,0.06]
    tail=int(SR*1.0); out=np.zeros(len(sig)+tail)
    out[:len(sig)] = sig
    for d_ms, decay in zip(delays_ms, decays):
        d=int(SR*d_ms/1000)
        out[d:d+len(sig)] += sig*decay
    mx=np.max(np.abs(out))
    return out/mx if mx>0 else out

def generate_shruti_audio(syllables):
    parts = []
    for syl in syllables:
        freq   = SHRUTI_FREQS.get(syl["svara"], SHRUTI_FREQS["svarita"])
        dur_ms = DURATION_MS.get(syl["type"], 420)
        tone   = make_shruti_tone(freq, dur_ms, syl["svara"])
        gap_ms = 30 if syl["type"]=="laghu" else 52
        parts.append(tone)
        parts.append(np.zeros(int(SR*gap_ms/1000)))
    chant = np.concatenate(parts)
    drone = make_tanpura_drone(len(chant))
    mixed = chant*0.80 + drone[:len(chant)]
    b, a  = butter(3, 5500/(SR/2), btype='low')
    mixed = filtfilt(b, a, mixed)
    mixed = apply_temple_reverb(mixed)
    mx=np.max(np.abs(mixed)); mixed=mixed/mx*0.90 if mx>0 else mixed
    mixed=np.tanh(mixed*1.1)/np.tanh(np.array([1.1]))[0]
    mx=np.max(np.abs(mixed)); mixed=mixed/mx*0.88 if mx>0 else mixed
    fade=int(SR*0.35)
    mixed[:fade]  *= np.linspace(0,1,fade)
    mixed[-fade:] *= np.linspace(1,0,fade)
    pcm = np.int16(mixed*32767)
    buf = io.BytesIO()
    with wave.open(buf,'w') as w:
        w.setnchannels(1); w.setsampwidth(2)
        w.setframerate(SR); w.writeframes(pcm.tobytes())
    buf.seek(0)
    return buf

def get_syllable_timings(syllables):
    timings = []
    t = 0.0
    for syl in syllables:
        dur_ms = DURATION_MS.get(syl["type"], 420)
        gap_ms = 30 if syl["type"]=="laghu" else 52
        timings.append({"text":syl["text"],"svara":syl["svara"],"type":syl["type"],"start":t,"end":t+dur_ms/1000.0})
        t += dur_ms/1000.0 + gap_ms/1000.0
    return timings

# ═══════════════════════════════════════════════════════════════
# LEARNING MODE
# ═══════════════════════════════════════════════════════════════

VERSE_LIBRARY = {
    "धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः": {
        "source":      "Bhagavad Gītā — Chapter 1, Verse 1",
        "translation": "On the sacred field of Kurukshetra, assembled together and eager to fight…",
        "meaning":     "King Dhritarashtra asks Sanjaya what his sons and the Pandavas did when they assembled on the sacred battlefield of Kurukshetra. The word 'dharma-kshetra' signals this is not merely a physical battle but a spiritual and moral one.",
        "context":     "This is the very first verse of the Bhagavad Gita, spoken by the blind king Dhritarashtra. It sets the stage for the 700-verse dialogue between Arjuna and Lord Krishna.",
        "meter":       "Anushtubh (अनुष्टुभ्) — 8 syllables per pada, 4 padas.",
        "keywords": [
            ("धर्मक्षेत्रे","dharma-kṣetre","On the field of righteousness"),
            ("कुरुक्षेत्रे","kuru-kṣetre","At Kurukshetra — the battlefield"),
            ("समवेताः","samavetāḥ","Assembled / gathered together"),
            ("युयुत्सवः","yuyutsavaḥ","Desiring to fight / eager for battle"),
        ],
        "chanting_tip": "Begin slowly. Hold each guru syllable for 2 beats. The verse should feel heavy and majestic.",
        "fun_fact":     "Kurukshetra is a real city in Haryana, India. The battle is believed to have taken place around 3102 BCE.",
    },
    "वक्रतुण्ड महाकाय सूर्यकोटि समप्रभ": {
        "source":      "Ganesha Shloka — Traditional invocation",
        "translation": "O Lord Ganesha, with a curved trunk and a large body, who shines like a million suns…",
        "meaning":     "A prayer to Lord Ganesha, the remover of obstacles. His curved trunk and large body are praised, and his brilliance is compared to a million suns.",
        "context":     "Traditionally recited at the beginning of any auspicious work, study, or journey. Ganesha is the deity of wisdom and new beginnings.",
        "meter":       "Anushtubh (अनुष्टुभ्) — 8 syllables per pada.",
        "keywords": [
            ("वक्रतुण्ड","vakra-tuṇḍa","Curved trunk — Ganesha's elephant trunk"),
            ("महाकाय","mahā-kāya","Large bodied — Ganesha's massive form"),
            ("सूर्यकोटि","sūrya-koṭi","A million suns — his radiance"),
            ("समप्रभ","sama-prabhā","Of equal brilliance"),
        ],
        "chanting_tip": "Chant with devotion and steady rhythm. Each syllable should resonate in your chest.",
        "fun_fact":     "This is one of the most widely chanted shlokas in India, recited before exams and new beginnings.",
    }
}

SVARA_LEARN = {
    "udatta":   ("Udātta ⬆️",   "High pitch — the raised accent. Strong, bright, upward energy.",   "#6b1a00","#fde8b0"),
    "svarita":  ("Svarita ↘️",  "Falling accent — begins high and glides down. Wave-like melodious quality.", "#8a3510","#fde8b0"),
    "anudatta": ("Anudātta ⬇️", "Low pitch — the unaccented base tone. Deep, resonant, stable energy.", "#1a3a6b","#e8d5ff"),
}

GANA_MEANINGS = {
    "ma":("म","ma-gaṇa","–––","Three guru syllables. Heaviest gaṇa."),
    "na":("न","na-gaṇa","⏑⏑⏑","Three laghu syllables. Lightest and fastest."),
    "bha":("भ","bha-gaṇa","–⏑⏑","Guru + two laghu. Descending weight."),
    "ja":("ज","ja-gaṇa","⏑–⏑","Laghu–Guru–Laghu. Balanced, lyrical feel."),
    "sa":("स","sa-gaṇa","⏑⏑–","Two laghu + guru. Ascending weight."),
    "ra":("र","ra-gaṇa","–⏑–","Guru–Laghu–Guru. Stately, dignified."),
    "ya":("य","ya-gaṇa","⏑––","Laghu + two guru. Rising weight."),
    "ta":("त","ta-gaṇa","––⏑","Two guru + laghu. Falls from heavy to light."),
}

def build_learning_panel(verse, syllables, lg_pattern, ganas, meter, data):
    info = VERSE_LIBRARY.get(verse.strip())
    st.markdown("### 📖 About This Verse")
    if info:
        st.markdown(f'<div class="learn-card"><h4>📜 {info["source"]}</h4><p><i>"{info["translation"]}"</i></p></div>', unsafe_allow_html=True)
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f'<div class="learn-card"><h4>💡 Meaning</h4><p>{info["meaning"]}</p></div>', unsafe_allow_html=True)
        with col_b:
            st.markdown(f'<div class="learn-card"><h4>🏛️ Context</h4><p>{info["context"]}</p></div>', unsafe_allow_html=True)
        st.markdown("#### 🔤 Word-by-Word Breakdown")
        kw_cols = st.columns(len(info["keywords"]))
        for ci,(skt,roman,meaning) in enumerate(info["keywords"]):
            with kw_cols[ci]:
                st.markdown(f'<div class="syl-learn-card"><div class="syl-learn-text">{skt}</div><div class="syl-learn-sub" style="font-style:italic;">{roman}</div><div class="syl-learn-sub">{meaning}</div></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div class="learn-highlight">🎵 <b>Chanting Tip:</b> {info["chanting_tip"]}</div><div class="learn-highlight">🌟 <b>Did You Know?</b> {info["fun_fact"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="learn-card"><h4>📜 Verse Information</h4><p>This verse is not yet in the library. The prosodic analysis below is auto-generated.</p></div>', unsafe_allow_html=True)

    st.markdown("<div class='om-divider'>· · · 🪷 · · ·</div>", unsafe_allow_html=True)
    st.markdown("### 📐 Understanding the Meter (Chanda)")
    meter_info = {
        "Anushtubh":     ("अनुष्टुभ्","8 syllables × 4 padas = 32 total","Most widely used Vedic meter. Found in Bhagavad Gita, Ramayana, Mahabharata.","🐢 Steady and balanced — like a slow river."),
        "Gayatri":       ("गायत्री","8 syllables × 3 padas = 24 total","Most sacred Vedic meter. The Gayatri Mantra uses this meter.","☀️ Pure and luminous — like sunrise."),
        "Trishtubh":     ("त्रिष्टुभ्","11 syllables × 4 padas = 44 total","Used in Rigveda for heroic hymns. Noble and commanding quality.","⚡ Powerful and heroic — like thunder."),
        "Jagati":        ("जगती","12 syllables × 4 padas = 48 total","Extended meter used in later Sanskrit literature. Flowing and lyrical.","🌊 Flowing and expansive — like the ocean."),
        "Vasantatilaka": ("वसन्ततिलका","14 syllables × 4 padas = 56 total","Classical meter used by Kalidasa. Distinctive flowing quality.","🌸 Graceful — like spring blossoms."),
        "Mandakranta":   ("मन्दाक्रान्ता","17 syllables × 4 padas","Meter of longing. Used in Kalidasa's Meghaduta.","💙 Melancholic — like waiting for rain."),
        "Shardula":      ("शार्दूलविक्रीडितम्","19 syllables × 4 padas","The Tiger's Play. Majestic and powerful.","🐯 Majestic — like a tiger in motion."),
        "Unknown":       ("अज्ञात","Non-standard syllable count","Does not match a standard classical meter.","🔍 Explore freely."),
    }
    mn,mdesc,mexp,mfeel = meter_info.get(meter, meter_info["Unknown"])
    st.markdown(f'<div class="learn-card"><h4>🎼 {meter} ({mn})</h4><p><b>Structure:</b> {mdesc}</p><p>{mexp}</p><div class="learn-highlight">✨ <b>Feel:</b> {mfeel}</div></div>', unsafe_allow_html=True)

    st.markdown("<div class='om-divider'>· · · 🪷 · · ·</div>", unsafe_allow_html=True)
    st.markdown("### 🔊 Syllable Pronunciation Guide")
    st.markdown('<div class="learn-highlight">📌 🟫 <b>Guru</b> = hold 2 beats &nbsp;|&nbsp; 🟦 <b>Laghu</b> = hold 1 beat &nbsp;|&nbsp; ⬆️ Udātta = high &nbsp;|&nbsp; ⬇️ Anudātta = low &nbsp;|&nbsp; ↘️ Svarita = glide down</div>', unsafe_allow_html=True)
    n_cols = min(len(syllables), 8)
    rows   = [syllables[i:i+n_cols] for i in range(0, len(syllables), n_cols)]
    svara_icons = {"udatta":"⬆️","anudatta":"⬇️","svarita":"↘️"}
    svara_name  = {"udatta":"Udātta","anudatta":"Anudātta","svarita":"Svarita"}
    for row in rows:
        cols = st.columns(len(row))
        for ci, syl in enumerate(row):
            with cols[ci]:
                g_color = "#6b1a00" if syl["type"]=="guru" else "#1a3a6b"
                st.markdown(f'<div class="syl-learn-card"><div class="syl-learn-text">{syl["text"]}</div><div class="syl-learn-sub" style="color:{g_color}!important;font-weight:bold;">{"🟫 Guru · 2 beats" if syl["type"]=="guru" else "🟦 Laghu · 1 beat"}</div><div class="syl-learn-sub">{svara_icons.get(syl["svara"],"")} {svara_name.get(syl["svara"],"")}</div></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div class="pronunciation-row"><b>LG Pattern:</b> <span style="font-family:monospace;font-size:1.1rem;letter-spacing:5px;">{lg_pattern}</span> &nbsp;|&nbsp; <b>Total:</b> {len(syllables)} &nbsp;|&nbsp; <b>Guru:</b> {sum(1 for s in syllables if s["type"]=="guru")} &nbsp;|&nbsp; <b>Laghu:</b> {sum(1 for s in syllables if s["type"]=="laghu")}</div>', unsafe_allow_html=True)

    st.markdown("<div class='om-divider'>· · · 🪷 · · ·</div>", unsafe_allow_html=True)
    st.markdown("### 🎵 The Three Vedic Svaras")
    sv_cols = st.columns(3)
    for ci, sv in enumerate(["udatta","svarita","anudatta"]):
        name, desc, bg, fg = SVARA_LEARN[sv]
        count = sum(1 for s in syllables if s["svara"]==sv)
        with sv_cols[ci]:
            st.markdown(f'<div class="learn-card" style="border-left:4px solid {bg};"><h4>{name}</h4><p>{desc}</p><div class="syl-learn-sub" style="font-size:0.85rem;">Appears <b>{count}</b> time(s)</div></div>', unsafe_allow_html=True)

    if ganas:
        from collections import Counter
        st.markdown("<div class='om-divider'>· · · 🪷 · · ·</div>", unsafe_allow_html=True)
        st.markdown("### 🧩 Gaṇa Breakdown")
        count = Counter(ganas)
        seen  = set(); unique_ganas = []
        for g in ganas:
            if g not in seen and g in GANA_MEANINGS:
                unique_ganas.append((g, count[g])); seen.add(g)
        g_cols = st.columns(min(len(unique_ganas), 4))
        for ci, (g, c) in enumerate(unique_ganas):
            letter, roman, pattern, meaning = GANA_MEANINGS[g]
            with g_cols[ci % len(g_cols)]:
                st.markdown(f'<div class="syl-learn-card" style="padding:12px;"><div style="font-size:1.5rem;color:#2a0e00!important;">{letter}</div><div class="syl-learn-sub" style="font-style:italic;">{roman}</div><div style="font-family:monospace;font-size:1rem;letter-spacing:4px;color:#2a0e00!important;">{pattern}</div><div class="syl-learn-sub">{meaning} · Used <b>{c}</b>×</div></div>', unsafe_allow_html=True)

    st.markdown("<div class='om-divider'>· · · 🪷 · · ·</div>", unsafe_allow_html=True)
    st.markdown("### 🧘 How to Chant This Verse")
    st.markdown('<div class="learn-card"><h4>🕉️ Step-by-Step Chanting Guide</h4><p><b>1. Posture</b> — Sit comfortably, spine straight, jaw and throat relaxed.<br><b>2. Breath</b> — Take a slow deep breath before each line.<br><b>3. Pitch</b> — Start on a comfortable low note (Sa). Anudātta stays at this base.<br><b>4. Accent</b> — Raise your voice for Udātta (⬆️). Let Svarita (↘️) glide downward naturally.<br><b>5. Duration</b> — Count silently: Laghu = 1 mātrā, Guru = 2 mātrās. Keep the beat steady.<br><b>6. Repetition</b> — Classical Vedic tradition repeats each verse 3 times (triyāvarta).<br><b>7. Resonance</b> — Feel the vibration in your chest and skull. Vedic chanting creates healing resonance.</p></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# CHARTS
# ═══════════════════════════════════════════════════════════════

def draw_pitch_graph(syllables, highlight_idx=None):
    labels  = [s["text"] for s in syllables]
    pitches = [PITCH_LABELS.get(s["svara"], BASE_SA) for s in syllables]
    base_colors = {"udatta":"#6b1a00","svarita":"#a05020","anudatta":"#1a4a6b"}
    colors = []
    sizes  = []
    for i, s in enumerate(syllables):
        if highlight_idx is not None and i == highlight_idx:
            colors.append("#f0c040"); sizes.append(22)
        else:
            colors.append(base_colors.get(s["svara"],"#888")); sizes.append(13)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=labels, y=pitches, fill="tozeroy",
        fillcolor="rgba(160,70,20,0.15)",
        line=dict(color="rgba(0,0,0,0)", shape="spline", smoothing=1.3), showlegend=False))
    fig.add_trace(go.Scatter(x=labels, y=pitches, mode="lines+markers+text",
        text=[s["svara"] for s in syllables], textposition="top center",
        textfont=dict(size=9, color="#2a0e00"),
        line=dict(color="#7a3010", width=3, shape="spline", smoothing=1.3),
        marker=dict(size=sizes, color=colors, line=dict(width=2, color="#fde8b0")),
        showlegend=False))
    tick_vals = [BASE_SA, BASE_SA*(4/3), BASE_SA*(3/2)]
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,225,150,0.2)",
        font=dict(color="#2a0e00"),
        xaxis=dict(title="Syllable", gridcolor="rgba(120,50,10,0.2)", color="#2a0e00"),
        yaxis=dict(title="Shruti Pitch (Hz)", gridcolor="rgba(120,50,10,0.2)", color="#2a0e00",
                   tickvals=tick_vals, ticktext=["Sa — Anudātta","Ma — Svarita","Pa — Udātta"]),
        margin=dict(t=30,b=30), height=300, showlegend=False)
    return fig

def draw_gana_chart(ganas):
    from collections import Counter
    count  = Counter(ganas)
    values = [count.get(g,0) for g in ALL_GANAS]
    colors = ["rgba(140,50,10,0.75)" if v>0 else "rgba(180,100,50,0.25)" for v in values]
    fig = go.Figure(go.Bar(x=ALL_GANAS, y=values, marker_color=colors,
        marker_line=dict(color="#7a3010", width=1.5),
        text=values, textposition="outside", textfont=dict(color="#2a0e00")))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,225,150,0.2)",
        font=dict(color="#2a0e00"),
        xaxis=dict(title="Gaṇa", gridcolor="rgba(120,50,10,0.15)", color="#2a0e00",
                   categoryorder="array", categoryarray=ALL_GANAS),
        yaxis=dict(title="Count", gridcolor="rgba(120,50,10,0.15)", color="#2a0e00"),
        margin=dict(t=30,b=30), height=280, showlegend=False)
    return fig

def draw_syllable_chart(syllables):
    texts  = [s["text"] for s in syllables]
    types  = [s["type"] for s in syllables]
    svaras = [s["svara"] for s in syllables]
    y_vals = [1 if t=="guru" else -1 for t in types]
    colors = ["#6b1a00" if t=="guru" else "#1a4a6b" for t in types]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=texts, y=y_vals, marker_color=colors,
        marker_line=dict(color="#fde8b0", width=1),
        text=[f"{'G' if t=='guru' else 'L'}<br>{sv[:3]}" for t,sv in zip(types,svaras)],
        textposition="outside", textfont=dict(color="#fde8b0", size=9), showlegend=False))
    fig.add_hline(y=0, line_color="rgba(120,50,10,0.5)", line_width=1.5)
    fig.add_annotation(x=0, y=1.15, xref="paper", yref="paper",
        text="🟫 Guru (Long) — above   |   🟦 Laghu (Short) — below",
        showarrow=False, font=dict(size=11, color="#2a0e00"), align="left")
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,225,150,0.2)",
        font=dict(color="#2a0e00"),
        xaxis=dict(title="Syllable", gridcolor="rgba(120,50,10,0.15)", color="#2a0e00"),
        yaxis=dict(gridcolor="rgba(120,50,10,0.15)", color="#2a0e00",
                   tickvals=[1,-1], ticktext=["Guru","Laghu"], range=[-1.8,1.8]),
        margin=dict(t=50,b=30), height=300, showlegend=False)
    return fig

# ═══════════════════════════════════════════════════════════════
# UI
# ═══════════════════════════════════════════════════════════════

st.markdown("""<div class='mandala-border'>
❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧
</div>""", unsafe_allow_html=True)

st.markdown("""
<div style='text-align:center;padding:1.5rem 0 1rem;'>
    <div style='font-size:2rem;color:rgba(70,20,0,0.45);letter-spacing:10px;'>🪷 ✦ 🕉️ ✦ 🪷</div>
    <h1>ShrutiLaya</h1>
    <p class='subtitle'>श्रुतिलय — Ancient Sanskrit Vedic Chanting</p>
    <div style='font-size:1.1rem;color:rgba(70,20,0,0.4);letter-spacing:8px;margin-top:0.5rem;'>❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧</div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Full-width input
verse = st.text_area(
    "✍️ Enter Sanskrit Verse (Devanagari):",
    value="ॐ भूर्भुवः स्वः \nतत्सवितुर्वरेण्यं \nभर्गो देवस्य धीमहि \nधियो यो नः प्रचोदयात्  ",
    height=110
)

# ── Mode selector — styled buttons centered below input ────────
if "mode" not in st.session_state:
    st.session_state.mode = "🎶 Chanting Mode"

st.markdown("<div style='text-align:center;margin:0.5rem 0 0.3rem;'><span style='font-family:Cinzel,serif;font-size:0.9rem;color:#2a0e00;font-weight:600;letter-spacing:1px;'>🎛️ SELECT MODE</span></div>", unsafe_allow_html=True)

# Render styled mode buttons
m1, m2, m3, m4, m5 = st.columns([1.5, 2, 0.5, 2, 1.5])
with m2:
    chant_cls = "mode-btn-active" if st.session_state.mode == "🎶 Chanting Mode" else "mode-btn-inactive"
    if st.button("🎶  Chanting Mode", key="btn_chant"):
        st.session_state.mode = "🎶 Chanting Mode"
        st.rerun()
with m4:
    learn_cls = "mode-btn-active" if st.session_state.mode == "📚 Learning Mode" else "mode-btn-inactive"
    if st.button("📚  Learning Mode", key="btn_learn"):
        st.session_state.mode = "📚 Learning Mode"
        st.rerun()

mode = st.session_state.mode

st.markdown("<div class='om-divider'>· · · 🪷 · · ·</div>", unsafe_allow_html=True)

# ── Generate button — perfectly centered ───────────────────────
btn_label = "🕉️  Generate Vedic Chanting" if mode == "🎶 Chanting Mode" else "📚  Reveal Verse Knowledge"
g1, g2, g3 = st.columns([1.2, 3.6, 1.2])
with g2:
    generate = st.button(btn_label)

if generate:
    with st.spinner("🔱 Analyzing the sacred verse..."):
        try:
            data       = analyze_verse(verse)
            syllables  = data["syllables"]
            lg_pattern = data.get("lg_pattern","")
            ganas      = data.get("ganas",[])
            meter      = data.get("meter","Unknown")
            n_guru     = sum(1 for s in syllables if s["type"]=="guru")
            n_laghu    = sum(1 for s in syllables if s["type"]=="laghu")
            udatta_c   = sum(1 for s in syllables if s["svara"]=="udatta")
            svarita_c  = sum(1 for s in syllables if s["svara"]=="svarita")
            anudatta_c = sum(1 for s in syllables if s["svara"]=="anudatta")

            st.markdown("---")
            st.markdown("### 📜 Verse Analysis")
            sc1,sc2,sc3,sc4 = st.columns(4)
            with sc1: st.markdown(f'<div class="stat-card"><div class="stat-num">{len(syllables)}</div><div class="stat-label">Total Syllables</div></div>', unsafe_allow_html=True)
            with sc2: st.markdown(f'<div class="stat-card"><div class="stat-num">{n_guru}</div><div class="stat-label">Guru — Long</div></div>', unsafe_allow_html=True)
            with sc3: st.markdown(f'<div class="stat-card"><div class="stat-num">{n_laghu}</div><div class="stat-label">Laghu — Short</div></div>', unsafe_allow_html=True)
            with sc4: st.markdown(f'<div class="stat-card"><div class="stat-num">{len(ganas)}</div><div class="stat-label">Gaṇas</div></div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f'<div class="meter-badge">📐 Detected Meter — {meter}</div>', unsafe_allow_html=True)
            if lg_pattern:
                st.markdown("**Laghu–Guru Pattern:**")
                st.markdown(f'<div class="pattern-box">{lg_pattern}</div>', unsafe_allow_html=True)
            if ganas:
                st.markdown("**Gaṇas (3-syllable units):**")
                st.markdown(f'<div class="gana-box">{" ".join(ganas)}</div>', unsafe_allow_html=True)

            st.markdown("<div class='om-divider'>· · · 🪷 · · ·</div>", unsafe_allow_html=True)

            if mode == "🎶 Chanting Mode":
                st.markdown("### 🔤 Syllable Distribution (Laghu vs Guru)")
                st.plotly_chart(draw_syllable_chart(syllables), use_container_width=True)
                st.markdown("<div class='om-divider'>· · · 🪷 · · ·</div>", unsafe_allow_html=True)

                st.markdown("### 🎤 Interactive Karaoke Chant")
                karaoke_ph = st.empty()
                for i in range(len(syllables)):
                    html = "<div style='display:flex;flex-wrap:wrap;gap:6px;padding:10px;justify-content:center;'>"
                    for j, s in enumerate(syllables):
                        svara_icons = {"udatta":"⬆️","anudatta":"⬇️","svarita":"↘️"}
                        if j == i:
                            box = "background:rgba(100,35,5,0.88);color:#fde8b0;box-shadow:0 0 16px rgba(200,100,30,0.7);border:2px solid rgba(255,200,100,0.8);"
                        elif s["type"] == "guru":
                            box = "background:rgba(100,35,5,0.3);color:#2a0e00;border:1px solid rgba(100,40,5,0.5);"
                        else:
                            box = "background:rgba(20,60,100,0.2);color:#2a0e00;border:1px solid rgba(20,60,100,0.4);"
                        html += f"""<div style='{box}border-radius:10px;padding:10px 8px;text-align:center;min-width:52px;'>
                            <div style='font-size:1.15rem;font-weight:bold;font-family:serif;'>{s['text']}</div>
                            <div style='font-size:0.6rem;margin-top:2px;'>{"🟫 G" if s["type"]=="guru" else "🟦 L"}</div>
                            <div style='font-size:0.6rem;'>{svara_icons.get(s["svara"],"")}</div>
                        </div>"""
                    html += "</div>"
                    karaoke_ph.markdown(html, unsafe_allow_html=True)
                    time.sleep(DURATION_MS.get(syllables[i]["type"],420) / 1000)

                st.markdown("---")
                st.markdown("### 🧠 Verse Insights")
                total = len(syllables)
                u_pct = round(udatta_c/total*100); a_pct = round(anudatta_c/total*100); s_pct = round(svarita_c/total*100)
                coverage = round((udatta_c+svarita_c+anudatta_c)/total*100)
                st.success(f"✨ Accent Coverage: {coverage}%  |  ⬆️ Udātta: {u_pct}%  |  ⬇️ Anudātta: {a_pct}%  |  ↘️ Svarita: {s_pct}%")
                if n_guru > n_laghu:
                    st.info("🐘 Guru-dominant verse — slow, majestic, powerful chanting pace.")
                else:
                    st.info("🪷 Laghu-dominant verse — light, swift, melodious chanting rhythm.")

                st.markdown("<div class='om-divider'>· · · 🪷 · · ·</div>", unsafe_allow_html=True)
                st.markdown("### 📊 Gaṇa Distribution (All 8 Gaṇas)")
                st.plotly_chart(draw_gana_chart(ganas), use_container_width=True)

                st.markdown("<div class='om-divider'>· · · 🪷 · · ·</div>", unsafe_allow_html=True)
                st.markdown("### 🎧 Sacred Shruti Chanting Audio")
                st.markdown("""<div class="shruti-badge">
                🎵 <b>Pure Shruti synthesis</b> — Rāga Bhairav tuning (Sa · Ma · Pa)<br>
                &nbsp;&nbsp;· 9-partial harmonic overtone stack · Gamaka meend glide · Vocal vibrato<br>
                &nbsp;&nbsp;· Tanpūrā drone underneath · Stone temple reverb · Warm low-pass filter
                </div>""", unsafe_allow_html=True)

                speed = st.slider("🎵 Karaoke Speed", 0.5, 2.0, 1.0)
                with st.spinner("🔔 Synthesizing shruti tones..."):
                    audio_buf = generate_shruti_audio(syllables)
                st.audio(audio_buf, format="audio/wav")

                colA, colB, colC = st.columns(3)
                with colA:
                    st.download_button("⬇️ Download .wav", audio_buf, "shrutilaya.wav", "audio/wav")
                with colB:
                    st.button("🔁 Regenerate")
                with colC:
                    st.button("📤 Share")

                st.markdown("<div class='om-divider'>· · · 🪷 · · ·</div>", unsafe_allow_html=True)
                st.markdown("### 📈 Live Shruti Pitch Contour")
                st.markdown('<div class="info-box">Watch the golden dot highlight each syllable as the verse plays!</div>', unsafe_allow_html=True)
                pitch_ph = st.empty()
                timings  = get_syllable_timings(syllables)
                pitch_ph.plotly_chart(draw_pitch_graph(syllables, highlight_idx=None), use_container_width=True)
                if st.button("▶️ Play Animated Pitch Graph"):
                    for i, timing in enumerate(timings):
                        dur = (timing["end"] - timing["start"]) / speed
                        pitch_ph.plotly_chart(draw_pitch_graph(syllables, highlight_idx=i), use_container_width=True)
                        time.sleep(dur)
                    pitch_ph.plotly_chart(draw_pitch_graph(syllables, highlight_idx=None), use_container_width=True)

            else:
                build_learning_panel(verse, syllables, lg_pattern, ganas, meter, data)
                st.markdown("<div class='om-divider'>· · · 🪷 · · ·</div>", unsafe_allow_html=True)
                st.markdown("### 📈 Shruti Pitch Contour")
                st.plotly_chart(draw_pitch_graph(syllables), use_container_width=True)
                st.markdown("### 🎧 Listen While You Learn")
                with st.spinner("🔔 Synthesizing shruti tones..."):
                    audio_buf = generate_shruti_audio(syllables)
                st.audio(audio_buf, format="audio/wav")
                st.download_button("⬇️ Download .wav", audio_buf, "shrutilaya_learn.wav", "audio/wav")

        except Exception as e:
            st.error(f"Something went wrong: {e}")
            import traceback
            st.code(traceback.format_exc())

st.markdown("""<div class='mandala-border' style='border-top:1.5px solid rgba(100,40,5,0.3);border-bottom:none;margin-top:2rem;'>
❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧
</div>""", unsafe_allow_html=True)