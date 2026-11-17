import os
import re

files = [
    'src/components/Navbar.tsx',
    'src/components/HeroSection.tsx',
    'src/components/MarketSection.tsx',
    'src/components/TerminalModal.tsx',
    'src/components/AuthModal.tsx'
]

for fp in files:
    if os.path.exists(fp):
        with open(fp, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"=== {fp} ({len(content)} chars) ===")
        # check for hidden classes
        hiddens = re.findall(r'(?:hidden|block|flex|grid)\s+(?:sm:|md:|lg:|xl:)[^\s"\'`]+', content)
        print("Responsive classes:", set(hiddens[:10]))
