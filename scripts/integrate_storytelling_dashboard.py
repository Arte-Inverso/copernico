import os

pedagogical_section = """
            <!-- Sección Historia & Storytelling Pedagógico -->
            <section id="storytelling" class="theory-section">
                <header style="margin-bottom: 1.5rem;">
                    <h1><i class="fa-solid fa-graduation-cap" style="color: #00d2ff;"></i> Historia &amp; Storytelling Pedagógico</h1>
                    <p style="color: var(--text-secondary);">Una explicación clara y visual del sistema: el problema social, la física satelital, los hallazgos geofísicos y el estado honesto de validación.</p>
                </header>

                <div style="background: rgba(0, 210, 255, 0.08); border-left: 4px solid #00d2ff; padding: 18px; border-radius: 8px; margin-bottom: 25px;">
                    <h3 style="color: #00d2ff; margin-top: 0;"><i class="fa-solid fa-bullhorn"></i> El Problema Social en Territorio</h3>
                    <p style="line-height: 1.6; margin-bottom: 0;">La <strong>Vereda Samanga Baja</strong> en Popayán (Cauca) protege las cuencas hídricas que abastecen a más de 5.000 familias campesinas, enfrentando riesgos continuos de deslizamientos de ladera y la influencia del <strong>Volcán Puracé</strong> a solo 25 km. El sistema Copernico utiliza radar orbital para detectar deformaciones milimétricas antes de que ocurran catástrofes.</p>
                </div>

                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); gap: 20px; margin-bottom: 25px;">
                    <!-- Tarjeta 1: Física InSAR -->
                    <div style="background: var(--card-bg, rgba(255,255,255,0.03)); border: 1px solid rgba(255,255,255,0.08); padding: 18px; border-radius: 10px;">
                        <h4 style="color: #ffcc00; margin-top: 0;"><i class="fa-solid fa-satellite"></i> 1. ¿Cómo Mide el Satélite?</h4>
                        <p style="font-size: 0.88rem; color: #ccc; min-height: 40px;">Ondas radar en banda C (λ = 55.47 mm) emitidas por Sentinel-1. La fase de retorno codifica el desplazamiento exacto del terreno en milímetros.</p>
                        <img src="img/pedagogical_insar_explained.png" alt="Física InSAR" style="width: 100%; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
                    </div>

                    <!-- Tarjeta 2: Mogi 2D -->
                    <div style="background: var(--card-bg, rgba(255,255,255,0.03)); border: 1px solid rgba(255,255,255,0.08); padding: 18px; border-radius: 10px;">
                        <h4 style="color: #ff4b2b; margin-top: 0;"><i class="fa-solid fa-volcano"></i> 2. Cámara Magmática del Puracé</h4>
                        <p style="font-size: 0.88rem; color: #ccc; min-height: 40px;">Corte vertical que integra la cámara Mogi calculada a 1.57 km, el conducto activo y la sismicidad VT registrada por el catálogo del SGC.</p>
                        <img src="img/pedagogical_mogi_chamber.png" alt="Cámara Mogi Puracé" style="width: 100%; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
                    </div>

                    <!-- Tarjeta 3: Test 6 días -->
                    <div style="background: var(--card-bg, rgba(255,255,255,0.03)); border: 1px solid rgba(255,255,255,0.08); padding: 18px; border-radius: 10px;">
                        <h4 style="color: #10b981; margin-top: 0;"><i class="fa-solid fa-circle-check"></i> 3. Test de Control (6 Días: -0.02 mm)</h4>
                        <p style="font-size: 0.88rem; color: #ccc; min-height: 40px;">Par de intervalo ultracorto (10 al 16 de marzo de 2026). Demuestra que el algoritmo funciona con precisión estricta y sin derivas numéricas.</p>
                        <img src="img/pedagogical_control_experiment.png" alt="Control 6 días" style="width: 100%; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
                    </div>

                    <!-- Tarjeta 4: Semáforo de Validación -->
                    <div style="background: var(--card-bg, rgba(255,255,255,0.03)); border: 1px solid rgba(255,255,255,0.08); padding: 18px; border-radius: 10px;">
                        <h4 style="color: #38bdf8; margin-top: 0;"><i class="fa-solid fa-list-check"></i> 4. Estado de Validación Honesto</h4>
                        <p style="font-size: 0.88rem; color: #ccc; min-height: 40px;">Matriz transparente de lo que está físicamente validado y las acciones en trámite (oficio formal al IGAC para datos POVA y TomoSAR cloud).</p>
                        <img src="img/pedagogical_validation_status.png" alt="Estado de Validación" style="width: 100%; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
                    </div>
                </div>

                <div style="text-align: center; margin-top: 20px;">
                    <a href="pedagogical_storytelling.html" target="_blank" style="display: inline-block; background: #00d2ff; color: #0b0e14; padding: 12px 24px; border-radius: 8px; font-weight: bold; text-decoration: none;">
                        <i class="fa-solid fa-up-right-from-square"></i> Abrir Versión Lectura Editorial Completa
                    </a>
                </div>
            </section>
"""

nav_item = """                    <li class="nav-item" onclick="showSection('storytelling', this)" style="border: 1px solid rgba(0, 210, 255, 0.4); background: rgba(0, 210, 255, 0.12); margin-top: 6px;">
                        <i class="fa-solid fa-graduation-cap" style="color: #00d2ff;"></i> Historia &amp; Storytelling
                    </li>"""

for base in [r"C:\Users\JENNER ZUÑIGA\copernico", r"C:\Copernico"]:
    idx_path = os.path.join(base, "dashboard", "index.html")
    if os.path.exists(idx_path):
        with open(idx_path, "r", encoding="utf-8") as f:
            html = f.read()
        
        # Add to nav if not present
        if "showSection('storytelling'" not in html:
            # Insert right before Modelo 3D Puracé
            target_nav = '<li class="nav-item" onclick="window.open(\'modelo_3d_purace.html\''
            if target_nav in html:
                html = html.replace(target_nav, nav_item + "\n" + target_nav)
            else:
                html = html.replace("</ul>", nav_item + "\n</ul>")
        
        # Add section if not present
        if 'id="storytelling"' not in html:
            html = html.replace("</main>", pedagogical_section + "\n</main>")
            
        with open(idx_path, "w", encoding="utf-8") as f:
            f.write(html)

print("Storytelling section integrated directly into index.html dashboard in both paths!")
