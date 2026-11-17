import re
import os

with open('taikry/web/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

print("--- Modals / Overlays / Sheets in index.html ---")
for m in re.finditer(r'id=["\']([^"\']*(?:modal|sheet|dialog|drawer|overlay)[^"\']*)["\']', html, re.I):
    print(m.group(1))

print("\n--- Top bar and Header interactive elements ---")
for m in re.finditer(r'<(?:button|a)[^>]*(?:id=["\']([^"\']+)["\'])?[^>]*onclick=["\']([^"\']+)["\'][^>]*>([\s\S]*?)</(?:button|a)>', html[:html.find('id="mobile-bottom-nav"')]):
    btn_id = m.group(1) or 'no-id'
    onclick = m.group(2)
    inner = re.sub(r'<[^>]+>', ' ', m.group(3)).strip()
    inner = ' '.join(inner.split())[:40]
    print(f"ID: {btn_id:25} | OnClick: {onclick:35} | Text: {inner}")

import re

with open('taikry/web/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

overlays = re.findall(r'id=["\'](tab-pane-[^"\']+)["\']', html)
print('\nFound overlays in index.html:', len(overlays))
for ov in overlays:
    idx = html.find(f'id="{ov}"')
    snippet = html[idx:idx+1500]
    has_close = ('close' in snippet.lower() or 'back to terminal' in snippet.lower() or 'switchNavPane' in snippet or 'toggle' in snippet)
    print(f'  {ov:30}: has close/back? {has_close}')

print("\n--- Inspecting tab-pane-settings ---")
idx = html.find('id="tab-pane-settings"')
if idx != -1:
    print(html[idx:idx+1000])
