with open('taikry/web/styles.css', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if 'mobile-more' in line:
        for j in range(max(0, i-2), min(i+30, len(lines))):
            print(f'{j+1}: {lines[j].rstrip()}')
        break
