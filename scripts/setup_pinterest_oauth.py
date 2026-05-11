"""
Einmaliger Pinterest OAuth2 Authorization Code Flow.
Oeffnet Browser fuer Login, dann lokaler Callback.
Ausfuehren: python scripts/setup_pinterest_oauth.py
"""
import requests
import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

REDIRECT_URI = "http://localhost:8080/callback"
SCOPES = "boards:read,boards:write,pins:read,pins:write"

print("=== Pinterest OAuth Setup ===\n")
client_id     = input("Pinterest App ID: ").strip()
client_secret = input("Pinterest App Secret Key: ").strip()

auth_code_holder = {}

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        if "code" in params:
            auth_code_holder["code"] = params["code"][0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Auth erfolgreich! Du kannst dieses Fenster schliessen.")
        else:
            self.send_response(400)
            self.end_headers()
    def log_message(self, *args):
        pass

server = HTTPServer(("localhost", 8080), CallbackHandler)
thread = threading.Thread(target=server.handle_request)
thread.start()

auth_url = (
    f"https://www.pinterest.com/oauth/"
    f"?client_id={client_id}"
    f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
    f"&response_type=code"
    f"&scope={SCOPES}"
)
print(f"\nBrowser wird geöffnet für Pinterest-Login...")
webbrowser.open(auth_url)
thread.join(timeout=120)

if "code" not in auth_code_holder:
    print("FEHLER: Kein Auth-Code empfangen (Timeout 120s).")
    exit(1)

resp = requests.post(
    "https://api.pinterest.com/v5/oauth/token",
    data={
        "grant_type": "authorization_code",
        "code": auth_code_holder["code"],
        "redirect_uri": REDIRECT_URI,
    },
    auth=(client_id, client_secret),
)
resp.raise_for_status()
tokens = resp.json()

print(f"\n✓ Pinterest OAuth erfolgreich!")
print(f"\nFuege folgendes als Claude Code Umgebungsvariablen ein (/config):")
print(f"\nPINTEREST_CLIENT_ID={client_id}")
print(f"PINTEREST_CLIENT_SECRET={client_secret}")
print(f"PINTEREST_REFRESH_TOKEN={tokens['refresh_token']}")
