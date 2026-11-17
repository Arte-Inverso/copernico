with open(r'C:\Users\JENNER ZUÑIGA\copernico\dashboard\index.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('id="graphify"')
end_idx = text.find('</section>', idx)
print(text[idx:end_idx+10])
