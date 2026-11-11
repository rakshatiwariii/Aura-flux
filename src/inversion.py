"""
AURA-Flux: Linear Integrated Mass Enhancement (LIME) Inversion Core Module
Applies dynamic boundary-layer effective wind parameterization and spatial mass integration.
"""

import numpy as np

class LIMEInversionEngine:
    def __init__(self, pixel_size_m: float = 60.0):
        self.pixel_size_m = pixel_size_m
        self.pixel_area_m2 = pixel_size_m ** 2
        # Molar masses: CH4 = 16.04 g/mol, Dry Air = 28.97 g/mol
        self.molar_ratio = 16.04 / 28.97

    def calculate_effective_wind(self, u10: float, v10: float) -> dict:
        """
        Calculates scalar 10m wind speed U10 and dynamic effective transport wind U_eff
        Ref: Varon et al. (2024) empirical boundary-layer parameterization: U_eff = 0.7 + 0.23 * U10
        """
        speed_10m = np.sqrt(u10**2 + v10**2)
        effective_wind = 0.7 + (0.23 * speed_10m)
        return {
            "U10_ms": round(float(speed_10m), 2),
            "U_eff_ms": round(float(effective_wind), 2)
        }

    def compute_mass_enhancement(self, plume_array_ppmm: np.ndarray, background_bg_ppmm: float) -> float:
        """
        Computes total Integrated Mass Enhancement (IME) in kilograms (kg).
        """
        enhancement_ppmm = np.maximum(plume_array_ppmm - background_bg_ppmm, 0.0)
        # Convert ppm*m to integrated column mass
        ime_kg = np.sum(enhancement_ppmm) * self.pixel_area_m2 * (self.molar_ratio / 1e6) * 1.19  # air density factor
        return float(ime_kg)

    def calculate_flux_rate(self, ime_kg: float, plume_length_m: float, u_eff_ms: float) -> dict:
        """
        Inverts IME and effective wind velocity into mass emission rate (Q in kg/hr).
        """
        if plume_length_m <= 0:
            return {"Q_kg_hr": 0.0, "uncertainty_kg_hr": 0.0}
        
        d_ime_dx = ime_kg / plume_length_m  # kg/m gradient
        q_kg_s = d_ime_dx * u_eff_ms
        q_kg_hr = q_kg_s * 3600.0
        
        # Quadratic error propagation (approx 15% model + wind variance)
        uncertainty = q_kg_hr * 0.15
        
        return {
            "Q_kg_hr": round(float(q_kg_hr), 1),
            "uncertainty_kg_hr": round(float(uncertainty), 1)
        }

    def compute_observability_index(self, q_kg_hr: float, u10_ms: float, bg_std_ppmm: float) -> dict:
        """
        Calculates dimensionless Point-Source Observability metric (Ops).
        Scenes with Ops < 0.04 fall below 50% statistical detection confidence threshold.
        """
        if u10_ms <= 0 or bg_std_ppmm <= 0:
            return {"Ops": 0.0, "confidence": "Low"}
            
        q_kg_s = q_kg_hr / 3600.0
        ops = q_kg_s / (self.pixel_size_m * u10_ms * (bg_std_ppmm * 1e-6))
        
        confidence = "High" if ops >= 0.08 else ("Moderate" if ops >= 0.04 else "Low (Below Detection Limit)")
        return {
            "Ops": round(float(ops), 4),
            "confidence": confidence
        }
