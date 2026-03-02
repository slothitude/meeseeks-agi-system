import json

with open('the-crypt/pending-retries.json', 'r') as f:
    data = json.load(f)

# Mark telegram button task as complete
for item in data['pending']:
    if 'TELEGRAM BOT: Add Inline Button Support' in item.get('original_task', ''):
        item['status'] = 'complete'
        item['note'] = 'Completed in main session - inline buttons working via direct Telegram API'
        print(f"Marked {item['session_key'][:20]}... as complete")

with open('the-crypt/pending-retries.json', 'w') as f:
    json.dump(data, f, indent=2)
print('Updated pending-retries.json')
