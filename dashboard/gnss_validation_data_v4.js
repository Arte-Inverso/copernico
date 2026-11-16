var gnssValidationDataV4 = {
  "generated_at": "2026-11-16 10:06:30",
  "version": "v4_honesto",
  "station": "POVA (Popayán)",
  "station_coords": {
    "lat": 2.378,
    "lon": -76.495
  },
  "sentinel1_params": {
    "wavelength_mm": 55.465763,
    "incidence_angle_deg": 36.9,
    "heading_deg": 192.5,
    "track": 142,
    "polarization": "VV"
  },
  "validation_status": "PENDIENTE",
  "reason": "Datos GNSS de POVA no disponibles públicamente. NGL (Nevada Geodetic Lab) no procesa estaciones IGAC GeoRED. Se requiere solicitud formal al IGAC para acceso a datos oficiales.",
  "insar_pixel_at_pova": {
    "disp_mm": -49.13,
    "coherence": 0.315,
    "distance_km": 0.01,
    "pixel_coords": {
      "lat": 2.3781,
      "lon": -76.4949
    },
    "pixel_idx": {
      "row": 287,
      "col": 416
    }
  },
  "what_is_validated": {
    "píxel_colocalization": "✓ VALIDADO (distancia 0.01 km)",
    "insar_disp_mm": "✓ InSAR real: -49.13 mm",
    "coherence": "✓ γ = 0.315",
    "gnss_real": "❌ PENDIENTE - requiere oficio al IGAC",
    "bias_calculation": "❌ PENDIENTE - no se puede calcular sin GNSS real",
    "verdict": "⚠ NO DETERMINABLE hasta validar con GNSS real"
  },
  "next_steps": [
    "1. Enviar oficio formal al IGAC solicitando datos POVA 2017-2026",
    "2. Considerar estaciones SIRGAS alternativas cercanas",
    "3. Integrar TomoSAR cloud del Dr. Dinh Ho Tong Minh (que incluye ERA5)",
    "4. NO reportar bias en propuesta Minciencias hasta tener GNSS real"
  ],
  "methodological_note": "La validación cuantitativa InSAR-GNSS requiere datos GNSS reales de la estación POVA. Esta estación es operada por el IGAC (Instituto Geográfico Agustín Codazzi) dentro de la red GeoRED, cuyos datos no están disponibles en repositorios públicos internacionales (NGL, UNAVCO). Se requiere solicitud formal al IGAC. Mientras tanto, se reporta honestamente el estado PENDIENTE de la validación."
};
