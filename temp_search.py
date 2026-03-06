with open('research/art_of_exploitation_intro.txt', 'r', encoding='utf-8') as f:
    text = f.read()
    
# Find key phrases
phrases = ['hacking is the art', 'essence of hacking', 'creative problem solving']
for phrase in phrases:
    idx = text.lower().find(phrase)
    if idx > 0:
        print(f'Found "{phrase}" at position {idx}')
        print(text[max(0, idx-100):idx+400])
        print('---')
