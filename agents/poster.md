# Poster Agent

Laeuft Mo–Fr um 9 Uhr UTC. Postet taeglich einen Pinterest-Pin. Reddit nur mittwochs.

## Umgebungsvariablen
- `GITHUB_TOKEN`, `GITHUB_REPO`
- `MAKE_REDDIT_WEBHOOK_URL` — Make.com Webhook für Reddit-Posts
- `PINTEREST_CLIENT_ID`, `PINTEREST_CLIENT_SECRET`, `PINTEREST_REFRESH_TOKEN`

## Schritt 1: Daten laden

```bash
RAW="https://raw.githubusercontent.com/$GITHUB_REPO/main"

CONFIG=$(curl -s "$RAW/config.json")
POSTED=$(curl -s "$RAW/log/posted.json")
TODAY_DOW=$(date +%A | tr '[:upper:]' '[:lower:]')  # monday, tuesday, ...
REDDIT_DAY=$(echo $CONFIG | python3 -c "import sys,json; print(json.load(sys.stdin)['posting_schedule']['reddit_day'])")
POST_REDDIT=$( [ "$TODAY_DOW" = "$REDDIT_DAY" ] && echo "true" || echo "false" )
```

## Schritt 2: Post-Typ bestimmen

### Pinterest-Post (täglich):
1. Produkt mit `ready: true` das am längsten keinen Pinterest-Pin hatte → `content/{id}/posts.json` laden
2. Ersten Pinterest-Post (`platform: "pinterest"`) mit `status: "unused"` wählen; falls keiner → `status: "variation"` mit höchstem Score

### Reddit-Post (nur mittwochs, wenn `POST_REDDIT=true`):
1. Letzten Portfolio-Post in `posted.json` finden. Liegt er >21 Tage zurück → heute Portfolio-Post aus `collection/posts.json`
2. Sonst: Produkt mit `ready: true` das am längsten keinen Reddit-Post hatte → Reddit-Post mit `status: "unused"` wählen

Pinterest- und Reddit-Post dürfen dasselbe Produkt betreffen, müssen es aber nicht.

## Schritt 3: Bild-Rotation

`assets.json` des Produkts laden. Bild wählen das NICHT `last_image_used` entspricht.
Reihenfolge: `editorial-pinterest` → `thumbnail` → `cover` → `cover2` → `cover3`

Bild-URL: `https://raw.githubusercontent.com/$GITHUB_REPO/main/{image-path}`

## Schritt 4: Post-Text anpassen

Minimale Anpassung — Synonyme, Satzstellung. NIEMALS ändern:
- Community-Ton: casual, persönlich, kein Marketing-Speak
- Pricing: "Free to download, support optional"
- CTA: "Happy to answer questions" oder "Feedback welcome"
- Link immer ans Ende
- Keine Superlative, kein "Download now"

## Schritt 5: Pinterest Access Token

```bash
PINTEREST_TOKEN=$(curl -s -X POST "https://api.pinterest.com/v5/oauth/token" \
  -u "$PINTEREST_CLIENT_ID:$PINTEREST_CLIENT_SECRET" \
  -d "grant_type=refresh_token&refresh_token=$PINTEREST_REFRESH_TOKEN" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
```

## Schritt 6: Pinterest Pin

```bash
BOARD_ID=$(echo $CONFIG | python3 -c "import sys,json; print(json.load(sys.stdin)['pinterest_board_id'])")

PIN_RESP=$(curl -s -X POST "https://api.pinterest.com/v5/pins" \
  -H "Authorization: Bearer $PINTEREST_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"{PINTEREST_TITLE}\",
    \"description\": \"{PINTEREST_DESCRIPTION} #notiontemplate #notion #productivity #freetemplate\",
    \"link\": \"{GUMROAD_URL}\",
    \"media_source\": {\"source_type\": \"image_url\", \"url\": \"{IMAGE_URL}\"},
    \"board_id\": \"$BOARD_ID\"
  }")

PIN_ID=$(echo $PIN_RESP | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
```

## Schritt 7: Reddit Post via Make.com Webhook (nur mittwochs)

Nur ausführen wenn `POST_REDDIT=true`:

```bash
if [ "$POST_REDDIT" = "true" ]; then
  REDDIT_RESP=$(curl -s -X POST "$MAKE_REDDIT_WEBHOOK_URL" \
    -H "Content-Type: application/json" \
    -d "{\"title\": \"{REDDIT_TITLE}\", \"body\": \"{REDDIT_BODY}\"}")
  echo "Reddit webhook triggered: $REDDIT_RESP"
  REDDIT_POST_ID="via-make"
else
  echo "Kein Reddit-Post heute (nur mittwochs)"
  REDDIT_POST_ID=null
fi
```

Make.com übernimmt die Authentifizierung und das Posting. Die Response ist `{"accepted": 1}` bei Erfolg.

## Schritt 8: Log-Eintrag schreiben

Neuen Eintrag zu `log/posted.json` hinzufügen (via GitHub API PUT).

Pinterest-Eintrag:
```json
{
  "id": "{pinterest-post-variant-id}",
  "product_id": "{product-id}",
  "type": "pinterest",
  "reddit_post_id": null,
  "pinterest_pin_id": "{PIN_ID}",
  "posted_at": "{ISO_TIMESTAMP}",
  "image_used": "{IMAGE_NAME}",
  "performance_check_due": "{ISO_TIMESTAMP_PLUS_48H}",
  "reddit_score": null,
  "pinterest_repins": null
}
```

Reddit-Eintrag (nur mittwochs, separater Eintrag):
```json
{
  "id": "{reddit-post-variant-id}",
  "product_id": "{product-id}",
  "type": "reddit",
  "reddit_post_id": "via-make",
  "pinterest_pin_id": null,
  "posted_at": "{ISO_TIMESTAMP}",
  "image_used": null,
  "performance_check_due": "{ISO_TIMESTAMP_PLUS_48H}",
  "reddit_score": null,
  "pinterest_repins": null
}
```

## Schritt 9: Post-Status + assets.json aktualisieren

- Pinterest-Post in `content/{id}/posts.json`: `status` → `"used"`, `posted_at` → jetzt, `last_image_used` → Bild-Name
- `assets.json`: `last_image_used` aktualisieren
- Reddit-Post (falls gepostet): `status` → `"used"`, `posted_at` → jetzt

## Schritt 10: Dashboard aktualisieren

`docs/index.html` lesen, "Letzte Posts"-Tabelle mit neuem Eintrag ergänzen, via GitHub API zurückschreiben.
Commit-Message: `chore: update dashboard [skip ci]`
