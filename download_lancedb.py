import urllib.request
import os
import time

url = "https://files.pythonhosted.org/packages/66/50/bd47bca59a87a88a4ca291a0718291422440750d84b34318048c70a537c2/lancedb-0.29.2-cp39-abi3-win_amd64.whl"
filename = "lancedb-0.29.2-cp39-abi3-win_amd64.whl"

# Download with progress
def download_with_progress(url, filename):
    print(f"Downloading {filename}...")
    
    # Check if partial download exists
    resume_pos = 0
    if os.path.exists(filename):
        resume_pos = os.path.getsize(filename)
        print(f"Resuming from {resume_pos / 1024 / 1024:.1f} MB")
    
    req = urllib.request.Request(url)
    if resume_pos > 0:
        req.add_header('Range', f'bytes={resume_pos}-')
    
    response = urllib.request.urlopen(req, timeout=120)
    total_size = int(response.headers.get('content-length', 0)) + resume_pos
    
    mode = 'ab' if resume_pos > 0 else 'wb'
    with open(filename, mode) as f:
        downloaded = resume_pos
        chunk_size = 8192
        last_print = 0
        while True:
            chunk = response.read(chunk_size)
            if not chunk:
                break
            f.write(chunk)
            downloaded += len(chunk)
            if time.time() - last_print > 2:  # Print every 2 seconds
                pct = (downloaded / total_size * 100) if total_size > 0 else 0
                print(f"Progress: {downloaded / 1024 / 1024:.1f} MB / {total_size / 1024 / 1024:.1f} MB ({pct:.1f}%)")
                last_print = time.time()
    
    print(f"Download complete: {filename}")
    return True

# Retry logic
max_retries = 5
for attempt in range(max_retries):
    try:
        download_with_progress(url, filename)
        break
    except Exception as e:
        print(f"Attempt {attempt + 1} failed: {e}")
        if attempt < max_retries - 1:
            wait_time = (attempt + 1) * 5
            print(f"Waiting {wait_time}s before retry...")
            time.sleep(wait_time)
        else:
            print("All retries failed")
            raise
