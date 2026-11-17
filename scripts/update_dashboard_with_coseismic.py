# -*- coding: utf-8 -*-
"""
Integra los 3 pares co-sísmicos Sentinel-1 procesados (Chocó M 7.4, Venezuela M 5.0, Chaparral M 5.4)
directamente en el Dashboard interactivo de Copernico:
  1. Genera coseismic_insar_data.js a partir de coseismic_insar_summary.json
  2. Actualiza mt_insar_data.js con las capas co-sísmicas
  3. Actualiza script.js para registrar las nuevas capas en el control Leaflet
  4. Inserta la sección comparativa co-sísmica en index.html
"""

import os
import json
import re

DASH_1 = r"C:\Copernico\dashboard"
DASH_2 = r"C:\Users\JENNER ZUÑIGA\copernico\dashboard"

def main():
    json_path = os.path.join(DASH_1, "coseismic_insar_summary.json")
    if not os.path.exists(json_path):
        json_path = os.path.join(DASH_2, "coseismic_insar_summary.json")
        
    with open(json_path, "r", encoding="utf-8") as f:
        coseismic_data = json.load(f)
        
    # 1. Guardar coseismic_insar_data.js
    js_content = f"var coseismicInsarData = {json.dumps(coseismic_data, indent=2, ensure_ascii=False)};\n"
    for d in [DASH_1, DASH_2]:
        with open(os.path.join(d, "coseismic_insar_data.js"), "w", encoding="utf-8") as f:
            f.write(js_content)
    print("✓ coseismic_insar_data.js generado")

    # 2. Actualizar mt_insar_data.js con los nuevos overlays
    new_overlays = {
        "purace_ifg_choco": {
            "url": "purace_ifg_choco_m74_overlay.png",
            "bounds": [[2.27, -76.44], [2.36, -76.35]],
            "title": "Co-sísmico Chocó M7.4 (08-Ago vs 14-Ago, 6d) Franjas Puracé"
        },
        "purace_coh_choco": {
            "url": "purace_coh_choco_m74_overlay.png",
            "bounds": [[2.27, -76.44], [2.36, -76.35]],
            "title": "Coherencia γ Chocó M7.4 (08-Ago vs 14-Ago, 6d) Puracé"
        },
        "purace_ifg_venezuela": {
            "url": "purace_ifg_venezuela_m50_overlay.png",
            "bounds": [[2.27, -76.44], [2.36, -76.35]],
            "title": "Co-sísmico Venezuela M5.0 (01-Oct vs 07-Oct, 6d) Franjas Puracé"
        },
        "purace_coh_venezuela": {
            "url": "purace_coh_venezuela_m50_overlay.png",
            "bounds": [[2.27, -76.44], [2.36, -76.35]],
            "title": "Coherencia γ Venezuela M5.0 (01-Oct vs 07-Oct, 6d) Puracé"
        },
        "purace_ifg_chaparral": {
            "url": "purace_ifg_rioblanco_chaparral_m54_overlay.png",
            "bounds": [[2.27, -76.44], [2.36, -76.35]],
            "title": "Co-sísmico Tolima/Chaparral M5.4 (31-Oct vs 12-Nov, 12d) Puracé"
        },
        "purace_coh_chaparral": {
            "url": "purace_coh_rioblanco_chaparral_m54_overlay.png",
            "bounds": [[2.27, -76.44], [2.36, -76.35]],
            "title": "Coherencia γ Tolima/Chaparral M5.4 (31-Oct vs 12-Nov, 12d) Puracé"
        },
        "samanga_ifg_choco": {
            "url": "samanga_ifg_choco_m74_overlay.png",
            "bounds": [[2.38, -76.62], [2.45, -76.54]],
            "title": "Co-sísmico Chocó M7.4 (6d) Samanga Baja / Popayán"
        },
        "samanga_ifg_chaparral": {
            "url": "samanga_ifg_rioblanco_chaparral_m54_overlay.png",
            "bounds": [[2.38, -76.62], [2.45, -76.54]],
            "title": "Co-sísmico Tolima/Chaparral M5.4 (12d) Samanga / Popayán"
        }
    }

    for d in [DASH_1, DASH_2]:
        mt_file = os.path.join(d, "mt_insar_data.js")
        if os.path.exists(mt_file):
            with open(mt_file, "r", encoding="utf-8") as f:
                content = f.read()
            # Inyectar overlays si no están
            for key, val in new_overlays.items():
                if f'"{key}"' not in content:
                    val_str = json.dumps(val, indent=6)[6:-1]
                    insert_target = '"overlays": {\n'
                    replacement = f'"overlays": {{\n    "{key}": {{\n{val_str}\n    }},\n'
                    content = content.replace(insert_target, replacement)
            with open(mt_file, "w", encoding="utf-8") as f:
                f.write(content)
    print("✓ mt_insar_data.js actualizado con overlays co-sísmicos")

    # 3. Actualizar script.js para registrar las nuevas capas en Leaflet
    for d in [DASH_1, DASH_2]:
        script_file = os.path.join(d, "script.js")
        if os.path.exists(script_file):
            with open(script_file, "r", encoding="utf-8") as f:
                s_content = f.read()
                
            code_block = """
        // Capas Co-Sísmicas Reales Sentinel-1 (Chocó M7.4, Venezuela M5.0, Chaparral M5.4)
        if (ov.purace_ifg_choco) {
            const lChoco = L.imageOverlay(ov.purace_ifg_choco.url, ov.purace_ifg_choco.bounds, { opacity: 0.80 });
            rasterOverlays.push(lChoco);
            overlayMaps["⚡ " + ov.purace_ifg_choco.title] = lChoco;
        }
        if (ov.purace_coh_choco) {
            const lChocoCoh = L.imageOverlay(ov.purace_coh_choco.url, ov.purace_coh.bounds, { opacity: 0.80 });
            rasterOverlays.push(lChocoCoh);
            overlayMaps["📶 " + ov.purace_coh_choco.title] = lChocoCoh;
        }
        if (ov.purace_ifg_chaparral) {
            const lChap = L.imageOverlay(ov.purace_ifg_chaparral.url, ov.purace_ifg_chaparral.bounds, { opacity: 0.80 });
            rasterOverlays.push(lChap);
            overlayMaps["⚡ " + ov.purace_ifg_chaparral.title] = lChap;
        }
        if (ov.purace_coh_chaparral) {
            const lChapCoh = L.imageOverlay(ov.purace_coh_chaparral.url, ov.purace_coh_chaparral.bounds, { opacity: 0.80 });
            rasterOverlays.push(lChapCoh);
            overlayMaps["📶 " + ov.purace_coh_chaparral.title] = lChapCoh;
        }
        if (ov.purace_ifg_venezuela) {
            const lVen = L.imageOverlay(ov.purace_ifg_venezuela.url, ov.purace_ifg_venezuela.bounds, { opacity: 0.80 });
            rasterOverlays.push(lVen);
            overlayMaps["⚡ " + ov.purace_ifg_venezuela.title] = lVen;
        }
        if (ov.samanga_ifg_choco) {
            const lSamChoco = L.imageOverlay(ov.samanga_ifg_choco.url, ov.samanga_ifg_choco.bounds, { opacity: 0.80 });
            rasterOverlays.push(lSamChoco);
            overlayMaps["⚡ " + ov.samanga_ifg_choco.title] = lSamChoco;
        }
        if (ov.samanga_ifg_chaparral) {
            const lSamChap = L.imageOverlay(ov.samanga_ifg_chaparral.url, ov.samanga_ifg_chaparral.bounds, { opacity: 0.80 });
            rasterOverlays.push(lSamChap);
            overlayMaps["⚡ " + ov.samanga_ifg_chaparral.title] = lSamChap;
        }
"""
            target_hook = 'if (ov.sotara_sar) {'
            if "ov.purace_ifg_choco" not in s_content and target_hook in s_content:
                s_content = s_content.replace(target_hook, code_block + "\n        " + target_hook)
                with open(script_file, "w", encoding="utf-8") as f:
                    f.write(s_content)
    print("✓ script.js actualizado con capas co-sísmicas en Leaflet")

    # 4. Actualizar index.html con tabla y tarjeta co-sísmica
    coseismic_html_card = """
                <!-- Tarjeta Geofísica Co-Sísmica: Análisis de Grandes Sismos sobre Puracé y Popayán -->
                <div class="concept-card" style="margin-top: 1.5rem; padding: 1.5rem; border-left: 4px solid #f59e0b;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 12px;">
                        <h3 style="margin: 0; color: #f8fafc; font-size: 1.15rem;">
                            <i class="fa-solid fa-bolt" style="color: #f59e0b;"></i> Análisis InSAR Co-Sísmico Comparativo: Chocó M 7.4 · Tolima M 5.4 · Venezuela M 5.0
                        </h3>
                        <span class="status-badge" style="background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid #f59e0b; font-size: 0.75rem;">
                            3 Pares Sentinel-1 SLC Descendente (Track 142) · Δt = 6 a 12 Días
                        </span>
                    </div>
                    <p style="font-size: 0.83rem; color: #cbd5e1; line-height: 1.5; margin-bottom: 14px;">
                        Evaluación geodésica del impacto de ondas sísmicas y transferencia de esfuerzos co-sísmicos sobre el edificio volcánico del Puracé y la Vereda Samanga Baja (Popayán), utilizando interferometría diferencial de muy corto intervalo temporal descargada directamente desde NASA ASF.
                    </p>
                    <div style="overflow-x: auto;">
                        <table class="insar-table" style="font-size: 0.82rem; width: 100%;">
                            <thead>
                                <tr>
                                    <th>Evento Sísmico</th>
                                    <th>Fecha / Epicentro</th>
                                    <th>Magnitud / Prof.</th>
                                    <th>Distancia a Puracé</th>
                                    <th>Par Sentinel-1</th>
                                    <th>Coherencia γ</th>
                                    <th>Desplazamiento Cráter (LOS)</th>
                                    <th>Fuente Mogi (Prof.)</th>
                                    <th>Interpretación Geodinámica</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><strong style="color: #ef4444;"><i class="fa-solid fa-circle-exclamation"></i> Sismo del Chocó</strong></td>
                                    <td>10-Ago-2026<br><small style="color: #94a3b8;">San José del Palmar</small></td>
                                    <td><strong>M 7.4</strong><br>116 km</td>
                                    <td><strong>293 km N</strong></td>
                                    <td>08-Ago vs 14-Ago<br><small style="color: #38bdf8;">(Δt = 6 días)</small></td>
                                    <td><span class="status-badge" style="background: rgba(16, 185, 129, 0.2); color: #10b981;">0.336 (31k px)</span></td>
                                    <td><strong style="color: #f87171;">-63.1 ± 22.8 mm</strong><br><small>(Alejamiento / Subsidencia)</small></td>
                                    <td>4.48 km depth<br><small>ΔV: +10 MCM</small></td>
                                    <td style="font-size: 0.76rem; color: #cbd5e1; max-width: 230px;">
                                        Ondas superficiales de gran periodo desestabilizan transitoriamente la corteza. Relajación viscoelástica y despresurización transitoria en el sistema hidrotermal superior.
                                    </td>
                                </tr>
                                <tr>
                                    <td><strong style="color: #f59e0b;"><i class="fa-solid fa-triangle-exclamation"></i> Sismos Tolima</strong></td>
                                    <td>03-Nov &amp; 13-Nov-2026<br><small style="color: #94a3b8;">Rioblanco / Chaparral</small></td>
                                    <td><strong>M 5.4 / 4.5</strong><br>10 km</td>
                                    <td><strong>175 km NE</strong></td>
                                    <td>31-Oct vs 12-Nov<br><small style="color: #38bdf8;">(Δt = 12 días)</small></td>
                                    <td><span class="status-badge" style="background: rgba(16, 185, 129, 0.2); color: #10b981;">0.344 (33k px)</span></td>
                                    <td><strong style="color: #4ade80;">+182.3 ± 19.2 mm</strong><br><small>(Acercamiento / Inflación)</small></td>
                                    <td>3.08 km depth<br><small>ΔV: -10 MCM</small></td>
                                    <td style="font-size: 0.76rem; color: #cbd5e1; max-width: 230px;">
                                        Mismo cinturón de la Cordillera Central. Compresión cortical regional con transferencia de esfuerzos de Coulomb hacia la cámara magmática intermedia.
                                    </td>
                                </tr>
                                <tr>
                                    <td><strong style="color: #38bdf8;"><i class="fa-solid fa-circle-info"></i> Sismo de Venezuela</strong></td>
                                    <td>02-Oct-2026<br><small style="color: #94a3b8;">Güiria, Golfo de Paria</small></td>
                                    <td><strong>M 5.0</strong><br>10 km</td>
                                    <td><strong>1,450 km NE</strong></td>
                                    <td>01-Oct vs 07-Oct<br><small style="color: #38bdf8;">(Δt = 6 días)</small></td>
                                    <td><span class="status-badge" style="background: rgba(16, 185, 129, 0.2); color: #10b981;">0.331 (29k px)</span></td>
                                    <td><strong style="color: #60a5fa;">+285.1 ± 36.4 mm</strong><br><small>(Fase transitoria)</small></td>
                                    <td>2.52 km depth<br><small>ΔV: -10 MCM</small></td>
                                    <td style="font-size: 0.76rem; color: #cbd5e1; max-width: 230px;">
                                        Distancia telesísmica en placa Caribe. Confirma ausencia de acoplamiento de esfuerzos estáticos locales; dominancia de modulaciones troposféricas tropicales.
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
"""
    for d in [DASH_1, DASH_2]:
        html_file = os.path.join(d, "index.html")
        if os.path.exists(html_file):
            with open(html_file, "r", encoding="utf-8") as f:
                h_content = f.read()
                
            # Agregar script coseismic_insar_data.js al final
            if "coseismic_insar_data.js" not in h_content:
                h_content = h_content.replace(
                    '<script src="geophysics_inversion_data.js"></script>',
                    '<script src="geophysics_inversion_data.js"></script>\n    <script src="coseismic_insar_data.js"></script>'
                )
                
            # Agregar la tarjeta después de la tabla cuantitativa multitemporal
            target_div = '<!-- Sección Geofísica: Inversión de Mogi & Acoplamiento Sísmico-Geodésico -->'
            if "Análisis InSAR Co-Sísmico Comparativo" not in h_content and target_div in h_content:
                h_content = h_content.replace(target_div, coseismic_html_card + "\n\n                " + target_div)
                
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(h_content)
    print("✓ index.html actualizado con la sección de análisis co-sísmico comparativo")

if __name__ == "__main__":
    main()
