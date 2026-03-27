import streamlit as st
import numpy as np
import io
import wave
import time
import os
import plotly.graph_objects as go
from scipy.signal import resample
from analyzer import analyze_verse

st.set_page_config(page_title="ShrutiLaya", page_icon="🕉️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Crimson+Text:ital,wght@0,400;0,600;1,400&display=swap');

    html, body,
    [data-testid="stAppViewContainer"],
    [data-testid="stApp"] {
        background: linear-gradient(160deg, #f5b942 0%, #e8922a 35%, #d4701a 65%, #c8601a 100%) !important;
    }
    [data-testid="stHeader"] {
        background: rgba(160, 70, 10, 0.92) !important;
        width: 100% !important;
    }
    .main .block-container {
        background: transparent !important;
        padding: 1rem 2rem 2rem 2rem;
        max-width: 1100px;
        margin: 0 auto;
    }

    /* Mandala pattern in background */
    [data-testid="stAppViewContainer"]::before {
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background-image:
            radial-gradient(circle at 10% 20%, rgba(120,50,5,0.12) 0%, transparent 50%),
            radial-gradient(circle at 90% 80%, rgba(120,50,5,0.12) 0%, transparent 50%),
            radial-gradient(circle at 50% 50%, rgba(120,50,5,0.08) 0%, transparent 60%),
            radial-gradient(circle at 10% 80%, rgba(120,50,5,0.10) 0%, transparent 40%),
            radial-gradient(circle at 90% 20%, rgba(120,50,5,0.10) 0%, transparent 40%);
        pointer-events: none;
        z-index: 0;
    }

    /* Mandala border top */
    .mandala-border {
        width: 100%;
        text-align: center;
        color: rgba(80, 25, 0, 0.45);
        font-size: 1.3rem;
        letter-spacing: 6px;
        padding: 6px 0;
        border-bottom: 1.5px solid rgba(100, 40, 5, 0.3);
        margin-bottom: 1rem;
        overflow: hidden;
        white-space: nowrap;
    }

    /* Typography */
    h1 {
        font-family: 'Cinzel', serif !important;
        color: #2a0e00 !important;
        text-align: center;
        font-size: 3rem !important;
        font-weight: 700 !important;
        text-shadow: 1px 1px 0px rgba(255,220,150,0.4);
        letter-spacing: 6px;
    }
    h2, h3 {
        font-family: 'Cinzel', serif !important;
        color: #2a0e00 !important;
    }
    p, label, div {
        color: #2a0e00 !important;
    }
    .stMarkdown p { color: #2a0e00 !important; }
    .subtitle {
        text-align: center;
        color: #3a1200 !important;
        font-family: 'Crimson Text', serif;
        font-size: 1.3rem;
        font-style: italic;
        letter-spacing: 3px;
    }
    .om-divider {
        text-align: center;
        color: rgba(70, 20, 0, 0.5);
        font-size: 1.1rem;
        letter-spacing: 8px;
        margin: 0.8rem 0;
    }

    /* Stat cards */
    .stat-card {
        background: rgba(255, 230, 160, 0.45);
        border: 1.5px solid rgba(120, 50, 10, 0.5);
        border-radius: 12px;
        padding: 14px 10px;
        text-align: center;
        box-shadow: 3px 4px 10px rgba(100, 30, 0, 0.25);
    }
    .stat-num {
        font-size: 1.8rem;
        font-weight: bold;
        color: #2a0e00 !important;
        font-family: 'Cinzel', serif;
    }
    .stat-label {
        font-size: 0.8rem;
        color: #4a1a00 !important;
        margin-top: 4px;
        font-family: 'Crimson Text', serif;
    }

    /* Meter badge */
    .meter-badge {
        background: rgba(100, 35, 5, 0.75);
        border: 1.5px solid rgba(255, 200, 100, 0.6);
        border-radius: 20px;
        padding: 8px 24px;
        color: #fde8b0 !important;
        font-family: 'Cinzel', serif;
        font-size: 1rem;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 1rem;
        box-shadow: 3px 4px 12px rgba(80, 20, 0, 0.4);
    }

    /* Pattern and gana boxes */
    .pattern-box {
        background: rgba(255, 230, 160, 0.35);
        border: 1px solid rgba(100, 40, 5, 0.5);
        border-radius: 10px;
        padding: 10px 16px;
        color: #2a0e00 !important;
        font-size: 1.2rem;
        letter-spacing: 4px;
        font-family: monospace;
        display: inline-block;
        box-shadow: inset 0 1px 4px rgba(0,0,0,0.1);
    }
    .gana-box {
        background: rgba(255, 230, 160, 0.35);
        border: 1px solid rgba(150, 80, 20, 0.5);
        border-radius: 10px;
        padding: 8px 16px;
        color: #2a0e00 !important;
        font-size: 1.1rem;
        letter-spacing: 6px;
        font-family: monospace;
        display: inline-block;
    }

    /* Info box */
    .info-box {
        background: rgba(255, 230, 160, 0.3);
        border-left: 3px solid rgba(120, 50, 10, 0.7);
        border-radius: 0 8px 8px 0;
        padding: 0.8rem 1rem;
        margin: 0.5rem 0;
        color: #2a0e00 !important;
        font-family: 'Crimson Text', serif;
        font-size: 1rem;
        line-height: 1.7;
        font-style: italic;
    }

    /* Syllable cards in karaoke */
    .syl {
        padding: 10px;
        margin: 4px;
        border-radius: 8px;
        text-align: center;
        display: inline-block;
        transition: 0.3s;
        background: rgba(255, 225, 150, 0.4);
        border: 1px solid rgba(120, 50, 10, 0.4);
        min-width: 55px;
        box-shadow: 2px 3px 7px rgba(100,30,0,0.2);
    }

    /* BUTTONS — popup 3D effect */
    .stButton > button {
        background: linear-gradient(145deg, #b04a08, #d06820, #b04a08) !important;
        color: #fde8b0 !important;
        font-family: 'Cinzel', serif !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        border: 2px solid rgba(255, 200, 100, 0.65) !important;
        border-radius: 12px !important;
        padding: 0.65rem 1.5rem !important;
        width: 100% !important;
        letter-spacing: 2px !important;
        box-shadow: 3px 5px 14px rgba(70,20,0,0.5), inset 0 1px 2px rgba(255,220,150,0.25) !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.5) !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background: linear-gradient(145deg, #d06820, #e07830, #d06820) !important;
        box-shadow: 4px 7px 18px rgba(70,20,0,0.6), inset 0 1px 3px rgba(255,220,150,0.3) !important;
        transform: translateY(-2px) !important;
        border-color: rgba(255, 220, 120, 0.9) !important;
    }
    .stButton > button:active {
        transform: translateY(1px) !important;
        box-shadow: 1px 2px 6px rgba(70,20,0,0.4) !important;
    }
    .stDownloadButton > button {
        background: linear-gradient(145deg, #7a2e08, #a04818) !important;
        color: #fde8b0 !important;
        border: 2px solid rgba(255, 200, 100, 0.6) !important;
        border-radius: 10px !important;
        box-shadow: 3px 4px 10px rgba(60,15,0,0.45) !important;
        font-family: 'Cinzel', serif !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.4) !important;
    }
    .stDownloadButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 4px 6px 14px rgba(60,15,0,0.55) !important;
    }

    /* Inputs */
    .stTextArea textarea {
        background: rgba(255, 235, 175, 0.5) !important;
        color: #1a0800 !important;
        border: 1.5px solid rgba(120, 50, 10, 0.5) !important;
        font-size: 1.3rem !important;
        font-family: 'Crimson Text', serif !important;
        border-radius: 10px !important;
        box-shadow: inset 1px 2px 6px rgba(100,30,0,0.12) !important;
    }
    .stSelectbox > div > div {
        background: rgba(255, 235, 175, 0.45) !important;
        color: #1a0800 !important;
        border: 1.5px solid rgba(120, 50, 10, 0.5) !important;
        border-radius: 8px !important;
        box-shadow: 1px 2px 6px rgba(100,30,0,0.15) !important;
    }
    .stSlider > div > div > div { background: rgba(180,80,20,0.5) !important; }
    .stSlider > div > div > div > div { background: #b04a08 !important; }

    /* Alerts */
    [data-testid="stAlert"] {
        background: rgba(255, 235, 175, 0.4) !important;
        border: 1px solid rgba(120, 60, 10, 0.4) !important;
        color: #1a0800 !important;
        border-radius: 10px !important;
    }

    /* HR */
    hr { border-color: rgba(100, 40, 5, 0.3) !important; }

    /* Audio player */
    audio { filter: sepia(0.3) !important; }
</style>
""", unsafe_allow_html=True)

# ── Audio settings ─────────────────────────────────────────────
DURATION = { "laghu": 300, "guru": 600 }
PITCH    = { "udatta": 293, "anudatta": 196, "svarita": 246 }

ALL_GANAS = ["ma", "na", "bha", "ja", "sa", "ra", "ya", "ta"]

# ── Helper: load wav ──────────────────────────────────────────
def load_wav_float(filepath, sample_rate=44100):
    with wave.open(filepath, 'r') as f:
        frames    = f.readframes(f.getnframes())
        channels  = f.getnchannels()
        orig_rate = f.getframerate()
        sampwidth = f.getsampwidth()
    if sampwidth == 2:
        data = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
    elif sampwidth == 4:
        data = np.frombuffer(frames, dtype=np.int32).astype(np.float32) / 2147483648.0
    else:
        data = np.frombuffer(frames, dtype=np.uint8).astype(np.float32) / 128.0 - 1.0
    if channels == 2:
        data = (data[0::2] + data[1::2]) / 2.0
    if orig_rate != sample_rate:
        num_samples = int(len(data) * sample_rate / orig_rate)
        data = resample(data, num_samples)
    if np.max(np.abs(data)) > 0:
        data = data / np.max(np.abs(data))
    return data

def loop_audio(audio, target_len):
    if len(audio) == 0:
        return np.zeros(target_len)
    reps = (target_len // len(audio)) + 2
    return np.tile(audio, reps)[:target_len]

def detect_bpm(audio, sample_rate=44100):
    try:
        import librosa
        tempo, _ = librosa.beat.beat_track(y=audio.astype(np.float32), sr=sample_rate)
        return float(tempo) if float(tempo) > 0 else 80.0
    except:
        return 80.0

def stretch_to_bpm(audio, orig_bpm, target_bpm, sample_rate=44100):
    try:
        import librosa
        if orig_bpm <= 0 or target_bpm <= 0:
            return audio
        rate = orig_bpm / target_bpm
        rate = np.clip(rate, 0.5, 2.0)
        return librosa.effects.time_stretch(audio.astype(np.float32), rate=rate)
    except:
        return audio

def get_chant_bpm(syllables):
    total_ms = sum(DURATION.get(s["type"], 300) for s in syllables)
    return (len(syllables) / (total_ms / 1000)) * 60

# ── Tone generation ───────────────────────────────────────────
def make_rich_tone(duration_ms, pitch_hz, sample_rate=44100):
    n   = int(sample_rate * duration_ms / 1000)
    t   = np.linspace(0, duration_ms / 1000, n)
    w   = (1.0  * np.sin(2 * np.pi * pitch_hz * t)
         + 0.4  * np.sin(2 * np.pi * pitch_hz * 2 * t)
         + 0.15 * np.sin(2 * np.pi * pitch_hz * 3 * t)
         + 0.05 * np.sin(2 * np.pi * pitch_hz * 4 * t))
    w  /= np.max(np.abs(w))
    att = int(sample_rate * 0.08)
    dec = int(sample_rate * 0.20)
    sus = max(0, n - att - dec)
    if sus == 0:
        att, dec = n // 2, n - n // 2
    env = np.concatenate([np.linspace(0, 1, att), np.ones(sus), np.linspace(1, 0, dec)])
    w  *= env[:n]
    w  *= (1 + 0.008 * np.sin(2 * np.pi * 5.5 * t))
    rd  = int(sample_rate * 0.10)
    rv  = np.zeros(n + rd * 3)
    rv[:n]          += w
    rv[rd:rd+n]     += w * 0.35
    rv[rd*2:rd*2+n] += w * 0.15
    rv[rd*3:rd*3+n] += w * 0.07
    if np.max(np.abs(rv)) > 0:
        rv /= np.max(np.abs(rv))
    return rv

# ── Syllable-synced instrument layers ─────────────────────────
def make_syllable_layer(sample, syllables, sample_rate, volume_map):
    result = []
    for syl in syllables:
        dur_ms  = DURATION.get(syl["type"], 300)
        dur_smp = int(sample_rate * dur_ms / 1000)
        vol     = volume_map(syl)
        if len(sample) == 0:
            result.append(np.zeros(dur_smp))
            continue
        chunk = np.tile(sample, (dur_smp // len(sample)) + 2)[:dur_smp]
        result.append(chunk * vol)
    return np.concatenate(result)

# ── Main audio generation ─────────────────────────────────────
def generate_audio(syllables, sample_rate=44100):
    chant_bpm = get_chant_bpm(syllables)

    # 1 — chant voice
    chant_parts = []
    for syl in syllables:
        tone = make_rich_tone(DURATION.get(syl["type"], 300), PITCH.get(syl["svara"], 246), sample_rate)
        gap  = np.zeros(int(sample_rate * (0.06 if syl["type"] == "guru" else 0.04)))
        chant_parts.append(np.concatenate([tone, gap]))
    chant     = np.concatenate(chant_parts)
    total_len = len(chant)

    # helper to safely load + sync
    def load_synced(fname):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), fname)
        if not os.path.exists(path):
            st.warning(f"⚠️ {fname} not found in project folder!")
            return np.zeros(1)
        raw  = load_wav_float(path, sample_rate)
        bpm  = detect_bpm(raw, sample_rate)
        return stretch_to_bpm(raw, bpm, chant_bpm, sample_rate)

    # 2 — tanpura (continuous drone)
    try:
        tanpura = load_synced("tanpura.wav")
        tanpura_layer = loop_audio(tanpura, total_len) * 0.22
    except Exception as e:
        t = np.linspace(0, total_len / sample_rate, total_len)
        tanpura_layer = (0.08 * np.sin(2 * np.pi * 130 * t)
                       + 0.04 * np.sin(2 * np.pi * 260 * t)
                       + 0.02 * np.sin(2 * np.pi * 390 * t))

    # 3 — tabla (synced per syllable — guru = strong hit, laghu = soft hit)
    try:
        tabla = load_synced("tabla.wav")
        tabla_layer = make_syllable_layer(
            tabla, syllables, sample_rate,
            lambda s: 0.85 if s["type"] == "guru" else 0.45
        ) * 0.30
        tabla_layer = loop_audio(tabla_layer, total_len)
    except:
        tabla_layer = np.zeros(total_len)

    # 4 — flute (plays on udatta = high pitch syllables)
    try:
        flute = load_synced("flute.wav")
        flute_layer = make_syllable_layer(
            flute, syllables, sample_rate,
            lambda s: 0.5 if s["svara"] == "udatta" else (0.2 if s["svara"] == "svarita" else 0.05)
        ) * 0.25
        flute_layer = loop_audio(flute_layer, total_len)
    except:
        flute_layer = np.zeros(total_len)

    # 5 — harmonics (subtle ambient texture)
    try:
        harmonics = load_synced("harmonics.wav")
        harmonics_layer = loop_audio(harmonics, total_len) * 0.12
    except:
        harmonics_layer = np.zeros(total_len)

    # 6 — master mix with proper blending
    mix = (chant * 0.70
         + tanpura_layer
         + tabla_layer
         + flute_layer
         + harmonics_layer)

    # normalize + soft clip
    peak = np.max(np.abs(mix))
    if peak > 0:
        mix = mix / peak * 0.75
    mix = np.tanh(mix * 1.2) / 1.2

    out = np.int16(mix * 32767)
    buf = io.BytesIO()
    with wave.open(buf, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(out.tobytes())
    buf.seek(0)
    return buf

# ── Pitch graph (smooth spline + filled area) ─────────────────
def draw_pitch_graph(syllables):
    labels  = [s["text"] for s in syllables]
    pitches = [PITCH.get(s["svara"], 220) for s in syllables]
    colors  = ["#6b1a00" if s["svara"]=="udatta" else "#c87040" if s["svara"]=="anudatta" else "#a05020" for s in syllables]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=labels, y=pitches, fill="tozeroy",
        fillcolor="rgba(160,70,20,0.15)",
        line=dict(color="rgba(0,0,0,0)", shape="spline", smoothing=1.3),
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=labels, y=pitches,
        mode="lines+markers+text",
        text=[s["svara"] for s in syllables],
        textposition="top center",
        textfont=dict(size=9, color="#2a0e00"),
        line=dict(color="#7a3010", width=3, shape="spline", smoothing=1.3),
        marker=dict(size=13, color=colors, line=dict(width=2, color="#fde8b0")),
        showlegend=False
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,225,150,0.2)",
        font=dict(color="#2a0e00"),
        xaxis=dict(title="Syllable", gridcolor="rgba(120,50,10,0.2)", color="#2a0e00",
                   showline=True, linecolor="rgba(120,50,10,0.4)"),
        yaxis=dict(title="Pitch (Hz)", gridcolor="rgba(120,50,10,0.2)", color="#2a0e00",
                   tickvals=[196, 246, 293],
                   ticktext=["Low — Anudātta","Mid — Svarita","High — Udātta"],
                   showline=True, linecolor="rgba(120,50,10,0.4)"),
        margin=dict(t=30, b=30), height=300, showlegend=False
    )
    return fig

# ── Gana distribution chart (all 8 ganas) ────────────────────
def draw_gana_chart(ganas):
    from collections import Counter
    count  = Counter(ganas)
    # always show all 8 ganas even if count is 0
    values = [count.get(g, 0) for g in ALL_GANAS]
    colors = [
        "rgba(140,50,10,0.75)" if v > 0 else "rgba(180,100,50,0.25)"
        for v in values
    ]
    fig = go.Figure(go.Bar(
        x=ALL_GANAS, y=values,
        marker_color=colors,
        marker_line=dict(color="#7a3010", width=1.5),
        text=values, textposition="outside",
        textfont=dict(color="#2a0e00")
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,225,150,0.2)",
        font=dict(color="#2a0e00"),
        xaxis=dict(title="Gaṇa", gridcolor="rgba(120,50,10,0.15)", color="#2a0e00",
                   categoryorder="array", categoryarray=ALL_GANAS),
        yaxis=dict(title="Count", gridcolor="rgba(120,50,10,0.15)", color="#2a0e00"),
        margin=dict(t=30, b=30), height=280, showlegend=False
    )
    return fig

# ── Syllable distribution chart (laghu vs guru with arrows) ───
def draw_syllable_chart(syllables):
    texts   = [s["text"] for s in syllables]
    types   = [s["type"] for s in syllables]
    svaras  = [s["svara"] for s in syllables]
    y_vals  = [1 if t == "guru" else -1 for t in types]
    colors  = ["#6b1a00" if t == "guru" else "#1a4a6b" for t in types]

    fig = go.Figure()

    # bars
    fig.add_trace(go.Bar(
        x=texts, y=y_vals,
        marker_color=colors,
        marker_line=dict(color="#fde8b0", width=1),
        text=[f"{'G' if t=='guru' else 'L'}<br>{sv[:3]}" for t, sv in zip(types, svaras)],
        textposition="outside",
        textfont=dict(color="#fde8b0", size=9),
        showlegend=False
    ))

    # zero line
    fig.add_hline(y=0, line_color="rgba(120,50,10,0.5)", line_width=1.5)

    # legend annotation
    fig.add_annotation(x=0, y=1.15, xref="paper", yref="paper",
        text="🟫 Guru (Long) — above   |   🟦 Laghu (Short) — below",
        showarrow=False, font=dict(size=11, color="#2a0e00"),
        align="left")

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,225,150,0.2)",
        font=dict(color="#2a0e00"),
        xaxis=dict(title="Syllable", gridcolor="rgba(120,50,10,0.15)", color="#2a0e00",
                   showline=True, linecolor="rgba(120,50,10,0.4)"),
        yaxis=dict(title="", gridcolor="rgba(120,50,10,0.15)", color="#2a0e00",
                   tickvals=[1, -1], ticktext=["Guru", "Laghu"],
                   range=[-1.8, 1.8]),
        margin=dict(t=50, b=30), height=300, showlegend=False
    )
    return fig

# ═══════════════════════════════════════════════════════════════
# ── UI ─────────────────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════

# Full-width mandala border
st.markdown("""
<div class='mandala-border'>
❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧
</div>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style='text-align:center;padding:1.5rem 0 1rem;'>
    <div style='font-size:2rem;color:rgba(70,20,0,0.45);letter-spacing:10px;'>🪷 ✦ 🕉️ ✦ 🪷</div>
    <h1>ShrutiLaya</h1>
    <p class='subtitle'>श्रुतिलय — Ancient Sanskrit Vedic Chanting</p>
    <div style='font-size:1.1rem;color:rgba(70,20,0,0.4);letter-spacing:8px;margin-top:0.5rem;'>
        ❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Input row
col1, col2 = st.columns([2, 1])
with col1:
    verse = st.text_area(
        "✍️ Enter Sanskrit Verse (Devanagari):",
        value="धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः",
        height=130
    )
with col2:
    speed = st.slider("🎵 Chant Speed", 0.5, 2.0, 1.0)
    mode  = st.selectbox("📖 Mode", ["Beginner", "Pro"])
    st.markdown('<div class="info-box">Chanda (meter) is automatically detected by AI using Vedic prosody rules.</div>',
                unsafe_allow_html=True)

st.markdown("<div class='om-divider'>· · · 🪷 · · ·</div>", unsafe_allow_html=True)

if st.button("🕉️  Generate Vedic Chanting Experience"):
    with st.spinner("🔱 AI is analyzing the sacred verse..."):
        try:
            data       = analyze_verse(verse)
            syllables  = data["syllables"]
            lg_pattern = data.get("lg_pattern", "")
            ganas      = data.get("ganas", [])
            n_guru     = sum(1 for s in syllables if s["type"] == "guru")
            n_laghu    = sum(1 for s in syllables if s["type"] == "laghu")
            udatta_c   = sum(1 for s in syllables if s["svara"] == "udatta")
            svarita_c  = sum(1 for s in syllables if s["svara"] == "svarita")
            anudatta_c = sum(1 for s in syllables if s["svara"] == "anudatta")

            st.markdown("---")

            # ── Stats ──────────────────────────────────────────
            st.markdown("### 📜 Verse Analysis")
            sc1, sc2, sc3, sc4 = st.columns(4)
            with sc1:
                st.markdown(f'<div class="stat-card"><div class="stat-num">{len(syllables)}</div><div class="stat-label">Total Syllables</div></div>', unsafe_allow_html=True)
            with sc2:
                st.markdown(f'<div class="stat-card"><div class="stat-num">{n_guru}</div><div class="stat-label">Guru — Long</div></div>', unsafe_allow_html=True)
            with sc3:
                st.markdown(f'<div class="stat-card"><div class="stat-num">{n_laghu}</div><div class="stat-label">Laghu — Short</div></div>', unsafe_allow_html=True)
            with sc4:
                st.markdown(f'<div class="stat-card"><div class="stat-num">{len(ganas)}</div><div class="stat-label">Gaṇas</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f'<div class="meter-badge">📐 Detected Meter — {data["meter"]}</div>', unsafe_allow_html=True)

            if lg_pattern:
                st.markdown("**Laghu–Guru Pattern:**")
                st.markdown(f'<div class="pattern-box">{lg_pattern}</div>', unsafe_allow_html=True)
            if ganas:
                st.markdown("**Gaṇas (3-syllable units):**")
                st.markdown(f'<div class="gana-box">{" ".join(ganas)}</div>', unsafe_allow_html=True)

            st.markdown("<div class='om-divider'>· · · 🪷 · · ·</div>", unsafe_allow_html=True)

            # ── Syllable distribution chart ────────────────────
            st.markdown("### 🔤 Syllable Distribution (Laghu vs Guru)")
            st.plotly_chart(draw_syllable_chart(syllables), use_container_width=True)

            st.markdown("<div class='om-divider'>· · · 🪷 · · ·</div>", unsafe_allow_html=True)

            # ── Karaoke ────────────────────────────────────────
            st.markdown("### 🎤 Interactive Karaoke Chant")
            placeholder = st.empty()
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
                    html += f"""<div style='{box}border-radius:10px;padding:10px 8px;text-align:center;min-width:52px;transition:0.3s;'>
                        <div style='font-size:1.15rem;font-weight:bold;font-family:serif;'>{s['text']}</div>
                        <div style='font-size:0.6rem;margin-top:2px;'>{"🟫 G" if s["type"]=="guru" else "🟦 L"}</div>
                        <div style='font-size:0.6rem;'>{svara_icons.get(s["svara"],"")}</div>
                    </div>"""
                html += "</div>"
                placeholder.markdown(html, unsafe_allow_html=True)
                time.sleep(DURATION.get(syllables[i]["type"], 300) / 1000 / speed)

            st.markdown("---")

            # ── AI insights ────────────────────────────────────
            st.markdown("### 🧠 AI Verse Insights")
            total = len(syllables)
            u_pct = round(udatta_c  / total * 100)
            a_pct = round(anudatta_c/ total * 100)
            s_pct = round(svarita_c / total * 100)
            coverage = round((udatta_c + svarita_c + anudatta_c) / total * 100)
            st.success(f"✨ Melodic Accent Coverage: {coverage}%  |  ⬆️ Udātta: {u_pct}%  |  ⬇️ Anudātta: {a_pct}%  |  ↘️ Svarita: {s_pct}%")
            if n_guru > n_laghu:
                st.info("🐘 Guru-dominant verse — slow, majestic, powerful chanting pace.")
            else:
                st.info("🪷 Laghu-dominant verse — light, swift, melodious chanting rhythm.")

            st.markdown("<div class='om-divider'>· · · 🪷 · · ·</div>", unsafe_allow_html=True)

            # ── Pitch graph ────────────────────────────────────
            st.markdown("### 📈 Melodic Pitch Contour")
            st.plotly_chart(draw_pitch_graph(syllables), use_container_width=True)

            # ── Gana chart ─────────────────────────────────────
            st.markdown("### 📊 Gaṇa Distribution (All 8 Gaṇas)")
            st.plotly_chart(draw_gana_chart(ganas), use_container_width=True)

            st.markdown("<div class='om-divider'>· · · 🪷 · · ·</div>", unsafe_allow_html=True)

            # ── Audio ──────────────────────────────────────────
            st.markdown("### 🎧 Sacred Chanting Audio")
            with st.spinner("🎵 Blending tanpura, tabla, flute, harmonics with chant..."):
                audio_buf = generate_audio(syllables)
            st.audio(audio_buf, format="audio/wav")

            colA, colB, colC = st.columns(3)
            with colA:
                st.download_button("⬇️ Download .wav", audio_buf, "shrutilaya.wav", "audio/wav")
            with colB:
                st.button("🔁 Regenerate")
            with colC:
                st.button("📤 Share")

        except Exception as e:
            st.error(f"Something went wrong: {e}")
            import traceback
            st.code(traceback.format_exc())

# Bottom mandala border
st.markdown("""
<div class='mandala-border' style='border-top:1.5px solid rgba(100,40,5,0.3);border-bottom:none;margin-top:2rem;'>
❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧ ✦ ❋ ✦ ❧
</div>
""", unsafe_allow_html=True)