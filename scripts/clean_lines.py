for path in [
    r'C:\Users\JENNER ZUÑIGA\copernico\scripts\insar_mogi_seismic_inversion_v2.py',
    r'C:\Copernico\scripts\insar_mogi_seismic_inversion_v2.py'
]:
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    skip = False
    for line in lines:
        if '},\n' in line and '"pixel_idx"' in lines[lines.index(line)+1]:
            continue
        new_lines.append(line)
        
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

print("Line cleaned successfully!")
