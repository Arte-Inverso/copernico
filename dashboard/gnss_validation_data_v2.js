var gnssValidationDataV2 = {
  "generated_at": "2026-11-16 09:34:57",
  "version": "v2",
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
    "insar_displacement_period_mm": 4.58,
    "insar_std_mm": 24.21,
    "bias_mm": 10.33,
    "rmse_mm": 10.33,
    "verdict": "fuera de tolerancia",
    "pova_in_processed_zone": false,
    "methodological_warning": "⚠ ADVERTENCIA METODOLÓGICA: POVA está FUERA de la zona procesada (samanga). La comparación es ESPACIALMENTE INVÁLIDA: InSAR mide deformación en zona volcánica activa, GNSS mide movimiento tectónico en zona estable. El bias no representa error de medición sino diferencia de señal física.",
    "gnss_points_total": 514,
    "gnss_points_period": 33,
    "zone_compared": "samanga",
    "period": {
      "start": "2026-03-16",
      "end": "2026-11-06",
      "days": 235
    }
  },
  "interpretation": "⚠ COMPARACIÓN METODOLÓGICAMENTE INVÁLIDA: la estación POVA está fuera de la zona procesada (samanga). El bias de 10.33 mm NO representa error de medición InSAR, sino la DIFERENCIA entre: (a) deformación volcánica en zona activa (InSAR) y (b) movimiento tectónico estable (GNSS POVA). Para validación válida: (1) procesar zona que incluya POVA, o (2) usar estación GNSS dentro de zona procesada.",
  "gnss_series_summary": {
    "total_points": 514,
    "start_date": "2017-01-01",
    "end_date": "2026-11-01"
  }
};
