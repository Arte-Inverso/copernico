var gnssValidationDataV3 = {
  "generated_at": "2026-11-16 09:54:39",
  "version": "v3_pixel_specific",
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
  "metrics": {
    "gnss_velocity_los_mm_per_year": 2.21,
    "gnss_displacement_period_mm": -5.75,
    "insar_displacement_period_mm": -49.13,
    "insar_pixel_coherence": 0.315,
    "insar_pixel_distance_km": 0.01,
    "bias_mm": -43.38,
    "rmse_mm": 43.38,
    "verdict": "fuera de tolerancia",
    "coherence_warning": "✓ Coherencia del píxel POVA aceptable (γ=0.315).",
    "comparison_method": "píxel-a-píxel (no zona-promedio)",
    "gnss_points_period": 33,
    "period": {
      "start": "2026-03-16",
      "end": "2026-11-06",
      "days": 235
    }
  },
  "interpretation": "COMPARACIÓN PÍXEL-A-PÍXEL (no zona-promedio): bias -43.38 mm, coherencia γ=0.315, distancia píxel-POVA 0.01 km.\n✗ Discrepancia SIGNIFICATIVA (bias > 10 mm). Causas probables: (1) par único sin ERA5, (2) atmósfera andina. Recomendado Procesamiento InSAR Multitemporal.",
  "gnss_series_summary": {
    "total_points": 514,
    "start_date": "2017-01-01",
    "end_date": "2026-11-01"
  }
};
