import os

files = [
    'research/art_of_exploitation_intro.txt',
    'research/art_of_exploitation_programming.txt'
]

for file in files:
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Find key phrases
        phrases = ['hacking is the art', 'essence of hacking', 'creative problem solving', 'unintended or overlooked']
        for phrase in phrases:
            idx = text.lower().find(phrase)
            if idx > 0:
                print(f'\n=== Found "{phrase}" in {file} ===')
                print(text[max(0, idx-50):idx+300])
                print('---')
