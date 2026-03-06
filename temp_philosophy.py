with open('research/art_of_exploitation_programming.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Find the introduction section
idx = text.lower().find('essence of hacking')
if idx > 0:
    # Get surrounding context (2000 chars before, 2000 after)
    context = text[max(0, idx-2000):idx+2000]
    print("=== HACKING PHILOSOPHY FROM BOOK ===\n")
    print(context)
