"""
Google OAuth Authorization Flow
Authorizes Sloth_rog to access Gmail, Drive, Calendar, YouTube
"""

import json
import webbrowser
import urllib.request
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

# Load OAuth credentials
with open('google_credentials.json', 'r') as f:
    creds = json.load(f)

installed = creds['installed']

# Scopes we need
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/youtube.readonly'
]

# Callback server to receive auth code
auth_code = None

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        
        if 'code' in params:
            auth_code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
                <html><body>
                <h1>Success!</h1>
                <p>Authorization complete. You can close this window.</p>
                <script>setTimeout(function(){window.close();}, 2000);</script>
                </body></html>
            """)
        else:
            self.send_response(400)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Suppress logging

print("=" * 60)
print("GOOGLE OAUTH AUTHORIZATION")
print("=" * 60)
print("\nThis will open your browser to authorize Sloth_rog.")
print("Log in as: slothitudegames@gmail.com")
print("Approve the requested permissions.")
print("\n" + "=" * 60)

# Start local server to receive callback
server = HTTPServer(('localhost', 8080), CallbackHandler)
server_thread = threading.Thread(target=server.handle_request)
server_thread.daemon = True
server_thread.start()

# Build auth URL
auth_url = (
    f"{installed['auth_uri']}?"
    f"client_id={installed['client_id']}&"
    f"redirect_uri=http://localhost:8080&"
    f"response_type=code&"
    f"scope={' '.join(SCOPES)}&"
    f"access_type=offline&"
    f"prompt=consent"
)

print(f"\nOpening browser...")
print(f"If it doesn't open, go to:\n{auth_url[:100]}...\n")

# Open browser
webbrowser.open(auth_url)

# Wait for callback
print("Waiting for authorization...")
timeout = 120  # 2 minutes
start = time.time()
while auth_code is None and (time.time() - start) < timeout:
    time.sleep(0.5)

server.server_close()

if auth_code:
    print("\n[OK] Authorization code received!")
    
    # Exchange code for token
    token_url = installed['token_uri']
    data = urllib.parse.urlencode({
        'code': auth_code,
        'client_id': installed['client_id'],
        'client_secret': installed['client_secret'],
        'redirect_uri': 'http://localhost:8080',
        'grant_type': 'authorization_code'
    })
    
    req = urllib.request.Request(token_url, data.encode())
    with urllib.request.urlopen(req) as response:
        token_data = json.loads(response.read())
    
    # Save token
    with open('google_token.json', 'w') as f:
        json.dump(token_data, f, indent=2)
    
    print("\n" + "=" * 60)
    print("SUCCESS!")
    print("=" * 60)
    print(f"\nAccess Token: {token_data['access_token'][:30]}...")
    print(f"Refresh Token: {token_data['refresh_token'][:30]}...")
    print(f"Expires in: {token_data.get('expires_in', 'unknown')} seconds")
    print(f"\nToken saved to: google_token.json")
    print("\nI now have access to:")
    print("  - Gmail (read, send, compose)")
    print("  - Drive (read, create files)")
    print("  - Calendar (read, write)")
    print("  - YouTube (read)")
    
else:
    print("\n[TIMEOUT] No authorization code received.")
    print("Please try again.")
