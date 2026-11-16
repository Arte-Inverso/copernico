import os, re

html_files = [
    r"C:\Users\JENNER ZUÑIGA\copernico\dashboard\index.html",
    r"C:\Copernico\dashboard\index.html",
    r"C:\Users\JENNER ZUÑIGA\copernico\dashboard\pedagogical_storytelling.html",
    r"C:\Copernico\dashboard\pedagogical_storytelling.html"
]

for h in html_files:
    if os.path.exists(h):
        with open(h, "r", encoding="utf-8") as f:
            content = f.read()

        # Remove the nav item for ficha_tecnica.html
        content = re.sub(r'<li[^>]*ficha_tecnica\.html[^>]*>[\s\S]*?</li>\s*', '', content)
        content = re.sub(r'<a[^>]*ficha_tecnica\.html[^>]*>[\s\S]*?</a>\s*', '', content)

        with open(h, "w", encoding="utf-8") as f:
            f.write(content)

# Remove the file ficha_tecnica.html
files_to_remove = [
    r"C:\Users\JENNER ZUÑIGA\copernico\dashboard\ficha_tecnica.html",
    r"C:\Copernico\dashboard\ficha_tecnica.html",
    r"C:\Geomatica\ficha_tecnica.html"
]

for f in files_to_remove:
    if os.path.exists(f):
        os.remove(f)
        print(f"Removed file: {f}")

print("Successfully removed ficha_tecnica.html and all its references from dashboards!")
