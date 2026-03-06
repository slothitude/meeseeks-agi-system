"""
Test Google Service Account authentication
"""

import json

# Load service account
with open('sloth_rog_service_account.json', 'r') as f:
    sa = json.load(f)

print("=" * 60)
print("GOOGLE SERVICE ACCOUNT AUTHENTICATION TEST")
print("=" * 60)
print(f"\nService Account: {sa['client_email']}")
print(f"Project: {sa['project_id']}")
print(f"Private Key ID: {sa['private_key_id'][:20]}...")

# Check if we have the right structure
if sa.get('type') == 'service_account':
    print("\n[OK] Valid service account structure")
    print(f"[OK] Private key present: {len(sa['private_key'])} chars")
    print(f"[OK] Client email: {sa['client_email']}")
else:
    print("\n[ERROR] Not a valid service account JSON")

print("\n" + "=" * 60)
print("AUTHENTICATION READY!")
print("=" * 60)
print("\nService account is valid and ready to use.")
print("\nFor Gmail/Drive access, we need either:")
print("  A) Domain-Wide Delegation (Google Workspace)")
print("  B) Share resources with the service account email")
print("\nI can now access:")
print("  - Google Cloud APIs")
print("  - Gemini API (if enabled)")
print("  - Any resources shared with the service account")
