for path in [
    r'C:\Users\JENNER ZUÑIGA\copernico\scripts\insar_mogi_seismic_inversion_v2.py',
    r'C:\Copernico\scripts\insar_mogi_seismic_inversion_v2.py'
]:
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    target = '},\n        "pixel_idx": {"row": int(best_i), "col": int(best_j)}\n    }'
    text = text.replace(target, '}')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)

print("Replacement complete without escaping issues!")
