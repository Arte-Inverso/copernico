import numpy as np
from PIL import Image
import os

def analyze_ndvi(filepath):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    # Open image
    img = Image.open(filepath)
    data = np.array(img)
    
    # Basic info
    print(f"--- NDVI Analysis: {os.path.basename(filepath)} ---")
    print(f"Shape: {data.shape}")
    print(f"Data Type: {data.dtype}")
    
    # Filter out nodata and NaNs
    # GEE exports often use specific nodata or NaNs for clouds/mask
    valid_data = data[~np.isnan(data)]
    valid_data = valid_data[valid_data != 0]
    
    if valid_data.size == 0:
        print("No valid data found in the image.")
        return

    min_val = np.nanmin(valid_data)
    max_val = np.nanmax(valid_data)
    mean_val = np.nanmean(valid_data)
    std_val = np.nanstd(valid_data)

    print(f"Min: {min_val:.4f}")
    print(f"Max: {max_val:.4f}")
    print(f"Mean: {mean_val:.4f}")
    print(f"Std Dev: {std_val:.4f}")

    # Histogram/Classes
    # NDVI Categories:
    # < 0: Water/Snow
    # 0 - 0.2: Soil/Rocks
    # 0.2 - 0.5: Sparse vegetation
    # > 0.5: Dense vegetation/Forest
    
    water = np.sum(valid_data < 0) / valid_data.size * 100
    soil = np.sum((valid_data >= 0) & (valid_data < 0.2)) / valid_data.size * 100
    sparse = np.sum((valid_data >= 0.2) & (valid_data < 0.5)) / valid_data.size * 100
    dense = np.sum(valid_data >= 0.5) / valid_data.size * 100

    print("\n--- Land Cover Estimation (NDVI based) ---")
    print(f"Water/Clouds/Shadows (<0): {water:.2f}%")
    print(f"Bare Soil/Urban (0 - 0.2): {soil:.2f}%")
    print(f"Sparse Vegetation (0.2 - 0.5): {sparse:.2f}%")
    print(f"Dense Vegetation/Forest (>0.5): {dense:.2f}%")

    # Save a preview as PNG for the walkthrough
    # Normalize data for visualization (0-255)
    # Handle NaNs for visualization: replace with -1 (bottom of range)
    viz_data = np.nan_to_num(data, nan=-1.0)
    norm_data = ((viz_data + 1) / 2 * 255).astype(np.uint8)
    preview_img = Image.fromarray(norm_data)
    preview_path = filepath.replace('.tif', '_preview.png')
    preview_img.save(preview_path)
    print(f"\nPreview saved to: {preview_path}")

if __name__ == "__main__":
    analyze_ndvi("Mapa_NDVI_Samanga_2026.tif")
