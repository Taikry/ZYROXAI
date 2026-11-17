with open('taikry/web/app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if 'function closeMobileMoreSheet' in line or 'function toggleMobileMoreSheet' in line:
        for j in range(max(0, i-2), min(i+25, len(lines))):
            print(f'{j+1}: {lines[j].rstrip()}')
