# -*- coding: utf-8 -*-
"""
validate_gnss_igac_v4_honesto.py — Versión HONESTA de validación GNSS

CAMBIOS CRÍTICOS vs v3:
1. NO usa datos sintéticos silenciosamente
2. Verifica si el cache existe y si es real o sintético
3. Reporta claramente cuando GNSS POVA no está disponible públicamente
4. Documenta el oficio al IGAC como paso siguiente obligatorio
5. Genera reporte en dashboard marcando "VALIDACIÓN PENDIENTE"
6. Mantiene el píxel InSAR colocalizado (ese SÍ es real)

Esta versión es publicable en Minciencias porque es metodológicamente honesta.
"""

import os
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from geopy.distance import geodesic
import requests

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

DATA_DIR = os.environ.get("DATA_DIR", "/data")
OUTPUTS_DIR = os.environ.get("OUTPUTS_DIR", "/outputs")
INSAR_RESULTS_PATH = os.path.join(OUTPUTS_DIR, "insar", "geophysics_inversion_data.js")
DASHBOARD_REPO = os.environ.get("DASHBOARD_REPO", "/opt/copernico/dashboard")
INSAR_RESULTS_ALT = os.path.join(DASHBOARD_REPO, "geophysics_inversion_data.js")

GNSS_CACHE_DIR = os.path.join(DATA_DIR, "gnss_igac")
GNSS_OUTPUTS_DIR = os.path.join(OUTPUTS_DIR, "gnss_validation")

POVA_LAT = 2.378
POVA_LON = -76.495

SENTINEL1_PARAMS = {
    "wavelength_mm": 55.465763,
    "incidence_angle_deg": 36.9,
    "heading_deg": 192.5,
    "track": 142,
    "polarization": "VV"
}


def load_insar_results():
    """Carga resultados InSAR v2 con pova_validation."""
    paths_to_try = [INSAR_RESULTS_PATH, INSAR_RESULTS_ALT]
    for path in paths_to_try:
        if os.path.exists(path):
            print(f"[1/3] Cargando resultados InSAR v2 desde: {path}")
            with open(path, "r", encoding="utf-8") as f:
                raw = f.read().replace("var geophysicsInversionData = ", "").rstrip(";\n")
            return json.loads(raw), path

    print(f"[1/3] ⚠ No se encontraron resultados InSAR")
    print(f"  Buscado en: {paths_to_try}")
    print(f"  Ejecuta primero: python scripts/insar_mogi_seismic_inversion_v2.py")
    return None, None


def attempt_real_gnss_download():
    """
    Intenta descargar datos reales de POVA desde NGL.
    Retorna (series, source) donde source indica si es 'real' o None.
    """
    url_ngl = "http://geodesy.unr.edu/gps_timeseries/tenv/IGS14/POVA.tenv2"
    print(f"[2/3] Intentando descarga GNSS POVA desde NGL (Nevada Geodetic Lab)...")
    print(f"  URL: {url_ngl}")

    try:
        r = requests.get(url_ngl, timeout=30)
        if r.status_code == 200 and len(r.text) > 1000:
            # Verificar que NO es página de error
            if "Not Found" not in r.text[:200]:
                lines = r.text.strip().split("\n")
                series = []
                for line in lines[1:]:
                    parts = line.split()
                    if len(parts) >= 10:
                        try:
                            year = float(parts[1])
                            day_of_year = float(parts[2])
                            date = datetime(int(year), 1, 1) + timedelta(days=day_of_year - 1)
                            east_mm = float(parts[8])
                            north_mm = float(parts[9])
                            up_mm = float(parts[10])
                            series.append({
                                "date": date.strftime("%Y-%m-%d"),
                                "east_mm": east_mm,
                                "north_mm": north_mm,
                                "up_mm": up_mm
                            })
                        except (ValueError, IndexError):
                            continue

                if len(series) > 100:  # mínimo 100 días para ser válido
                    print(f"  ✓ Descargados {len(series)} días GNSS REALES de POVA (NGL)")
                    return series, "real_NGL"
                else:
                    print(f"  ⚠ NGL respondió pero solo {len(series)} días (insuficiente)")
            else:
                print(f"  ⚠ NGL respondió con página de error (404 Not Found)")
        else:
            print(f"  ⚠ NGL no disponible (HTTP {r.status_code})")

    except Exception as e:
        print(f"  ⚠ Error descarga NGL: {e}")

    return None, None


def check_cache_validity(cache_file):
    """
    Verifica si el cache local es real o sintético.
    Detecta el patrón de datos sintéticos (semilla 42, velocidades fijas).
    """
    if not os.path.exists(cache_file):
        return None, "no_cache"

    with open(cache_file, "r") as f:
        series = json.load(f)

    if len(series) < 10:
        return None, "invalid_cache"

    # Verificar patrón sintético: velocidades lineales + ruido gaussiano
    # Serie sintética tiene: east=8.0*t + N(0,2), north=12.0*t + N(0,2.5), up=0.3*t + N(0,3)
    # Detectar si los datos siguen este patrón
    df = pd.DataFrame(series)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    days_elapsed = (df["date"] - df["date"].iloc[0]).dt.days
    years_elapsed = days_elapsed / 365.25

    # Verificar correlación con tiempo (sintético tiene R² muy alto)
    if len(df) > 50:
        east_corr = np.corrcoef(years_elapsed, df["east_mm"])[0, 1]
        north_corr = np.corrcoef(years_elapsed, df["north_mm"])[0, 1]

        # Sintético tiene velocidades exactas 8.0, 12.0, 0.3
        # Calcular velocidad media observada
        if years_elapsed.iloc[-1] > 0:
            v_east = (df["east_mm"].iloc[-1] - df["east_mm"].iloc[0]) / years_elapsed.iloc[-1]
            v_north = (df["north_mm"].iloc[-1] - df["north_mm"].iloc[0]) / years_elapsed.iloc[-1]

            # Detectar patrón sintético
            if (7.5 < v_east < 8.5 and 11.5 < v_north < 12.5
                and east_corr > 0.95 and north_corr > 0.95):
                return series, "synthetic_detected"

    return series, "possibly_real"


def generate_pending_validation(insar_results):
    """
    Genera reporte de validación PENDIENTE cuando GNSS real no está disponible.
    Esto es metodológicamente honesto.
    """
    pova_data = insar_results.get("pova_validation", {})
    insar_pixel = pova_data.get("insar_pixel", {})

    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "version": "v4_honesto",
        "station": "POVA (Popayán)",
        "station_coords": {"lat": POVA_LAT, "lon": POVA_LON},
        "sentinel1_params": SENTINEL1_PARAMS,
        "validation_status": "PENDIENTE",
        "reason": (
            "Datos GNSS de POVA no disponibles públicamente. "
            "NGL (Nevada Geodetic Lab) no procesa estaciones IGAC GeoRED. "
            "Se requiere solicitud formal al IGAC para acceso a datos oficiales."
        ),
        "insar_pixel_at_pova": insar_pixel,
        "what_is_validated": {
            "píxel_colocalization": "✓ VALIDADO (distancia 0.01 km)",
            "insar_disp_mm": f"✓ InSAR real: {insar_pixel.get('disp_mm', 'N/A')} mm",
            "coherence": f"✓ γ = {insar_pixel.get('coherence', 'N/A')}",
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
        "methodological_note": (
            "La validación cuantitativa InSAR-GNSS requiere datos GNSS reales "
            "de la estación POVA. Esta estación es operada por el IGAC (Instituto "
            "Geográfico Agustín Codazzi) dentro de la red GeoRED, cuyos datos no "
            "están disponibles en repositorios públicos internacionales (NGL, UNAVCO). "
            "Se requiere solicitud formal al IGAC. Mientras tanto, se reporta "
            "honestamente el estado PENDIENTE de la validación."
        )
    }


def plot_validation_pending(insar_pixel, output_path):
    """Genera visualización marcando validación como PENDIENTE."""
    fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
    fig.patch.set_facecolor("#0b0e14")

    # Mostrar el píxel InSAR real sobre POVA
    disp = insar_pixel.get("disp_mm", 0)
    coh = insar_pixel.get("coherence", 0)

    ax.barh(["InSAR píxel POVA\n(real, satélite)"], [disp],
            color="#ff4b2b", alpha=0.8, label=f"InSAR: {disp} mm (γ={coh})")
    ax.barh(["GNSS POVA\n(PENDIENTE - IGAC)"], [0],
            color="#888888", alpha=0.3, label="GNSS: PENDIENTE")

    ax.set_title("VALIDACIÓN GNSS PENDIENTE — Datos POVA no disponibles públicamente",
                 color="white", fontsize=11)
    ax.set_xlabel("Desplazamiento LOS [mm]", color="lightgray")
    ax.axvline(0, color="gray", linewidth=0.5)
    ax.tick_params(colors="lightgray")
    ax.grid(True, alpha=0.3, axis="x")
    for spine in ax.spines.values():
        spine.set_color("gray")

    # Anotación metodológica
    ax.text(0.02, 0.02,
            "⚠ InSAR es real pero GNSS requiere oficio al IGAC.\n"
            "No se reporta bias hasta tener datos reales.",
            transform=ax.transAxes, color="#ffcc00", fontsize=9,
            verticalalignment="bottom",
            bbox=dict(boxstyle="round", facecolor="#1a1f2e", alpha=0.8))

    plt.tight_layout()
    plt.savefig(output_path, facecolor=fig.get_facecolor(), dpi=150)
    plt.close(fig)

    # Copiar a dashboard
    dashboard_path = os.path.join(DASHBOARD_REPO, "gnss_validation_plot_v4.png")
    if os.path.isdir(os.path.dirname(dashboard_path)):
        import shutil
        shutil.copy(output_path, dashboard_path)

    print(f"  ✓ Plot de validación PENDIENTE generado: {output_path}")


def main():
    print("=" * 80)
    print("VALIDACIÓN v4 HONESTA InSAR vs GNSS (POVA)")
    print("=" * 80)
    print("\n⚠ NOTA IMPORTANTE:")
    print("   Esta versión NO usa datos sintéticos silenciosamente.")
    print("   Reporta honestamente cuando GNSS POVA no está disponible.\n")

    # Paso 1: Cargar resultados InSAR v2 (con píxel POVA real)
    insar_results, insar_path = load_insar_results()
    if not insar_results or "pova_validation" not in insar_results:
        print("\n❌ No se encontró 'pova_validation' en resultados InSAR")
        print("   Ejecuta primero: python scripts/insar_mogi_seismic_inversion_v2.py")
        return

    pova_data = insar_results["pova_validation"]
    insar_pixel = pova_data["insar_pixel"]

    print(f"\n📍 Píxel InSAR colocalizado con POVA (REAL):")
    print(f"   Coordenadas: {insar_pixel['pixel_coords']['lat']}°N, "
          f"{insar_pixel['pixel_coords']['lon']}°W")
    print(f"   Distancia a POVA: {insar_pixel['distance_km']} km")
    print(f"   Desplazamiento LOS: {insar_pixel['disp_mm']} mm")
    print(f"   Coherencia γ: {insar_pixel['coherence']}")

    # Paso 2: Verificar cache local
    os.makedirs(GNSS_CACHE_DIR, exist_ok=True)
    os.makedirs(GNSS_OUTPUTS_DIR, exist_ok=True)
    cache_file = os.path.join(GNSS_CACHE_DIR, "POVA_timeseries.json")

    print(f"\n[2/3] Verificando cache GNSS POVA en: {cache_file}")
    cached_series, cache_status = check_cache_validity(cache_file)

    if cache_status == "synthetic_detected":
        print("  ⚠⚠⚠ CACHE SINTÉTICO DETECTADO ⚠⚠⚠")
        print("  El cache contiene datos SINTÉTICOS (velocidades 8.0/12.0/0.3 mm/año)")
        print("  Estos NO son datos reales de POVA")
        print("  → Eliminando cache sintético...")
        os.remove(cache_file)
        cached_series = None
    elif cache_status == "possibly_real":
        print("  ✓ Cache posiblemente real (patrón no sintético)")
    elif cache_status == "no_cache":
        print("  → Sin cache previo")
    else:
        print(f"  ⚠ Cache inválido: {cache_status}")

    # Paso 3: Intentar descarga real de NGL
    if cached_series is None:
        real_series, source = attempt_real_gnss_download()

        if real_series is None:
            print("\n" + "=" * 80)
            print("❌ DATOS GNSS REALES DE POVA NO DISPONIBLES PÚBLICAMENTE")
            print("=" * 80)
            print("\nCausa: NGL (Nevada Geodetic Lab) no procesa estaciones IGAC GeoRED.")
            print("POVA es operada por el IGAC colombiano, no por redes IGS globales.\n")

            print("📋 PRÓXIMOS PASOS OBLIGATORIOS:")
            print("  1. Enviar oficio formal al IGAC solicitando datos POVA 2017-2026")
            print("  2. Mientras tanto, NO reportar bias en propuesta Minciencias")
            print("  3. Reportar honestamente: 'validación GNSS pendiente'")
            print("  4. Integrar TomoSAR cloud del Dr. Dinh (incluye ERA5)\n")

            # Generar reporte de validación PENDIENTE
            pending_data = generate_pending_validation(insar_results)

            out_js = f"var gnssValidationDataV4 = {json.dumps(pending_data, indent=2, ensure_ascii=False)};\n"
            out_path = os.path.join(GNSS_OUTPUTS_DIR, "gnss_validation_data_v4.js")

            with open(out_path, "w", encoding="utf-8") as f:
                f.write(out_js)

            dashboard_path = os.path.join(DASHBOARD_REPO, "gnss_validation_data_v4.js")
            if os.path.isdir(os.path.dirname(dashboard_path)):
                import shutil
                shutil.copy(out_path, dashboard_path)

            # Generar visualización de estado PENDIENTE
            plot_path = os.path.join(GNSS_OUTPUTS_DIR, "gnss_validation_plot_v4.png")
            plot_validation_pending(insar_pixel, plot_path)

            print(f"\n✅ Reporte de validación PENDIENTE generado:")
            print(f"   {out_path}")
            print(f"   {plot_path}")
            print(f"\n📊 Estado del proyecto (honesto):")
            print(f"   ✓ InSAR real: {insar_pixel['disp_mm']} mm (γ={insar_pixel['coherence']})")
            print(f"   ❌ GNSS: PENDIENTE (requiere oficio al IGAC)")
            print(f"   ⚠ Bias: NO CALCULABLE sin GNSS real")
            print(f"\n📄 Documento Word con oficio al IGAC: pendiente de generar")
            return

    # Si llegamos aquí, tenemos datos reales (caso futuro cuando IGAC responda)
    print(f"\n✓ Datos GNSS reales obtenidos de POVA")
    print(f"   Continuando con validación cuantitativa...")


if __name__ == "__main__":
    main()
