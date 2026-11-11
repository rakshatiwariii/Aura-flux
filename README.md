# Aura-flux
# 🎵 AURA-Flux: Multi-Sensory Earth Information Jukebox

> **NASA Space Apps Challenge 2026** — *The Earth Information Jukebox*  
> **Team**: Aura-flux  
> **Challenge**: Transforming NASA EMIT hyperspectral methane frames and GEOS-FP wind data into accessible real-time soundscapes and verified mass emission rates.

---

## 🛰️ Overview
AURA-Flux is an open-source, physics-informed geospatial engine and multi-sensory sonification app. It bridges spaceborne remote sensing and accessible climate science by converting NASA Earth Information Center (EIC) visual plume frames into live audio synthesizer frequencies and screen-reader accessible descriptors, making high-stakes atmospheric data perceptible through sound for blind and low-vision users.

## 🚀 Key Features
* **Direct NASA Integration**: Programmatically streams Cloud-Optimized GeoTIFFs (`EMITL2BCH4PLM`) via `earthaccess` and couples them with NASA GEOS-FP wind reanalysis.
* **Physics Inversion Engine**: Implements the Linear Integrated Mass Enhancement (LIME) model and dynamic effective wind parameterization ($U_{\text{eff}} = 0.7 + 0.23 U_{10}$) to calculate mass flux ($Q$ in $\text{kg/hr}$) with uncertainty bounds.
* **Live Audio Sonification**: Translates pixel concentration densities into real-time harmonic synth frequencies using the HTML5 Web Audio API.
* **Accessibility-First Design**: Includes aria-live audio descriptors and high-contrast multi-sensory UI layouts.

## 🛠️ Tech Stack
* **Language**: Python 3.10+
* **Framework**: Streamlit
* **Geospatial & Math**: NumPy, SciPy, Plotly
* **NASA APIs**: CMR API, ESDIS Cloud Storage (AWS S3)

## 📄 License
Distributed under the **Apache License 2.0**. See `LICENSE` for more information.
