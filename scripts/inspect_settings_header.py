with open('taikry/web/index.html', 'r', encoding='utf-8') as f:
    text = f.read()
idx = text.find('id="tab-pane-settings"')
print(text[idx:idx+2000])
