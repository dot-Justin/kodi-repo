# dotJustin's Kodi Repository

Kodi addon repository by dotJustin. Add this repo to Kodi to install and auto-update addons.

## How to Add This Repository to Kodi

**Step 1 — Enable unknown sources**
Settings → System → Add-ons → Unknown sources → On

**Step 2 — Install the repository addon**
1. Settings → Add-ons → Install from zip file
2. Navigate to the downloaded `repository.dotjustin-1.0.0.zip` ([download here](../../releases/latest))
3. Kodi will confirm the repository is installed

**Step 3 — Install addons from the repo**
1. Settings → Add-ons → Install from repository → dotJustin's Kodi Repository
2. Browse and install any addon

Kodi will check this repository for updates automatically.

---

## Addons

| Addon | Description |
|---|---|
| [Bouncer](https://github.com/dot-Justin/Bouncer) | Rating-based playback control. Blocks content by MPAA/TV rating and requires a PIN to continue. |

---

## For Developers (adding a new addon)

1. Drop the addon zip into a subdirectory named after the addon ID: `service.myaddon/service.myaddon-x.y.z.zip`
2. Push to `main` — the GitHub Action regenerates `addons.xml` and `addons.xml.md5` automatically
