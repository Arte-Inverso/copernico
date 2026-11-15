import cv2
import numpy as np
import os

# Paths
img_path = r'c:\Copernico\purace_zoom.png'
out_path = r'c:\Copernico\purace_segmented.png'

# Load image
img = cv2.imread(img_path)

if img is not None:
    # Reshape image to a 2D array of pixels
    Z = img.reshape((-1, 3))
    Z = np.float32(Z)

    # Define criteria and apply k-means
    # criteria: (type, max_iter, epsilon)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    K = 4 # Number of clusters (Classes: Ash, Rock, Shadow/Water, Vegetation)
    ret, label, center = cv2.kmeans(Z, K, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

    # Convert back to uint8 and reshape to original image dimensions
    center = np.uint8(center)
    res = center[label.flatten()]
    res2 = res.reshape((img.shape))

    # Save the segmented image
    cv2.imwrite(out_path, res2)
    
    print(f"--- AI Segmentation Completed ---")
    print(f"Segmented image saved to: {out_path}")
    print(f"Clusters used: {K}")
else:
    print(f"Error: Could not load image from {img_path}")
