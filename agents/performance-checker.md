# Performance Checker Agent

Laeuft taeglich um 9 Uhr UTC. Prueft Posts die ~48h alt sind und noch kein Score haben.

## Umgebungsvariablen
- `GITHUB_TOKEN`, `GITHUB_REPO`
- `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USERNAME`, `REDDIT_PASSWORD`
- `PINTEREST_CLIENT_ID`, `PINTEREST_CLIENT_SECRET`, `PINTEREST_REFRESH_TOKEN`

## Schritt 1: Faellige Posts finden

```bash
POSTED=$(curl -s "https://raw.githubusercontent.com/$GITHUB_REPO/main/log/posted.json")
```

Filtere Einträge wo `performance_check_due` in der Vergangenheit liegt UND `reddit_score` noch `null` ist.

Wenn keine solchen Einträge → Agent beendet sich ohne weitere Aktion.

## Schritt 2: Reddit Score abrufen

```bash
REDDIT_TOKEN=$(curl -s -X POST "https://www.reddit.com/api/v1/access_token" \
  -u "$REDDIT_CLIENT_ID:$REDDIT_CLIENT_SECRET" \
  -H "User-Agent: tinycraft-poster/1.0 by $REDDIT_USERNAME" \
  -d "grant_type=password&username=$REDDIT_USERNAME&password=$REDDIT_PASSWORD" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

SCORE=$(curl -s \
  -H "Authorization: Bearer $REDDIT_TOKEN" \
  -H "User-Agent: tinycraft-poster/1.0 by $REDDIT_USERNAME" \
  "https://oauth.reddit.com/api/info?id={REDDIT_POST_ID}" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['data']['children'][0]['data']['score'])")
```

## Schritt 3: Pinterest Repins abrufen

```bash
PINTEREST_TOKEN=$(curl -s -X POST "https://api.pinterest.com/v5/oauth/token" \
  -u "$PINTEREST_CLIENT_ID:$PINTEREST_CLIENT_SECRET" \
  -d "grant_type=refresh_token&refresh_token=$PINTEREST_REFRESH_TOKEN" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

START=$(date -d "3 days ago" +%Y-%m-%d)
END=$(date +%Y-%m-%d)

ANALYTICS=$(curl -s \
  "https://api.pinterest.com/v5/pins/{PIN_ID}/analytics?start_date=$START&end_date=$END&metric_types=SAVE" \
  -H "Authorization: Bearer $PINTEREST_TOKEN")

REPINS=$(echo $ANALYTICS | python3 -c "
import sys,json
d=json.load(sys.stdin)
vals=d.get('all',{}).get('daily_metrics',[])
print(sum(v.get('data_status','') == 'READY' and v.get('SAVE',0) or 0 for v in vals))
" 2>/dev/null || echo 0)
```

## Schritt 4: Auswertung

Schwellwerte aus `config.json`:
- **Top-Performer**: Reddit Score > 20 ODER Pinterest Repins > 50
- **Schwach**: Reddit Score < 5 nach 48h
- **Durchschnitt**: alles dazwischen → nur Score speichern

## Schritt 5a: Top-Performer — 2 Variationen generieren

Analysiere was funktioniert hat (Titel-Muster, Einstieg-Typ, Bild).
Generiere 2 neue Post-Varianten:
- Gleicher Kern, anderes Titel-Muster (Problem/Lösung → Persönliche Story oder umgekehrt)
- Gleicher Kern, anderer Body-Einstieg

Zu `content/{product-id}/posts.json` hinzufügen mit:
```json
{
  "id": "{product-id}-r-0X",
  "platform": "reddit",
  "subreddit": "r/Notion",
  "title": "...",
  "body": "...",
  "status": "variation",
  "score": null,
  "posted_at": null,
  "last_image_used": null,
  "variation_of": "{original-post-id}"
}
```

## Schritt 5b: Schwacher Post

```json
"status": "weak",
"avoid_note": "Schwacher Winkel: [kurze Analyse was nicht funktioniert hat]"
```

## Schritt 6: Log aktualisieren

`log/posted.json` via GitHub API: `reddit_score` und `pinterest_repins` eintragen.

## Schritt 7: Dashboard aktualisieren

Performance-Werte in `docs/index.html` aktualisieren. Commit: `chore: update performance data [skip ci]`
