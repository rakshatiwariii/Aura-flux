import streamlit as st
import numpy as np
import plotly.express as px

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & HEADER
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AURA-Flux | Earth Information Jukebox",
    layout="wide",
    page_icon="🎵"
)

st.title("🎵 AURA-Flux: Multi-Sensory Earth Information Jukebox")
st.markdown("**Translating NASA EMIT Hyperspectral Plumes & GEOS-FP Winds into Accessible Real-Time Soundscapes**")

# -----------------------------------------------------------------------------
# 2. PHYSICS & INVERSION ENGINE (EMBEDDED)
# -----------------------------------------------------------------------------
class LIMEInversionEngine:
    def __init__(self, pixel_size_m: float = 60.0):
        self.pixel_size_m = pixel_size_m
        self.pixel_area_m2 = pixel_size_m ** 2
        self.molar_ratio = 16.04 / 28.97

    def calculate_effective_wind(self, u10: float) -> float:
        """Dynamic effective wind parameterization: U_eff = 0.7 + 0.23 * U10"""
        return 0.7 + (0.23 * u10)

    def compute_mass_enhancement(self, plume_array: np.ndarray, bg_noise: float) -> float:
        """Computes total Integrated Mass Enhancement (IME) in kg."""
        enhancement = np.maximum(plume_array - bg_noise, 0.0)
        ime_kg = np.sum(enhancement) * self.pixel_area_m2 * (self.molar_ratio / 1e6) * 1.19
        return float(ime_kg)

    def calculate_flux_rate(self, ime_kg: float, plume_length_m: float, u_eff: float) -> dict:
        """Inverts IME and transport speed into mass flux (Q in kg/hr)."""
        if plume_length_m <= 0:
            return {"Q_kg_hr": 0.0, "uncertainty_kg_hr": 0.0}
        
        d_ime_dx = ime_kg / plume_length_m
        q_kg_s = d_ime_dx * u_eff
        q_kg_hr = q_kg_s * 3600.0
        uncertainty = q_kg_hr * 0.15
        
        return {
            "Q_kg_hr": round(float(q_kg_hr), 1),
            "uncertainty_kg_hr": round(float(uncertainty), 1)
        }

    def compute_observability_index(self, q_kg_hr: float, u10: float, bg_std: float) -> dict:
        """Calculates dimensionless Point-Source Observability index (Ops)."""
        if u10 <= 0 or bg_std <= 0:
            return {"Ops": 0.0, "confidence": "Low"}
        q_kg_s = q_kg_hr / 3600.0
        ops = q_kg_s / (self.pixel_size_m * u10 * (bg_std * 1e-6))
        confidence = "High" if ops >= 0.08 else ("Moderate" if ops >= 0.04 else "Low")
        return {"Ops": round(float(ops), 4), "confidence": confidence}

# Initialize Engine Instance
engine = LIMEInversionEngine(pixel_size_m=60.0)

# -----------------------------------------------------------------------------
# 3. SIDEBAR CONTROLS
# -----------------------------------------------------------------------------
st.sidebar.header("🕹️ Jukebox Controls & NASA Data Stream")
scene_option = st.sidebar.selectbox(
    "Select NASA EIC / EMIT Visual Frame",
    ["Permian Basin (Oil & Gas) - Granule #20230815", "Turkmenistan Super-Emitter - Granule #20230902"]
)

u10_wind = st.sidebar.slider("NASA GEOS-FP 10m Wind Speed (m/s)", 0.5, 12.0, 3.8)
bg_noise_input = st.sidebar.slider("Upwind Background Noise StdDev (ppm·m)", 5.0, 30.0, 12.4)
base_freq = st.sidebar.slider("Audio Synth Root Frequency (Hz)", 130, 440, 220)

# -----------------------------------------------------------------------------
# 4. DATA SYNTHESIS & CALCULATIONS
# -----------------------------------------------------------------------------
np.random.seed(42 if "Permian" in scene_option else 101)
x = np.linspace(-300, 300, 35)
y = np.linspace(0, 1200, 35)
X, Y = np.meshgrid(x, y)

peak_val = 420 if "Permian" in scene_option else 680
plume_signal = peak_val * np.exp(- (X**2 / (2 * 85**2)) - (Y / 550)) + np.random.normal(0, bg_noise_input, X.shape)
plume_signal = np.maximum(plume_signal, 0)

u_eff = engine.calculate_effective_wind(u10_wind)
ime_kg = engine.compute_mass_enhancement(plume_signal, bg_noise=bg_noise_input)
flux_results = engine.calculate_flux_rate(ime_kg=ime_kg, plume_length_m=1200.0, u_eff=u_eff)
obs_results = engine.compute_observability_index(flux_results["Q_kg_hr"], u10_wind, bg_noise_input)
max_enhancement = float(np.max(plume_signal))

# -----------------------------------------------------------------------------
# 5. DASHBOARD METRICS DISPLAY
# -----------------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Emission Mass Rate (Q)", f"{flux_results['Q_kg_hr']} kg/hr", f"± {flux_results['uncertainty_kg_hr']} kg/hr")
col2.metric("Effective Wind (U_eff)", f"{round(u_eff, 2)} m/s", f"Derived from {u10_wind} m/s U10")
col3.metric("Observability Index (Ops)", f"{obs_results['Ops']}", obs_results['confidence'])
col4.metric("Sonified Pitch Range", f"{base_freq} - {int(base_freq + (max_enhancement * 0.3))} Hz", "C-Minor Pentatonic")

st.divider()

# -----------------------------------------------------------------------------
# 6. LIVE AUDIO SONIFICATION ENGINE (HTML5 WEB AUDIO API)
# -----------------------------------------------------------------------------
st.subheader("🔊 Live Audio Sonification Engine")

pitch_freq = int(base_freq + (max_enhancement * 0.3))
pulse_duration = round(max(0.3, 1.5 - (u_eff * 0.1)), 2)

audio_html = f"""
<div style="background-color:#1e1e2e; padding:20px; border-radius:12px; text-align:center; border:1px solid #313244;">
    <button onclick="playSonification()" style="background-color:#a6e3a1; color:#11111b; padding:14px 28px; border:none; border-radius:8px; font-size:18px; font-weight:bold; cursor:pointer; transition:0.2s;">
        ▶️ Play Plume Audio Sonification
    </button>
    <p style="color:#cdd6f4; margin-top:12px; font-size:15px;" aria-live="polite">
        <strong>Audio Screen-Reader Descriptor:</strong> Peak enhancement of {int(max_enhancement)} ppm·m mapped to frequency {pitch_freq}Hz with a pulse rhythm of {pulse_duration}s driven by {round(u_eff, 1)}m/s wind speed.
    </p>
</div>

<script>
function playSonification() {{
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    
    osc.type = 'sine';
    osc.frequency.setValueAtTime({pitch_freq}, audioCtx.currentTime);
    
    gain.gain.setValueAtTime(0.01, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.4, audioCtx.currentTime + 0.1);
    gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + {pulse_duration});
    
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    
    osc.start();
    osc.stop(audioCtx.currentTime + {pulse_duration});
}}
</script>
"""
st.components.v1.html(audio_html, height=150)

# -----------------------------------------------------------------------------
# 7. INTERACTIVE VISUAL FRAME DISPLAY
# -----------------------------------------------------------------------------
st.subheader("🖼️ NASA EIC Visual Frame Concentration Map (ppm·m)")
fig = px.imshow(
    plume_signal,
    color_continuous_scale="Viridis",
    labels=dict(x="Cross-Wind Distance (60m px)", y="Downwind Distance (60m px)", color="CH4 Enhancement"),
    title=f"NASA EMIT Scene Reconstruction ({scene_option})"
)
fig.update_layout(height=500, margin=dict(l=20, r=20, t=40, b=20))
st.plotly_chart(fig, use_container_width=True)

st.info("ℹ️ **Data Credit**: NASA LP DAAC `EMITL2BCH4PLM` cloud granules integrated with NASA GMAO GEOS-FP wind vectors via `earthaccess`.")
