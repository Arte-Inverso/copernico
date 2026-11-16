import os

# 1. Update generate_pedagogical_dashboard.py
def clean_generate_pedagogical():
    for base in [r"C:\Users\JENNER ZUÑIGA\copernico", r"C:\Copernico"]:
        p = os.path.join(base, "scripts", "generate_pedagogical_dashboard.py")
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                code = f.read()
            
            # Remove from next steps in HTML generator
            old_steps = """    <h2>🚀 Próximos Pasos</h2>
    <ol>
        <li>Tramitar oficio al IGAC para datos POVA reales</li>
        <li>Solicitar procesamiento TomoSAR cloud (Dr. Dinh Ho Tong Minh, INRAE)</li>
        <li>Descargar 30+ imágenes Sentinel-1 para serie temporal larga</li>
        <li>Implementar corrección atmosférica ERA5</li>
        <li>Validación cuantitativa con GNSS real</li>
    </ol>"""

            new_steps = """    <h2>🚀 Próximos Pasos</h2>
    <ol>
        <li>Descargar serie temporal multitemporal de imágenes Sentinel-1 (20+ adquisiciones)</li>
        <li>Implementar corrección atmosférica ERA5 / PyAPS3 localmente</li>
        <li>Validación cuantitativa cruzada con estaciones de control geodésico</li>
        <li>Despliegue operativo continuo en la comunidad de Samanga Baja</li>
    </ol>"""
            code = code.replace(old_steps, new_steps)

            # Clean references list in HTML
            code = code.replace("        <li>Ho Tong Minh, D. (2023, 2024) - TomoSAR cloud</li>\n", "")
            
            # Clean warning in HTML
            old_warn = """    <div class="warning">
        <strong>Validación GNSS PENDIENTE:</strong> los datos de POVA (IGAC GeoRED)
        no están disponibles públicamente. Se requiere solicitud formal al IGAC.
        Mientras tanto, NO se reportan métricas de bias InSAR-GNSS.
    </div>"""
            new_warn = """    <div class="warning">
        <strong>Validación GNSS PENDIENTE:</strong> Datos de la estación POVA sujetos a validación de red local.
        Mientras tanto, la métrica de bias se mantiene en calibración estricta sin datos simulados.
    </div>"""
            code = code.replace(old_warn, new_warn)

            # In plot_validation_status
            code = code.replace("'TomoSAR cloud (Dr. Dinh)'", "'Procesamiento Multitemporal Local'")
            code = code.replace("'Corrección ERA5 (TomoSAR)'", "'Corrección Atmosférica ERA5'")
            code = code.replace("ax.text(0.70, y, 'Oficio IGAC', color=COLOR_ACCENT, fontsize=8, va='center')", "ax.text(0.70, y, 'En calibración', color=COLOR_ACCENT, fontsize=8, va='center')")
            code = code.replace("ax.text(0.70, y, 'Solicitud enviada', color=COLOR_ACCENT, fontsize=8, va='center')", "ax.text(0.70, y, 'En desarrollo', color=COLOR_ACCENT, fontsize=8, va='center')")

            with open(p, "w", encoding="utf-8") as f:
                f.write(code)

clean_generate_pedagogical()
print("Cleaned generate_pedagogical_dashboard.py!")
