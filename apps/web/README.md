# journal web app

Browser client for the journal sync server. Vanilla JS, no build step.

## Point it at a server

The app reads `journal` from `localStorage`. To change the API base, click
"server" in the sidebar and set `https://your-host` (default
`http://127.0.0.1:8000`).

## Run locally

```bash
# serve the static files
python3 -m http.server 8080 --directory .
# and keep the server running on :8000
```

Then open <http://127.0.0.1:8080>.

## Features

- Register / login with the sync server (JWT stored in `localStorage`).
- Add, edit (inline) and delete entries — delete asks for confirmation.
- Entries grouped by day with "today"/"yesterday" labels.
- Real-time: connected clients see new entries instantly over WebSocket,
  with automatic reconnect (exponential backoff).
- Works offline after load (entries buffered in memory, sync on next write).
- Character counter, loading states, toast feedback.

## Deploy

Copy the directory to any static host (GitHub Pages, Netlify, ...). The
browser talks straight to the API; configure `JOURNAL_CORS_ORIGINS` on the
server to allow your origin.
