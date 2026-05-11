"""
Einmaliger Reddit OAuth-Flow.
Ausfuehren: python scripts/setup_reddit_oauth.py
"""
import requests
import base64

print("=== Reddit OAuth Setup ===\n")
client_id     = input("Reddit Client ID: ").strip()
client_secret = input("Reddit Client Secret: ").strip()
username      = input("Reddit Username: ").strip()
password      = input("Reddit Password: ").strip()

credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
headers = {
    "Authorization": f"Basic {credentials}",
    "User-Agent": f"tinycraft-poster/1.0 by {username}"
}
data = {
    "grant_type": "password",
    "username": username,
    "password": password,
    "scope": "submit identity"
}

resp = requests.post("https://www.reddit.com/api/v1/access_token", headers=headers, data=data)
resp.raise_for_status()
token_data = resp.json()

if "error" in token_data:
    print(f"\nFEHLER: {token_data}")
else:
    print(f"\n✓ OAuth erfolgreich! Test-Token: {token_data['access_token'][:20]}...")
    print(f"\nFuege folgendes als Claude Code Umgebungsvariablen ein (/config):")
    print(f"\nREDDIT_CLIENT_ID={client_id}")
    print(f"REDDIT_CLIENT_SECRET={client_secret}")
    print(f"REDDIT_USERNAME={username}")
    print(f"REDDIT_PASSWORD={password}")
