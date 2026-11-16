import os

code_to_add_script = """
// Integración Validación GNSS IGAC
function renderGnssValidation() {
    if (typeof gnssValidationData === 'undefined') {
        console.log('Datos GNSS no disponibles');
        return;
    }
    const data = gnssValidationData;
    const container = document.getElementById('gnss-validation-content');
    if (!container) return;

    const m = data.metrics;
    const verdictColor = m.verdict === 'óptimo' ? '#10b981' :
                        m.verdict === 'aceptable' ? '#f59e0b' : '#ef4444';

    container.innerHTML = `
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px;">
            <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px;">
                <h4 style="color: #00d2ff; margin-bottom: 10px;">Estación</h4>
                <p><strong>${data.station}</strong></p>
                <p style="font-size: 0.85rem; color: #aaa;">
                    Lat: ${data.station_info.lat}°N<br>
                    Lon: ${data.station_info.lon}°W<br>
                    Operador: ${data.station_info.operator}
                </p>
            </div>
            <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px;">
                <h4 style="color: #00d2ff; margin-bottom: 10px;">Velocidad GNSS</h4>
                <p style="font-size: 1.8rem; font-weight: 700;">
                    ${m.gnss_velocity_los_mm_per_year} <small>mm/año</small>
                </p>
                <p style="font-size: 0.85rem; color: #aaa;">
                    Periodo: ${data.gnss_series_summary.start_date} a ${data.gnss_series_summary.end_date}
                </p>
            </div>
            <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px;">
                <h4 style="color: #00d2ff; margin-bottom: 10px;">Bias InSAR - GNSS</h4>
                <p style="font-size: 1.8rem; font-weight: 700; color: ${verdictColor};">
                    ${m.bias_mm < 0 ? '' : '+'}${m.bias_mm} <small>mm</small>
                </p>
                <p style="font-size: 0.85rem; color: #aaa;">RMSE: ±${m.rmse_mm} mm</p>
            </div>
            <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px; border: 2px solid ${verdictColor};">
                <h4 style="margin-bottom: 10px;">Veredicto</h4>
                <p style="font-size: 1.4rem; font-weight: 700; color: ${verdictColor}; text-transform: uppercase;">${m.verdict}</p>
            </div>
        </div>
        <div style="background: rgba(255,255,255,0.03); padding: 15px; border-radius: 8px; margin-top: 20px;">
            <h4 style="color: #00d2ff; margin-bottom: 10px;">Interpretación</h4>
            <p style="font-size: 0.9rem; line-height: 1.6;">${data.interpretation}</p>
        </div>
    `;
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', renderGnssValidation);
} else {
    renderGnssValidation();
}
"""

gnss_section = """
    <!-- Sección Validación GNSS IGAC -->
    <section id="gnss-validation" class="theory-section" style="margin-top: 30px;">
        <h2><i class="fa-solid fa-satellite-dish"></i> Validación InSAR vs GNSS IGAC</h2>
        <p>Validación cuantitativa de resultados InSAR contra estación continua POVA (Popayán) de la red GeoRED del IGAC.</p>
        <div id="gnss-validation-content" style="margin-top: 20px;"></div>
        <div style="text-align: center; margin-top: 20px;">
            <img src="gnss_validation_plot.png" alt="Validación InSAR vs GNSS POVA" style="width: 100%; max-width: 900px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
        </div>
    </section>
"""

for base_dir in [r'C:\Users\JENNER ZUÑIGA\copernico', r'C:\Copernico']:
    html_path = os.path.join(base_dir, 'dashboard', 'index.html')
    if os.path.exists(html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        if 'gnss_validation_data.js' not in html:
            html = html.replace('</head>', '    <script src="gnss_validation_data.js"></script>\n</head>')
        if 'id="gnss-validation"' not in html:
            html = html.replace('</main>', gnss_section + '\n</main>')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)

    js_path = os.path.join(base_dir, 'dashboard', 'script.js')
    if os.path.exists(js_path):
        with open(js_path, 'r', encoding='utf-8') as f:
            js = f.read()
        if 'renderGnssValidation' not in js:
            js = js + "\n" + code_to_add_script
            with open(js_path, 'w', encoding='utf-8') as f:
                f.write(js)

print("Dashboard integration complete in both locations!")
