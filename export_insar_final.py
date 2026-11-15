import numpy as np
import cv2
import os

# UUID/Cache-Buster Name
TARGET_NAME = "purace_reliability_v3_final.png"
PHASE_NAME = "purace_ifg_v3_final.png"

# 2x Decimation for stability
W_FULL, H_FULL = 5588, 6627
STEP = 2
W, H = W_FULL // STEP, H_FULL // STEP

COH_SOURCE = r"c:/Copernico/purace_insar_tc_final.data/coh_ifg_VH.img"
IFG_SOURCE = r"c:/Copernico/purace_insar_tc_final.data/phase_ifg_VH.img"
OUT_COH = os.path.join(r"C:\Copernico", TARGET_NAME)
OUT_IFG = os.path.join(r"C:\Copernico", PHASE_NAME)

def force_export():
    print(f"--- CACHE-BUSTING EXPORT ({TARGET_NAME}) ---")
    
    # 1. COHERENCE
    if os.path.exists(COH_SOURCE):
        d = np.fromfile(COH_SOURCE, dtype='<f4')
        if len(d) >= W_FULL * H_FULL:
            arr = d[:W_FULL*H_FULL].reshape((H_FULL, W_FULL))[::STEP, ::STEP][:H, :W]
            mask = (arr > 0) & (~np.isnan(arr))
            if np.any(mask):
                v = arr[mask]
                p2, p98 = np.percentile(v, 2), np.percentile(v, 98)
                norm = np.clip((arr - p2) / (p98 - p2 + 1e-6), 0, 1)
                gamma = np.power(norm, 0.5)
                final = np.zeros((H, W), dtype=np.uint8)
                final[mask] = (gamma[mask] * 255).astype(np.uint8)
                colored = cv2.applyColorMap(final, cv2.COLORMAP_BONE)
                colored[~mask] = [5, 5, 5]
                cv2.imwrite(OUT_COH, colored)
                print(f"SUCCESS: Saved {OUT_COH} ({os.path.getsize(OUT_COH)} bytes)")

    # 2. PHASE
    if os.path.exists(IFG_SOURCE):
        d = np.fromfile(IFG_SOURCE, dtype='<f4')
        if len(d) >= W_FULL * H_FULL:
            arr = d[:W_FULL*H_FULL].reshape((H_FULL, W_FULL))[::STEP, ::STEP][:H, :W]
            mask = (arr != 0)
            if np.any(mask):
                final = np.zeros((H, W), dtype=np.uint8)
                final[mask] = (((arr[mask] + np.pi) % (2 * np.pi)) / (2 * np.pi) * 255).astype(np.uint8)
                colored = cv2.applyColorMap(final, cv2.COLORMAP_JET)
                colored[~mask] = [10, 10, 10]
                cv2.imwrite(OUT_IFG, colored)
                print(f"SUCCESS: Saved {OUT_IFG} ({os.path.getsize(OUT_IFG)} bytes)")

if __name__ == "__main__":
    force_export()
