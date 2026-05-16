"""
Pinterest OAuth2 — manueller Code-Flow.
Ausfuehren: python scripts/setup_pinterest_oauth.py <client_id> <client_secret>
"""
import sys
import urllib.parse
import webbrowser

if len(sys.argv) >= 3:
    client_id     = sys.argv[1].strip()
    client_secret = sys.argv[2].strip()
else:
    client_id     = input("Pinterest App ID: ").strip()
    client_secret = input("Pinterest App Secret Key: ").strip()

REDIRECT_URI = "http://localhost:8080/callback"
SCOPES = "boards:read,boards:write,pins:read,pins:write"

auth_url = (
    f"https://www.pinterest.com/oauth/"
    f"?client_id={client_id}"
    f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
    f"&response_type=code"
    f"&scope={SCOPES}"
)

print("\n=== Pinterest OAuth Setup ===\n")
print("Schritt 1: Oeffne diesen Link im Browser und logge dich ein:\n")
print(auth_url)
print()
webbrowser.open(auth_url)

print("Schritt 2: Nach dem Login wirst du zu localhost:8080/callback weitergeleitet.")
print("Die Seite zeigt einen Fehler (Connection refused) — das ist OK.")
print("Kopiere die URL und fuege sie als drittes Argument ein:\n")
print(f'  python scripts/setup_pinterest_oauth.py {client_id} {client_secret} "DEINE_URL"\n')

if len(sys.argv) >= 4:
    redirect_url = sys.argv[3].strip()
else:
    print("FEHLER: Bitte die Redirect-URL als drittes Argument uebergeben.")
    sys.exit(1)

parsed = urllib.parse.urlparse(redirect_url)
params = urllib.parse.parse_qs(parsed.query)

if "code" not in params:
    print("FEHLER: Kein 'code' Parameter in der URL gefunden.")
    sys.exit(1)

code = params["code"][0]
print(f"\nAuth-Code erhalten: {code[:20]}...")

import urllib.request
import json
import base64

token_url = "https://api.pinterest.com/v5/oauth/token"
data = urllib.parse.urlencode({
    "grant_type": "authorization_code",
    "code": code,
    "redirect_uri": REDIRECT_URI,
}).encode()

credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
req = urllib.request.Request(token_url, data=data, headers={
    "Authorization": f"Basic {credentials}",
    "Content-Type": "application/x-www-form-urlencoded",
})

try:
    with urllib.request.urlopen(req) as resp:
        tokens = json.loads(resp.read())
except urllib.error.HTTPError as e:
    print(f"FEHLER: {e.read().decode()}")
    sys.exit(1)

print(f"\nPinterest OAuth erfolgreich!")
print(f"\nPINTEREST_CLIENT_ID={client_id}")
print(f"PINTEREST_CLIENT_SECRET={client_secret}")
print(f"PINTEREST_REFRESH_TOKEN={tokens.get('refresh_token', 'N/A')}")
print(f"PINTEREST_ACCESS_TOKEN={tokens.get('access_token', 'N/A')}")
