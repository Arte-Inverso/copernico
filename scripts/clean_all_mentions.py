import os, re

def clean_file(path):
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    # Reemplazar frases específicas solicitadas
    text = text.replace("Tramitar oficio al IGAC para datos POVA reales", "Validación cruzada con redes geodésicas locales")
    text = text.replace("Solicitar procesamiento TomoSAR cloud (Dr. Dinh Ho Tong Minh, INRAE)", "Ampliación a procesamiento multitemporal (20+ imágenes) con corrección ERA5")
    text = text.replace("TomoSAR cloud (Dr. Dinh)", "Procesamiento Multitemporal Local")
    text = text.replace("TomoSAR cloud", "Procesamiento InSAR Multitemporal")
    text = text.replace("TomoSAR", "InSAR Multitemporal")
    text = text.replace("Dr. Dinh Ho Tong Minh", "Procesamiento Multitemporal")
    text = text.replace("Dr. Dinh", "Procesamiento Multitemporal")
    text = text.replace("oficio al IGAC", "calibración geodésica")
    text = text.replace("Oficio IGAC", "Calibración geodésica")

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

files_to_clean = [
    r"C:\Users\JENNER ZUÑIGA\copernico\dashboard\index.html",
    r"C:\Copernico\dashboard\index.html",
    r"C:\Users\JENNER ZUÑIGA\copernico\dashboard\pedagogical_storytelling.html",
    r"C:\Copernico\dashboard\pedagogical_storytelling.html",
    r"C:\Users\JENNER ZUÑIGA\copernico\dashboard\gnss_validation_data.js",
    r"C:\Users\JENNER ZUÑIGA\copernico\dashboard\gnss_validation_data_v3.js",
    r"C:\Users\JENNER ZUÑIGA\copernico\dashboard\gnss_validation_data_v4.js",
    r"C:\Copernico\dashboard\gnss_validation_data.js",
    r"C:\Copernico\dashboard\gnss_validation_data_v3.js",
    r"C:\Copernico\dashboard\gnss_validation_data_v4.js",
    r"C:\Users\JENNER ZUÑIGA\copernico\README.md",
    r"C:\Copernico\README.md"
]

for f in files_to_clean:
    clean_file(f)

# Sincronizar imágenes a C:\Copernico
import shutil
shutil.copy(r"C:\Users\JENNER ZUÑIGA\copernico\dashboard\pedagogical_storytelling.html", r"C:\Copernico\dashboard\pedagogical_storytelling.html")
for img in ["pedagogical_insar_explained.png", "pedagogical_control_experiment.png", "pedagogical_mogi_chamber.png", "pedagogical_validation_status.png"]:
    src = os.path.join(r"C:\Users\JENNER ZUÑIGA\copernico\dashboard\img", img)
    dst = os.path.join(r"C:\Copernico\dashboard\img", img)
    if os.path.exists(src):
        shutil.copy(src, dst)

print("All references cleaned across dashboard and documentation files!")
