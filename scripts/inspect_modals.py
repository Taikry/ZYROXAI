import re

with open('taikry/web/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

modal_ids = [
    'modal-trade-journal',
    'plans-spec-modal',
    'developer-profile-modal',
    'exness-mt5-bridge-modal',
    'modal-v6-concept-explorer',
    'pair-selector-modal',
    'mobile-more-sheet',
    'tab-pane-portfolio-drawer',
    'tab-pane-macro-drawer'
]

for mid in modal_ids:
    idx = html.find(f'id="{mid}"')
    if idx != -1:
        # Find enclosing tag start
        start = html.rfind('<', 0, idx)
        snippet = html[start:start+400]
        print(f"=== #{mid} ===")
        print(snippet[:350].strip())
        print("...")
