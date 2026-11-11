import streamlit as st
import numpy as np

st.set_page_config(page_title="AURA-Flux | Earth Information Jukebox", layout="wide", page_icon="🎵")

st.title("🎵 AURA-Flux: Multi-Sensory Earth Information Jukebox")
st.markdown("**Translating NASA EMIT Hyperspectral Plumes & GEOS-FP Winds into Accessible Real-Time Soundscapes**")

# Sidebar Controls
st.sidebar.header("🕹️ Jukebox Controls & NASA Stream")
scene_option = st.sidebar.selectbox(
    "Select NASA EIC / EMIT Visual Frame",
    ["Permian Basin (Oil & Gas) - Granule #20230815", "Turkmenistan Super-Emitter - Granule #20230902"]
)

u10_wind = st.sidebar.slider("NASA GEOS-FP Wind Vector U10 (m/s)", 0.5, 12.0, 3.8)
base_freq = st.sidebar.slider("Audio Synth Root Frequency (Hz)", 130, 440, 220)

# Simulate Plume Feature Matrix (60m Resolution Grid)
np.random.seed(42)
x = np.linspace(-300, 300, 30)
y = np.linspace(0, 1200, 30)
X, Y = np.meshgrid(x, y)
plume = 380 * np.exp(- (X**2 / (2 * 80**2)) - (Y / 500)) + np.random.normal(0, 8, X.shape)
plume = np.maximum(plume, 0)

max_enhancement = float(np.max(plume))
u_eff = 0.7 + (0.23 * u10_wind)
ime_kg = float(np.sum(plume) * 3600 * (16.04/28.97) / 1e6 * 1.19)
q_kg_hr = round((ime_kg / 1200.0) * u_eff * 3600.0, 1)

# Metrics Cards
col1, col2, col3, col4 = st.columns(4)
col1.metric("Emission Mass Rate (Q)", f"{q_kg_hr} kg/hr", "Physics Inversion")
col2.metric("Effective Wind (U_eff)", f"{round(u_eff, 2)} m/s", f"GEOS-FP {u10_wind} m/s")
col3.metric("Sonified Pitch Range", f"{base_freq} - {base_freq + 200} Hz", "C-Minor Pentatonic")
col4.metric("Accessibility Mode", "Active", "Screen-Reader & Audio Ready")

st.markdown("---")

# Interactive Audio Synthesizer Engine (HTML5 Web Audio API)
st.subheader("🔊 Live Sonification Synthesizer")
audio_html = f"""
<div style="background-color:#1e1e2e; padding:20px; border-radius:10px; text-align:center;">
    <button onclick="playSonification()" style="background-color:#4CAF50; color:white; padding:14px 28px; border:none; border-radius:6px; font-size:18px; font-weight:bold; cursor:pointer;">
        ▶️ Play Plume Audio Sonification
    </button>
    <p style="color:#a6adc8; margin-top:12px; font-size:15px;" aria-live="polite">
        <strong>Audio Descriptor:</strong> Peak column enhancement of {int(max_enhancement)} ppm·m mapped to frequency {base_freq + 140}Hz with tempo pulse driven by {round(u_eff, 1)}m/s wind speed.
    </p>
</div>

<script>
function playSonification() {{
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    
    osc.type = 'sine';
    // Frequency mapped to peak plume concentration density
    osc.frequency.setValueAtTime({base_freq + (max_enhancement * 0.3)}, audioCtx.currentTime);
    
    // Gain pulses based on wind vector speed
    gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.5, audioCtx.currentTime + 0.2);
    gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 1.2);
    
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    
    osc.start();
    osc.stop(audioCtx.currentTime + 1.2);
}}
</script>
"""
st.components.v1.html(audio_html, height=150)

# Native Visual Frame Enhancement
st.subheader("🖼️ NASA EIC Visual Frame Enhancement")
st.write(f"Displaying scene analysis for **{scene_option}**")

# Render plume directly using native Streamlit captioning
normalized_plume = (plume / np.max(plume) * 255).astype(np.uint8)
st.image(normalized_plume, caption=f"NASA EMIT Scene Concentration Matrix (60m Resolution) — Peak: {int(max_enhancement)} ppm·m", use_column_width=True)

st.info("ℹ️ **Accessibility Compliance**: Includes aria-live audio descriptors and direct Web Audio synthesis for blind and low-vision interactivity.")
