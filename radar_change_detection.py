import cv2
import numpy as np
import os

# Paths
path1 = r'c:\Copernico\S1A_IW_SLC__1SDV_20260310T105208_20260310T105236_063564_07FCFB_FA9C.SAFE\preview\quick-look.png'
path2 = r'c:\Copernico\S1C_IW_SLC__1SDV_20260316T105045_20260316T105113_006788_00DB83_BEA4.SAFE\preview\quick-look.png'
out_diff = r'c:\Copernico\purace_change_detection.png'

# Load images
img1 = cv2.imread(path1, cv2.IMREAD_GRAYSCALE)
img2 = cv2.imread(path2, cv2.IMREAD_GRAYSCALE)

if img1 is not None and img2 is not None:
    # Ensure they have the same size (they might differ slightly due to processing)
    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    
    # Simple Difference
    diff = cv2.absdiff(img1, img2)
    
    # Enhance difference for visualization
    diff_colored = cv2.applyColorMap(diff, cv2.COLORMAP_HOT)
    
    # Coordinates of Puracé (re-using mapping logic)
    lat_max, lat_min = 4.22, 2.07
    lon_max, lon_min = -75.81, -78.04
    v_lat, v_lon = 2.317, -76.398
    
    h, w = img1.shape
    x_pct = (v_lon - lon_min) / (lon_max - lon_min)
    y_pct = 1.0 - (v_lat - lat_min) / (lat_max - lat_min)
    px, py = int(x_pct * w), int(y_pct * h)
    
    # Zoom into Puracé on the difference map
    crop_size = 400
    x1 = max(0, px - crop_size // 2)
    y1 = max(0, py - crop_size // 2)
    x2 = min(w, px + crop_size // 2)
    y2 = min(h, py + crop_size // 2)
    
    diff_crop = diff_colored[y1:y2, x1:x2]
    
    # Save
    cv2.imwrite(out_diff, diff_crop)
    print(f"--- Radar Change Detection Completed ---")
    print(f"Difference map (Puracé zoom) saved to: {out_diff}")
else:
    print("Error loading one of the radar images.")
