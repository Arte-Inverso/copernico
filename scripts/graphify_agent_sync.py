import os, json, glob, datetime

BASE_DIR = os.environ.get("COPERNICO_DIR", r"C:\Users\JENNER ZUÑIGA\copernico")
LOCAL_DOCS_DIR = os.path.join(BASE_DIR, "local_docs")
os.makedirs(LOCAL_DOCS_DIR, exist_ok=True)

def scan_project_state():
    """Escanea el estado del proyecto para mantener Graphify actualizado."""
    scripts = glob.glob(os.path.join(BASE_DIR, "scripts", "*.py")) + glob.glob(os.path.join(BASE_DIR, "*.py"))
    scripts_info = [os.path.basename(s) for s in sorted(scripts)]
    
    # InSAR data check
    insar_js = os.path.join(BASE_DIR, "dashboard", "geophysics_inversion_data.js")
    insar_status = "No disponible"
    mogi_depth = "N/A"
    pova_dist = "N/A"
    if os.path.exists(insar_js):
        try:
            with open(insar_js, "r", encoding="utf-8") as f:
                c = f.read()
                raw = c.replace("var geophysicsInversionData = ", "").rstrip(";\n ")
                d = json.loads(raw)
                mogi_depth = f"{d.get('mogi_inversion', {}).get('depth_km', 'N/A')} km"
                pova_dist = f"{d.get('pova_validation', {}).get('insar_pixel', {}).get('distance_km', 'N/A')} km"
                insar_status = "Activo y Calibrado"
        except:
            pass

    return {
        "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "scripts_count": len(scripts_info),
        "scripts": scripts_info,
        "mogi_depth": mogi_depth,
        "pova_colocation_dist": pova_dist,
        "insar_status": insar_status
    }

def update_local_graphify_knowledge():
    state = scan_project_state()
    
    # 1. Guardar memoria local del agente (NO sube a Git)
    knowledge_file = os.path.join(LOCAL_DOCS_DIR, "agent_graphify_memory.json")
    with open(knowledge_file, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)
        
    # 2. Guardar resumen markdown local
    md_file = os.path.join(LOCAL_DOCS_DIR, "resumen_desarrollo_local.md")
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(f"""# ESTADO DE DESARROLLO Y MEMORIA LOCAL (GRAPHIFY)
Fecha actualización: {state['updated_at']}

## 🛰️ Estado Núcleo Científico
- Estado InSAR: {state['insar_status']}
- Profundidad Cámara Mogi: {state['mogi_depth']}
- Colocalización POVA: {state['pova_colocation_dist']}

## 📜 Scripts Registrados ({state['scripts_count']}):
""" + "\n".join([f"- `{s}`" for s in state['scripts']]))

    print(f"✓ Memoria Graphify actualizada localmente en: {LOCAL_DOCS_DIR}")

if __name__ == "__main__":
    update_local_graphify_knowledge()
