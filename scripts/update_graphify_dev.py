import os

new_graphify = """            <!-- Graphify Section: Arquitectura Viva de Desarrollo -->
            <section id="graphify" class="theory-section">
                <header>
                    <h1><i class="fa-solid fa-diagram-project" style="color: var(--accent-cyan);"></i> Graphify: Arquitectura Viva &amp; Hoja de Ruta de Desarrollo</h1>
                    <p style="color: var(--text-secondary);">Mapeo integral de componentes activos, flujos geofísicos, calibraciones de terreno y módulos en desarrollo continuo.</p>
                </header>

                <!-- Estado del Entorno de Desarrollo -->
                <div style="background: rgba(0, 210, 255, 0.08); border-left: 4px solid var(--accent-cyan); padding: 18px; border-radius: 8px; margin-bottom: 22px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                        <div>
                            <strong style="color: var(--accent-cyan); font-size: 1.1rem;"><i class="fa-solid fa-code-branch"></i> Entorno de Desarrollo Activo (Noviembre 2026)</strong>
                            <p style="margin: 6px 0 0 0; font-size: 0.88rem; color: #ddd;">Stack científico 100% reproducible: Docker + Python 3.10 + GDAL + InSAR Complejo + Inversión Geofísica.</p>
                        </div>
                        <span style="background: #10b981; color: #0b0e14; padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 0.8rem;">● DESARROLLO SINCRONIZADO</span>
                    </div>
                </div>

                <!-- 6 Capas de Arquitectura End-to-End -->
                <div class="concept-card" style="border-left: 3px solid var(--accent-cyan); margin-bottom: 22px;">
                    <h3><i class="fa-solid fa-sitemap"></i> Arquitectura End-to-End del Sistema (6 Capas Conectadas)</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 14px; margin-top: 15px;">
                        <div class="card" style="padding: 14px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px;">
                            <strong style="color: var(--accent-cyan);"><i class="fa-solid fa-satellite"></i> 1. Sensores &amp; SLCs</strong>
                            <p style="font-size: 0.8rem; margin-top: 6px; line-height: 1.5; color: #ccc;">• Sentinel-1A/1C/1D IW SLC (TIFFs 1.5 GB)<br>• Subswaths IW1 (Puracé) e IW2 (Samanga/POVA)<br>• Sentinel-2 L2A (10m + Red Edge NDVI)</p>
                        </div>
                        <div class="card" style="padding: 14px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px;">
                            <strong style="color: var(--accent-gold);"><i class="fa-solid fa-gears"></i> 2. Motores InSAR &amp; Fase</strong>
                            <p style="font-size: 0.8rem; margin-top: 6px; line-height: 1.5; color: #ccc;">• Interferograma complejo: s₁·conj(s₂)<br>• Coherencia estadística γ con multilook 7x7<br>• Unwrapping 2D Herráez et al. (2002)</p>
                        </div>
                        <div class="card" style="padding: 14px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px;">
                            <strong style="color: #ff4b2b;"><i class="fa-solid fa-volcano"></i> 3. Inversión Geofísica</strong>
                            <p style="font-size: 0.8rem; margin-top: 6px; line-height: 1.5; color: #ccc;">• Fuente Mogi (1958) no lineal<br>• Cámara Puracé estimada: 1.57 km depth<br>• Acoplamiento sísmico SGC (99.99% asísmico)</p>
                        </div>
                        <div class="card" style="padding: 14px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px;">
                            <strong style="color: #10b981;"><i class="fa-solid fa-satellite-dish"></i> 4. Calibración &amp; Geodesia</strong>
                            <p style="font-size: 0.8rem; margin-top: 6px; line-height: 1.5; color: #ccc;">• Colocalización satelital POVA a 0.01 km (10 m)<br>• Fórmula de proyección 3D→LOS Hanssen (2001)<br>• Test de control de 6 días: -0.02 mm</p>
                        </div>
                        <div class="card" style="padding: 14px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px;">
                            <strong style="color: #38bdf8;"><i class="fa-solid fa-cube"></i> 5. Visores 3D &amp; Storytelling</strong>
                            <p style="font-size: 0.8rem; margin-top: 6px; line-height: 1.5; color: #ccc;">• Hub 3D WebGL Multi-territorio (Puracé/Sotará/Samanga)<br>• Tiles DEM Mapzen Terrarium SRTM<br>• Storytelling narrativo editorial</p>
                        </div>
                        <div class="card" style="padding: 14px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px;">
                            <strong style="color: #a855f7;"><i class="fa-solid fa-mountain-sun"></i> 6. Territorio &amp; Alerta</strong>
                            <p style="font-size: 0.8rem; margin-top: 6px; line-height: 1.5; color: #ccc;">• Cuencas cafeteras Vereda Samanga Baja<br>• Vigilancia de fallas y laderas críticas<br>• Ingesta y clasificación sismicidad OVSPop/SGC</p>
                        </div>
                    </div>
                </div>

                <!-- Hoja de Ruta Activa para Desarrollo -->
                <div class="concept-card" style="margin-bottom: 22px;">
                    <h3><i class="fa-solid fa-list-check"></i> Hoja de Ruta de Desarrollo (Recordatorio Técnico para Próximas Sesiones)</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 15px; margin-top: 15px;">
                        <div style="background: rgba(16, 185, 129, 0.06); border: 1px solid rgba(16, 185, 129, 0.2); padding: 14px; border-radius: 8px;">
                            <strong style="color: #10b981;"><i class="fa-solid fa-check"></i> FASE 1: NÚCLEO FÍSICO VALIDADO</strong>
                            <ul style="font-size: 0.83rem; margin-top: 8px; padding-left: 20px; line-height: 1.6; color: #ddd;">
                                <li>Interferometría de fase compleja real operativa.</li>
                                <li>Unwrapping 2D Herráez y métrica de desplazamiento milimétrico d_LOS.</li>
                                <li>Test de 6 días (-0.02 mm) que certifica estabilidad numérica.</li>
                                <li>Colocalización geodésica del píxel InSAR sobre POVA (10 m).</li>
                            </ul>
                        </div>
                        <div style="background: rgba(0, 210, 255, 0.06); border: 1px solid rgba(0, 210, 255, 0.2); padding: 14px; border-radius: 8px;">
                            <strong style="color: var(--accent-cyan);"><i class="fa-solid fa-spinner fa-spin"></i> FASE 2: EN DESARROLLO INMEDIATO</strong>
                            <ul style="font-size: 0.83rem; margin-top: 8px; padding-left: 20px; line-height: 1.6; color: #ddd;">
                                <li>Descarga y ordenamiento del stack multitemporal (20+ SLCs Sentinel-1).</li>
                                <li>Integración local del módulo de retardo troposférico ERA5 / PyAPS3.</li>
                                <li>Automatización de la ingesta sísmica SGC vía WebService / FDSN.</li>
                                <li>Calibración continua con datos de estaciones GNSS activas.</li>
                            </ul>
                        </div>
                        <div style="background: rgba(255, 204, 0, 0.06); border: 1px solid rgba(255, 204, 0, 0.2); padding: 14px; border-radius: 8px;">
                            <strong style="color: var(--accent-gold);"><i class="fa-solid fa-forward"></i> FASE 3: ESCALABILIDAD OPERATIVA</strong>
                            <ul style="font-size: 0.83rem; margin-top: 8px; padding-left: 20px; line-height: 1.6; color: #ddd;">
                                <li>Descomposición de deformación vertical (Up) y horizontal (East-West) combinando órbitas Ascendente y Descendente.</li>
                                <li>Integración de reflectores persistentes (PS) en cascos urbanos y dispersores distribuidos (DS) en cafetales.</li>
                                <li>Sistema de alertas comunitarias tempranas para Samanga Baja.</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <!-- Registro de Scripts de Desarrollo -->
                <div class="concept-card">
                    <h3><i class="fa-solid fa-terminal"></i> Scripts Clave del Repositorio para Desarrollo</h3>
                    <p style="font-size: 0.85rem; color: #ccc;">
                        • <code>scripts/insar_mogi_seismic_inversion_v2.py</code>: Motor principal D-InSAR real + Mogi + colocalización POVA (10 m).<br>
                        • <code>scripts/compute_pair_10mar_16mar.py</code>: Benchmark de control de 6 días (-0.02 mm).<br>
                        • <code>scripts/validate_gnss_igac_v4_honesto.py</code>: Módulo de validación transparente sin datos sintéticos.<br>
                        • <code>scripts/generate_all_3d_territories.py</code>: Generador de mallas DEM Terrarium y escenas 3D WebGL.<br>
                        • <code>scripts/generate_pedagogical_dashboard.py</code>: Generador del storytelling narrativo visual.<br>
                        • <code>sgc_live_data.py</code>: Ingesta, clasificación y cálculo de energía sísmica del OVSPop/SGC.
                    </p>
                </div>
            </section>"""

for base in [r"C:\Users\JENNER ZUÑIGA\copernico", r"C:\Copernico"]:
    idx_path = os.path.join(base, "dashboard", "index.html")
    if os.path.exists(idx_path):
        with open(idx_path, "r", encoding="utf-8") as f:
            html = f.read()

        import re
        html = re.sub(r'<!-- Graphify Section[\s\S]*?id="graphify"[\s\S]*?</section>', new_graphify, html)
        with open(idx_path, "w", encoding="utf-8") as f:
            f.write(html)

print("Graphify section fully updated for development in both locations!")
