with open(r'C:\Users\JENNER ZUÑIGA\copernico\dashboard\index.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('id="graphify"')
if idx != -1:
    print(text[idx-100:idx+1500])
else:
    print('Not found')
