import urllib.request
import json

resp = urllib.request.urlopen('https://pypi.org/pypi/lancedb/json', timeout=60)
data = json.loads(resp.read().decode())
for url in data['urls']:
    if 'win_amd64' in url['filename'] and 'abi3' in url['filename']:
        print(f"URL: {url['url']}")
        print(f"Filename: {url['filename']}")
        print(f"Size: {url['size'] / 1024 / 1024:.1f} MB")
        break
