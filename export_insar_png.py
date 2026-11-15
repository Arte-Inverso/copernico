import numpy as np
import cv2
import os

# Dimensions from BEAM-DIMAP metadata (Stage 2 geocoded)
W, H = 5588, 6627
DATA_DIR = r"c:\Copernico\purace_insar_tc.data"
OUT_DIR = r"c:\Copernico"

def export():
    print(f"Starting FINAL export for {W}x{H} products...")

    # Phase (Interferogram)
    # Using verified geocoded filename with 10.4M valid pixels
    phase_img = os.path.join(DATA_DIR, "phase_ifg_VH.img")
    
    if not os.path.exists(phase_img):
        print(f"ERROR: {phase_img} not found.")
        return

    print("Reading phase data...")
    raw = np.fromfile(phase_img, dtype='<f4')
    img = raw.reshape((H, W))
    
    mask = (img != 0)
    print(f"Phase valid pixels: {np.count_nonzero(mask)}")
    
    # Cyclic Phase mapping (stretch -pi to pi -> 0 to 255)
    norm = np.zeros((H, W), dtype=np.uint8)
    if np.any(mask):
        norm[mask] = (((img[mask] + np.pi) % (2 * np.pi)) / (2 * np.pi) * 255).astype(np.uint8)
    
    # Apply JET colormap for high-contrast fringes (Rainbow: Blue -> Green -> Red)
    colored = cv2.applyColorMap(norm, cv2.COLORMAP_JET)
    
    # Background: Dark Gray (25, 25, 25) to separate from data
    colored[~mask] = [25, 25, 25]
    
    cv2.imwrite(os.path.join(OUT_DIR, "purace_ifg.png"), colored)
    print(f"Interferogram saved to {os.path.join(OUT_DIR, 'purace_ifg.png')}")

    # Coherence
    coh_filename = "coh_IW1_VV_10Mar2026_16Mar2026.img"
    coh_path = os.path.join(DATA_DIR, coh_filename)
    if os.path.exists(coh_path):
        raw = np.fromfile(coh_path, dtype='<f4')
        img = raw.reshape((H, W))
        
        mask = (img > 0)
        out_coh = np.zeros((H, W), dtype=np.uint8)
        if np.any(mask):
            valid_data = img[mask]
            v_min, v_max = valid_data.min(), valid_data.max()
            print(f"Coh Range: {v_min:.4f} - {v_max:.4f}")
            # Manual stretch 0 to 1 -> 0 to 255
            str_coh = ((valid_data - v_min) / (v_max - v_min + 1e-6) * 255).astype(np.uint8)
            out_coh[mask] = str_coh
            
        cv2.imwrite(os.path.join(OUT_DIR, "purace_coh.png"), out_coh)
        print(f"Coherence map saved to {os.path.join(OUT_DIR, 'purace_coh.png')}")

if __name__ == "__main__":
    export()
