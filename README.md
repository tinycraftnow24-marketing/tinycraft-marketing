# Tinycraft Marketing System

Automatisiertes Marketing für Notion-Templates auf Gumroad.
Claude generiert Content und verwaltet die Queue. Make.com postet mechanisch täglich.

---

## Wie das System funktioniert

```
Notion-Template fertig
       ↓
Tinycraft-Marketing: Dateien anlegen (config, content, images)
       ↓
GitHub Push → GitHub Action rendert HTML-Designs → PNGs erscheinen
       ↓
Queue befüllen: Pinterest-Posts + Reddit-Posts als JSON-Dateien
       ↓
Make.com liest täglich 001.json → postet → löscht die Datei
```

**Posting-Rhythmus:** Mo–Fr 9:00 UTC Pinterest-Pin · Mi 9:00 UTC Reddit-Post

**Preisregel:** Solange alle Templates auf Gumroad auf Free stehen → kein Preis nennen. Formulierung: "Free to download" oder "It's free — just thought I'd share it here."

---

## Dateistruktur — ein Template, alle Dateien

```
config.json                          ← Produkt-Registry (hier eintragen)
content/{product-id}/
  posts.json                         ← alle Post-Varianten (Reddit + Pinterest)
  assets.json                        ← Bildpfade und Rotations-Status
images/{product-id}/
  thumbnail.html                     ← Quadratisches Bild 600×600 (Gumroad + Thumbnail)
  thumbnail.png                      ← gerendert von GitHub Action
  editorial-pinterest.html           ← Pinterest-Bild 1000×1500
  editorial-pinterest.png            ← gerendert von GitHub Action
queue/pinterest/
  001.json … NNN.json                ← aktuelle Pinterest-Queue (Make.com liest 001.json)
queue/reddit/
  001.json … NNN.json                ← aktuelle Reddit-Queue (Make.com liest 001.json)
log/posted.json                      ← Historie aller Posts
agents/poster.md                     ← Anleitung für Claude als Poster-Agent
agents/image-builder.md              ← Anleitung für Claude als Image-Builder-Agent
```

---

## Neues Template hinzufügen — Schritt für Schritt

### 1. Template-ID festlegen
Format: `notion-{name}` z.B. `notion-time-tracker`
Diese ID wird überall verwendet — konsistent halten.

### 2. config.json erweitern
In das `products`-Array eintragen:
```json
{
  "id": "notion-time-tracker",
  "name": "Notion Time Tracker",
  "gumroad_url": "https://tinycraft.gumroad.com/l/XXXXX",
  "ready": true,
  "premium": false,
  "platforms": ["reddit", "pinterest"],
  "subreddit": "r/Notion",
  "source_path": "content/notion-time-tracker"
}
```
`ready: false` bis Gumroad-Link + Bilder da sind.

### 3. content/{product-id}/posts.json anlegen
Mindestens 3 Reddit-Posts und 3 Pinterest-Posts. Schema:
```json
[
  {
    "id": "notion-time-tracker-r-01",
    "platform": "reddit",
    "subreddit": "r/Notion",
    "title": "...",
    "body": "...",
    "status": "unused",
    "score": null,
    "posted_at": null,
    "last_image_used": null
  },
  {
    "id": "notion-time-tracker-p-01",
    "platform": "pinterest",
    "title": "...",
    "description": "...",
    "status": "unused",
    "score": null,
    "posted_at": null,
    "last_image_used": null
  }
]
```

### 4. content/{product-id}/assets.json anlegen
```json
{
  "product_id": "notion-time-tracker",
  "images": [
    {"name": "editorial-pinterest", "path": "images/notion-time-tracker/editorial-pinterest.png", "format": "pinterest"},
    {"name": "thumbnail", "path": "images/notion-time-tracker/thumbnail.png", "format": "thumbnail"}
  ],
  "last_image_used": null,
  "last_updated": "2026-XX-XX"
}
```

### 5. Bilder generieren (via Claude)
Claude schreibt `images/{product-id}/editorial-pinterest.html` und `thumbnail.html`.
Nach GitHub-Push rendert die GitHub Action diese automatisch zu PNGs.

**Design-Spec (für Claude):**
- Pinterest: 1000×1500px, dunkler Hintergrund `linear-gradient(135deg, #0f0f0f, #1a1a2e)`
- Headline: 88px bold, stärkstes Benefit, ein Begriff in `#6366f1` (Indigo)
- Brand: "Tinycraft" oben klein, Buchstabenabstand 4px, uppercase, Opacity 40%
- CTA unten: "Free to download · Pay what you want", Opacity 60%
- Thumbnail: 600×600px, gleiches Design, Headline 42px zentriert
- Referenz: `images/style-reference.html`

### 6. Queue befüllen
Neue Einträge ans Ende der Queue stellen (nächste freie Nummer):

**Pinterest:** `queue/pinterest/NNN.json`
```json
{
  "post_id": "notion-time-tracker-p-01",
  "product_id": "notion-time-tracker",
  "title": "...",
  "description": "... #notiontemplate #notion #productivity #freetemplate",
  "image_url": "https://raw.githubusercontent.com/tinycraftnow24-marketing/tinycraft-marketing/main/images/notion-time-tracker/thumbnail.png",
  "gumroad_url": "https://tinycraft.gumroad.com/l/XXXXX"
}
```

**Reddit:** `queue/reddit/NNN.json`
```json
{
  "post_id": "notion-time-tracker-r-01",
  "product_id": "notion-time-tracker",
  "title": "...",
  "body": "..."
}
```

### 7. Alles committen und pushen
```bash
git add config.json content/notion-time-tracker/ images/notion-time-tracker/ queue/
git commit -m "feat: add notion-time-tracker"
git push
```

GitHub Action läuft automatisch und rendert die PNGs innerhalb 1–2 Minuten.

---

## Post-Typen & Varianten

| Variante | Beschreibung |
|----------|-------------|
| `p-01`   | Tool-Übersicht — zeigt alle Datenbanken/Features |
| `p-02`   | Feature-Fokus — ein konkretes Use-Case oder Feature |
| `p-03`   | Ergebnis/Social-Proof — "was es mir gebracht hat" |
| `r-01`   | Persönliche Geschichte + Features + Gumroad-Link |
| `r-02`   | Andere Perspektive / anderer Einstieg |

Reddit-Posts: immer casual, persönlich, kein Marketing-Speak.
Pinterest-Posts: kurze Beschreibung + 4–5 Hashtags.

---

## Bild-Design (Pinterest Editorial)

Das Pinterest-Bild (`editorial-pinterest.html`) folgt immer diesem Aufbau:

```
┌─────────────────────────────────────┐
│ TINYCRAFT              (klein, grau) │  ← Brand oben
│                                     │
│                                     │
│  Hauptheadline                      │  ← 88px, bold, weiß
│  mit einem Wort                     │     ein Begriff in Indigo #6366f1
│  in Farbe.                          │
│                                     │
│  [Screenshot/Mockup]                │  ← leicht rotiert, Schatten
│                                     │
│                                     │
│ Free to download · Pay what you     │  ← CTA unten, grau
│ want                                │
└─────────────────────────────────────┘
1000 × 1500 px — dunkler Hintergrund (#0f0f0f → #1a1a2e)
```

**Beispiel-Headlines:**
- "Build the habit. *Keep the streak.*"
- "Every idea. *One place.*"
- "Know your money. *Keep your data.*"
- "Track every hour. *Own your time.*"

---

## Queue-Verwaltung

Make.com liest immer `queue/pinterest/001.json` und `queue/reddit/001.json`.
Nach erfolgreichem Post löscht Make.com die Datei via GitHub API DELETE — alle anderen rücken NICHT automatisch vor. Die Dateien müssen korrekt nummeriert sein.

**Wenn die Queue leer wird (< 3 Dateien):** Claude-Session starten und den Queue-Prompt nutzen (siehe unten).

**Aktuelle Queue-Kapazität:**
- Pinterest: 8 Posts → reicht ca. 8 Wochen (1×/Woche pro Produkt)
- Reddit: 10 Posts → reicht ca. 10 Wochen

---

## Prompts für neue Claude-Code-Sessions

### PROMPT A — Neues Template komplett einrichten
```
Ich habe ein neues Notion-Template fertig: [NAME].
Gumroad-URL: [URL]
Gumroad-Produkt-ID: [ID aus der URL, z.B. "yxvmey"]

Bitte richte alles ein im Verzeichnis C:\Projekte\tinycraft-marketing:
1. Produkt in config.json eintragen (ready: true, subreddit: r/Notion)
2. content/notion-[name]/posts.json mit 3 Reddit-Posts (r-01, r-02, r-03) und 3 Pinterest-Posts (p-01, p-02, p-03) erstellen — casual, persönlich, kein Marketing-Speak, keine Preisangaben (Templates sind kostenlos)
3. content/notion-[name]/assets.json anlegen
4. images/notion-[name]/editorial-pinterest.html und thumbnail.html im etablierten Tinycraft-Stil generieren (Referenz: images/style-reference.html)
5. Neuen Pinterest-Post als nächste Datei in queue/pinterest/ einfügen (p-01)
6. Neuen Reddit-Post als nächste Datei in queue/reddit/ einfügen (r-01)
7. Alles committen und nach GitHub pushen

Bestehende Produkte als Referenz: content/notion-habit-tracker/
```

### PROMPT B — Queue nachfüllen
```
Bitte fülle die Marketing-Queue für C:\Projekte\tinycraft-marketing nach.

Prüfe:
- Wie viele Dateien liegen in queue/pinterest/ und queue/reddit/?
- Welche Produkte haben noch ungenutzte Post-Varianten in posts.json (status: "unused")?
- Welche Produkte sind in der Queue unterrepräsentiert?

Dann:
1. Neue Queue-Einträge für Pinterest aus ungenutzten p-02/p-03 Varianten erstellen
2. Neue Queue-Einträge für Reddit aus ungenutzten r-02/r-03 Varianten erstellen
3. Falls ein Produkt keine weiteren Varianten hat: neue Post-Variante in posts.json schreiben UND als Queue-Eintrag anlegen
4. Alles committen und pushen

Regeln: Keine Preisangaben. Casual-Ton. Gumroad-Links aus config.json.
```

### PROMPT C — Neue Bilder für ein Produkt
```
Bitte erstelle die HTML-Designdateien für [PRODUCT-ID] in C:\Projekte\tinycraft-marketing.

Lies die Stil-Referenz unter images/style-reference.html.
Erstelle:
- images/[PRODUCT-ID]/editorial-pinterest.html (1000×1500px, Pinterest-Format)
- images/[PRODUCT-ID]/thumbnail.html (600×600px, quadratisch)

Das stärkste Benefit des Templates: [KURZE BESCHREIBUNG]
Schlüsselbegriff für Indigo-Hervorhebung: [WORT]

Nach dem Push rendert die GitHub Action die PNGs automatisch.
```

### PROMPT D — Performance prüfen und Top-Posts identifizieren
```
Prüfe den Performance-Status in C:\Projekte\tinycraft-marketing.

Lies log/posted.json und identifiziere:
- Posts die performance_check_due überschritten haben
- Reddit-Posts mit > 20 Upvotes (Top-Performer)
- Pinterest-Posts mit > 50 Repins (Top-Performer)

Falls Top-Performer gefunden:
- Titel/Text leicht variieren
- Als neue p-0X / r-0X Variante in posts.json des Produkts eintragen
- Als nächste Queue-Datei in queue/pinterest/ oder queue/reddit/ anlegen

Dann committen und pushen.
```

---

## Technische Details

| Variable | Wo gesetzt |
|----------|-----------|
| GITHUB_TOKEN | ~/.claude/settings.json env |
| GITHUB_REPO | `tinycraftnow24-marketing/tinycraft-marketing` |
| MAKE_REDDIT_WEBHOOK_URL | ~/.claude/settings.json env |
| PINTEREST_CLIENT_ID | ~/.claude/settings.json env |
| PINTEREST_CLIENT_SECRET | ~/.claude/settings.json env |
| PINTEREST_REFRESH_TOKEN | ~/.claude/settings.json env |

Pinterest Board: `https://de.pinterest.com/tinycraftnow24/free-notion-templates-setups/`
Board-ID: `1133640606143313391`

Make.com-Szenarien:
- **Daily Pinterest Poster:** Läuft Mo–Fr 9:00 UTC · liest `queue/pinterest/001.json` · postet · löscht Datei
- **Wednesday Reddit Poster:** Läuft Mi 9:00 UTC · liest `queue/reddit/001.json` · sendet an Webhook · löscht Datei

---

## Bestehende Produkte (Stand Mai 2026)

| Produkt | ID | Status |
|---------|-----|--------|
| Habit Tracker | notion-habit-tracker | live |
| Weekly Planner | notion-weekly-planner | live |
| Personal Finance | notion-personal-finance | live |
| Job Tracker | notion-job-tracker | live |
| Product Roadmap | notion-product-roadmap | live |
| Book Tracker | notion-book-tracker | live |
| Content Calendar | notion-content-calendar | live |
| Freelancer Dashboard | notion-freelancer-dashboard | live |
| Second Brain (PARA) | notion-second-brain | live |
| Agency OS | notion-agency-os | live |
