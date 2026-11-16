import os

with open(r'C:\Users\JENNER ZUÑIGA\Downloads\generate_pedagogical_dashboard.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = 'DASHBOARD_DIR = "/opt/copernico/dashboard"'
replacement = 'DASHBOARD_DIR = os.environ.get("DASHBOARD_REPO", r"C:\\Users\\JENNER ZUÑIGA\\copernico\\dashboard")'

text = text.replace(target, replacement)

for path in [
    r'C:\Users\JENNER ZUÑIGA\copernico\scripts\generate_pedagogical_dashboard.py',
    r'C:\Copernico\scripts\generate_pedagogical_dashboard.py'
]:
    with open(path, 'w', encoding='utf-8') as out:
        out.write(text)

print("Saved generate_pedagogical_dashboard.py with dynamic paths!")
