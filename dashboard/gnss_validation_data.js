var gnssValidationData = {
  "generated_at": "2026-11-16 09:15:30",
  "station": "POVA (Popay\u00e1n)",
  "station_info": {
    "name": "Popay\u00e1n",
    "lat": 2.378,
    "lon": -76.495,
    "height_m": 1730.0,
    "distance_to_samanga_km": 15.0,
    "distance_to_purace_km": 25.0,
    "operator": "IGAC GeoRED",
    "url_sopac": "http://geodesy.unr.edu/NGLStationPages/stations/POVA.sta"
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
    "insar_displacement_period_mm": 50.47,
    "bias_mm": 56.22,
    "rmse_mm": 56.22,
    "verdict": "fuera de tolerancia",
    "gnss_points_total": 514,
    "gnss_points_period": 33,
    "period": {
      "start": "2026-03-16",
      "end": "2026-11-06",
      "days": 235
    }
  },
  "gnss_series_summary": {
    "total_points": 514,
    "start_date": "2017-01-01",
    "end_date": "2026-11-01",
    "gnss_velocity_los_mm_per_year": 2.21
  },
  "interpretation": "Resultados InSAR presentan discrepancia significativa con GNSS IGAC (bias > 10 mm). Posibles causas: (1) solo 2 im\u00e1genes (par \u00fanico), (2) ausencia de correcci\u00f3n atmosf\u00e9rica ERA5, (3) unwrapping sin red de control robusta. Recomendado: Procesamiento InSAR Multitemporal con 30+ im\u00e1genes."
};\n