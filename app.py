import streamlit as st
import numpy as np
import io
import wave
import time
import plotly.graph_objects as go
from analyzer import analyze_verse

st.set_page_config(page_title="Vedic Chanting Pro", page_icon="🕉️", layout="wide")

st.markdown("""
<style>
    .main { background-color: #0f0f1a; }
    .block-container { padding: 2rem 3rem; }
    body { background: linear-gradient(135deg,#0f0f1a,#1a1a2e); }
    .glass {
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 20px;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    }
    .syl {
        padding: 10px;
        margin: 4px;
        border-radius: 10px;
        text-align: center;
        display: inline-block;
        transition: 0.3s;
        background: #1a1a2e;
        border: 1px solid #3a3a5e;
        min-width: 50px;
    }
    .syl:hover { transform: scale(1.1); background: #2a2a4a; }
    .active { background: #f0c060 !important; color: black !important; font-weight: bold; }
    .syl-text { font-size: 1.1rem; font-weight: bold; color: #f0c060; }
    .syl-type-laghu { color: #60d080; font-size: 0.7rem; }
    .syl-type-guru { color: #a060f0; font-size: 0.7rem; }
    .syl-svara { font-size: 0.65rem; color: #8080b0; }
    .meter-badge {
        background: #2a1a4a;
        border: 1px solid #6a3a9a;
        border-radius: 20px;
        padding: 6px 20px;
        color: #c080f0;
        font-size: 1rem;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 1rem;
    }
    .pattern-box {
        background: #1a1a2e;
        border: 1px solid #3a5a3a;
        border-radius: 10px;
        padding: 10px 16px;
        color: #80e080;
        font-size: 1.2rem;
        letter-spacing: 4px;
        font-family: monospace;
        display: inline-block;
        margin-bottom: 0.5rem;
    }
    .gana-box {
        background: #1a1a2e;
        border: 1px solid #5a3a5a;
        border-radius: 10px;
        padding: 8px 16px;
        color: #d080d0;
        font-size: 1.1rem;
        letter-spacing: 6px;
        font-family: monospace;
        display: inline-block;
    }
    .stButton > button {
        background: linear-gradient(135deg, #c89040, #f0c060);
        color: #0f0f1a;
        font-weight: bold;
        font-size: 1.1rem;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 2rem;
        width: 100%;
    }
    .stTextArea textarea {
        background: #1a1a2e;
        color: #f0e0b0;
        border: 1px solid #3a3a5e;
        font-size: 1.1rem;
    }
    .info-box {
        background: #1a1a2e;
        border-left: 4px solid #f0c060;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin: 1rem 0;
        color: #c0c0e0;
        font-size: 0.9rem;
        line-height: 1.7;
    }
    .stat-card {
        background: #1a1a2e;
        border: 1px solid #3a3a5e;
        border-radius: 10px;
        padding: 14px 10px;
        text-align: center;
    }
    .stat-num { font-size: 1.8rem; font-weight: bold; color: #f0c060; }
    .stat-label { font-size: 0.8rem; color: #8080b0; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

# ── Audio settings ─────────────────────────────────────────────
DURATION = { "laghu": 300, "guru": 600 }
PITCH    = { "udatta": 280, "anudatta": 180, "svarita": 230 }

CHANDA_INFO = {
    "Auto detect": "Let the analyzer automatically detect the meter from your verse using Sanskrit prosody rules.",
    "Anushtubh":   "8 syllables per pada, 4 padas. Most common meter — used in Bhagavad Gita and Ramayana.",
    "Gayatri":     "8 syllables per pada, 3 padas. One of the oldest and most sacred Vedic meters.",
    "Trishtubh":   "11 syllables per pada, 4 padas. Used in Rigveda for heroic and powerful passages.",
    "Jagati":      "12 syllables per pada, 4 padas. Extended and flowing meter used in later Sanskrit texts.",
}

# ── Rich harmonium-like tone ──────────────────────────────────
def make_rich_tone(duration_ms, pitch_hz, sample_rate=44100):
    t = np.linspace(0, duration_ms / 1000, int(sample_rate * duration_ms / 1000))
    wave_arr  =  1.0  * np.sin(2 * np.pi * pitch_hz * t)
    wave_arr +=  0.6  * np.sin(2 * np.pi * pitch_hz * 2 * t)
    wave_arr +=  0.3  * np.sin(2 * np.pi * pitch_hz * 3 * t)
    wave_arr +=  0.15 * np.sin(2 * np.pi * pitch_hz * 4 * t)
    wave_arr +=  0.08 * np.sin(2 * np.pi * pitch_hz * 5 * t)
    wave_arr = wave_arr / np.max(np.abs(wave_arr))
    attack  = int(sample_rate * 0.06)
    decay   = int(sample_rate * 0.15)
    sustain = len(t) - attack - decay
    if sustain < 0:
        sustain = 0
        attack  = len(t) // 2
        decay   = len(t) - attack
    envelope = np.concatenate([
        np.linspace(0, 1, attack),
        np.ones(sustain),
        np.linspace(1, 0, decay)
    ])
    envelope = envelope[:len(wave_arr)]
    wave_arr = wave_arr * envelope
    vibrato_rate  = 5.5
    vibrato_depth = 0.012
    vibrato = 1 + vibrato_depth * np.sin(2 * np.pi * vibrato_rate * t[:len(wave_arr)])
    wave_arr = wave_arr * vibrato
    reverb_delay = int(sample_rate * 0.08)
    reverb = np.zeros(len(wave_arr) + reverb_delay * 3)
    reverb[:len(wave_arr)]                              += wave_arr * 1.0
    reverb[reverb_delay:reverb_delay+len(wave_arr)]     += wave_arr * 0.3
    reverb[reverb_delay*2:reverb_delay*2+len(wave_arr)] += wave_arr * 0.1
    reverb[reverb_delay*3:reverb_delay*3+len(wave_arr)] += wave_arr * 0.04
    if np.max(np.abs(reverb)) > 0:
        reverb = reverb / np.max(np.abs(reverb))
    return reverb

def generate_audio(syllables, sample_rate=44100):
    parts = []
    drone_freq = 130.8
    for syl in syllables:
        dur = DURATION.get(syl["type"], 300)
        pit = PITCH.get(syl["svara"], 220)
        tone = make_rich_tone(dur, pit, sample_rate)
        drone_dur = len(tone)
        t_drone = np.linspace(0, drone_dur / sample_rate, drone_dur)
        drone = 0.08 * np.sin(2 * np.pi * drone_freq * t_drone)
        drone += 0.04 * np.sin(2 * np.pi * drone_freq * 2 * t_drone)
        if len(drone) < len(tone):
            drone = np.pad(drone, (0, len(tone) - len(drone)))
        else:
            drone = drone[:len(tone)]
        mixed = tone + drone
        if np.max(np.abs(mixed)) > 0:
            mixed = mixed / np.max(np.abs(mixed)) * 0.85
        parts.append(mixed)
        gap_dur = 0.04 if syl["type"] == "laghu" else 0.07
        parts.append(np.zeros(int(sample_rate * gap_dur)))
    combined = np.concatenate(parts)
    combined = np.int16(combined * 32767 * 0.75)
    buf = io.BytesIO()
    with wave.open(buf, 'w') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        w.writeframes(combined.tobytes())
    buf.seek(0)
    return buf

# ── Pitch graph ───────────────────────────────────────────────
def draw_pitch_graph(syllables):
    labels  = [s["text"] for s in syllables]
    pitches = [PITCH.get(s["svara"], 220) for s in syllables]
    colors  = []
    for s in syllables:
        if s["svara"] == "udatta":     colors.append("#f0c060")
        elif s["svara"] == "anudatta": colors.append("#60a0f0")
        else:                          colors.append("#c060f0")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=labels, y=pitches,
        mode="lines+markers+text",
        text=[s["svara"] for s in syllables],
        textposition="top center",
        textfont=dict(size=10, color="white"),
        line=dict(color="#f0c060", width=2.5),
        marker=dict(size=14, color=colors, line=dict(width=1.5, color="white"))
    ))
    fig.update_layout(
        paper_bgcolor="#0f0f1a", plot_bgcolor="#1a1a2e",
        font=dict(color="white"),
        xaxis=dict(title="Syllable", gridcolor="#2a2a4a", color="white"),
        yaxis=dict(title="Pitch (Hz)", gridcolor="#2a2a4a", color="white",
                   tickvals=[180, 230, 280],
                   ticktext=["Low (Anudātta)", "Mid (Svarita)", "High (Udātta)"]),
        margin=dict(t=30, b=30), height=320, showlegend=False
    )
    return fig

def draw_gana_chart(ganas):
    from collections import Counter
    count = Counter(ganas)
    labels = list(count.keys())
    values = list(count.values())
    fig = go.Figure(go.Bar(
        x=labels, y=values,
        marker_color="#c080f0",
        text=values, textposition="outside",
        textfont=dict(color="white")
    ))
    fig.update_layout(
        paper_bgcolor="#0f0f1a", plot_bgcolor="#1a1a2e",
        font=dict(color="white"),
        xaxis=dict(title="Gaṇa", gridcolor="#2a2a4a", color="white"),
        yaxis=dict(title="Count", gridcolor="#2a2a4a", color="white"),
        margin=dict(t=20, b=30), height=250, showlegend=False
    )
    return fig

# ── Header ────────────────────────────────────────────────────
st.markdown("<h1 style='text-align:center;color:#f0c060;'>🕉️ Vedic Chanting Pro</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#aaa;font-size:1.1rem;'>AI + Sanskrit + Music 🔥</p>", unsafe_allow_html=True)
st.markdown("---")

# ── Input Section ─────────────────────────────────────────────
col1, col2 = st.columns([2, 1])

with col1:
    verse = st.text_area(
        "Enter Sanskrit Verse (Devanagari):",
        value="धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः",
        height=120
    )

with col2:
    chanda_choice = st.selectbox("Select Chanda (meter):", list(CHANDA_INFO.keys()))
    speed = st.slider("Chant Speed", 0.5, 2.0, 1.0)
    mode  = st.selectbox("Mode", ["Beginner", "Pro"])
    st.markdown(f'<div class="info-box">{CHANDA_INFO[chanda_choice]}</div>', unsafe_allow_html=True)

# ── Generate Button ───────────────────────────────────────────
if st.button("✨ Generate Vedic Chanting Experience"):
    with st.spinner("AI is analyzing the Sanskrit verse..."):
        try:
            data = analyze_verse(verse)

            if chanda_choice != "Auto detect":
                data["meter"] = chanda_choice

            syllables  = data["syllables"]
            lg_pattern = data.get("lg_pattern", "")
            ganas      = data.get("ganas", [])

            st.markdown("---")

            # ── Stats ──────────────────────────────────────────
            st.markdown("### 📊 Stats")
            n_guru  = sum(1 for s in syllables if s["type"] == "guru")
            n_laghu = sum(1 for s in syllables if s["type"] == "laghu")

            sc1, sc2, sc3, sc4 = st.columns(4)
            with sc1:
                st.markdown(f'<div class="stat-card"><div class="stat-num">{len(syllables)}</div><div class="stat-label">Total Syllables</div></div>', unsafe_allow_html=True)
            with sc2:
                st.markdown(f'<div class="stat-card"><div class="stat-num" style="color:#a060f0">{n_guru}</div><div class="stat-label">Guru (Long)</div></div>', unsafe_allow_html=True)
            with sc3:
                st.markdown(f'<div class="stat-card"><div class="stat-num" style="color:#60d080">{n_laghu}</div><div class="stat-label">Laghu (Short)</div></div>', unsafe_allow_html=True)
            with sc4:
                st.markdown(f'<div class="stat-card"><div class="stat-num" style="color:#c080f0">{len(ganas)}</div><div class="stat-label">Gaṇas</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f'<div class="meter-badge">📐 Detected Meter: {data["meter"]}</div>', unsafe_allow_html=True)

            # ── LG Pattern & Ganas ─────────────────────────────
            if lg_pattern:
                st.markdown("**Laghu–Guru Pattern:**")
                st.markdown(f'<div class="pattern-box">{lg_pattern}</div>', unsafe_allow_html=True)
            if ganas:
                st.markdown("**Gaṇas (3-syllable units):**")
                st.markdown(f'<div class="gana-box">{" ".join(ganas)}</div>', unsafe_allow_html=True)

            st.markdown("---")

            # ── Karaoke Animation ──────────────────────────────
            st.markdown("### 🎤 Interactive Karaoke Chant")
            placeholder = st.empty()

            for i in range(len(syllables)):
                html = "<div style='display:flex;flex-wrap:wrap;gap:6px;'>"
                for j, s in enumerate(syllables):
                    svara_icons = {"udatta": "⬆️", "anudatta": "⬇️", "svarita": "↘️"}
                    active_style = "background:#f0c060;color:black;" if j == i else "background:#1a1a2e;color:#f0c060;"
                    html += f"""
                    <div class='syl' style='{active_style}border:1px solid #3a3a5e;border-radius:10px;padding:10px;text-align:center;min-width:50px;'>
                        <div style='font-size:1.1rem;font-weight:bold;'>{s['text']}</div>
                        <div style='font-size:0.65rem;color:{"black" if j==i else "#60d080" if s["type"]=="laghu" else "#a060f0"};'>{"🟢" if s["type"]=="laghu" else "🟣"} {s["type"]}</div>
                        <div style='font-size:0.6rem;color:{"black" if j==i else "#8080b0"};'>{svara_icons.get(s["svara"],"")}</div>
                    </div>"""
                html += "</div>"
                placeholder.markdown(html, unsafe_allow_html=True)
                time.sleep(DURATION.get(syllables[i]["type"], 300) / 1000 / speed)

            st.markdown("---")

            # ── AI Feedback ────────────────────────────────────
            st.markdown("### 🧠 AI Analysis Feedback")
            udatta_count   = sum(1 for s in syllables if s["svara"] == "udatta")
            anudatta_count = sum(1 for s in syllables if s["svara"] == "anudatta")
            svarita_count  = sum(1 for s in syllables if s["svara"] == "svarita")
            accuracy = round((udatta_count + svarita_count) / len(syllables) * 100)
            st.success(f"Melodic Accent Coverage: {accuracy}% 🔥")
            if n_guru > n_laghu:
                st.info("This verse is heavy with Guru syllables — expect a slow, majestic chanting pace.")
            else:
                st.info("This verse has more Laghu syllables — expect a lighter, faster chanting rhythm.")

            st.markdown("---")

            # ── Pitch Graph ────────────────────────────────────
            st.markdown("### 📈 Melodic Pitch Contour")
            st.plotly_chart(draw_pitch_graph(syllables), use_container_width=True)

            if ganas:
                st.markdown("### 📊 Gaṇa Distribution")
                st.plotly_chart(draw_gana_chart(ganas), use_container_width=True)

            st.markdown("---")

            # ── Audio Controls ─────────────────────────────────
            st.markdown("### 🎧 Generated Chanting Audio")
            audio_buf = generate_audio(syllables)
            st.audio(audio_buf, format="audio/wav")

            colA, colB, colC = st.columns(3)
            with colA:
                st.download_button("⬇️ Download .wav", audio_buf, "sanskrit_chanting.wav", "audio/wav")
            with colB:
                st.button("🔁 Regenerate")
            with colC:
                st.button("📤 Share")

        except Exception as e:
            st.error(f"Something went wrong: {e}")
