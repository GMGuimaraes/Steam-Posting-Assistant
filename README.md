# Steam Posting Assistant

A local-first toolkit for collecting Steam review history, preparing review drafts, cataloging artwork, and publishing artwork through supervised or automated workflows. A Tkinter desktop launcher provides buttons for the scripts that are present in the project folder.

## Features

### Steam review-history downloader
- Opens Steam Community in a persistent Playwright browser profile so the user can sign in manually.
- Downloads review-history pages sequentially and saves their HTML locally in the html_pages folder.
- Waits for review containers to render and applies delays between requests.
- Stops when it reaches an empty/end-of-history page.

### Review-history CSV compiler
- Reads saved HTML pages in numeric order.
- Extracts game names, Steam AppIDs, recommendation sentiment, and review text when available.
- Removes duplicate AppIDs and exports a UTF-8 CSV.
- Reports pages that could not be parsed while preserving successfully extracted records.

### Steam review draft queue
- Reads a private fila_reviews.csv queue based on tools/fila_reviews.example.csv.
- Opens the specific public Store page for each AppID; the user confirms whether the correct game page loaded.
- Marks invalid or incorrectly redirected pages as UNAVAILABLE and advances to the next row.
- Saves the current review to review_atual.txt and copies the complete title and body to the clipboard.
- Offers three choices after manual publication:
  - **S** — the user confirms publication; save PUBLICADA and continue.
  - **N** — leave the row as DRAFT and exit.
  - **P** — save the queue and a timestamped pause note, leave the row as DRAFT, and exit.
- Resumes at the first pending DRAFT. PUBLICADA and UNAVAILABLE rows are skipped.
- Saves queue changes atomically and creates an initial backup.

The review helper never submits a review. The user pastes and publishes manually and should choose S only after verifying publication.

### Artwork catalog
- Recursively scans a local folder of images.
- Exports filename, relative path, extension, size, SHA-256, and dimensions when Pillow is installed.
- Identifies byte-identical files by SHA-256.
- Read-only: source images are not moved, renamed, or deleted.

### Artwork publishing and diagnostics
- envio/postar_tudo.py uses Playwright to upload artwork to the Steam Community hub selected in the manifest.
- Uses the Community upload action, not the profile-only save action.
- Tracks image hashes and AppIDs in a local history to avoid reposting the same image to the same game.
- Handles errors per target, saves manifest/history updates atomically, and writes logs and diagnostic screenshots/text.
- Tries to like and favorite confirmed uploads.
- Uses a limit of 10 uploads per run, up to 10 targets per image, 2 attempts per target, 120–300 second delays, and at most 5 free-game claims per run.
- If an upload form is unavailable because the game is not owned, it may claim the game only when it is free and passes the script's safety checks. It never buys paid games.
- Automatic deletion of original artwork is disabled; source files are preserved.
- envio/enviar_artwork.py is a supervised alternative: it opens the upload form, attaches the image, fills title/description, and waits for the user to review and publish manually.
- envio/inspecionar_form.py is a read-only diagnostic tool. It saves a screenshot and a list of form elements; it does not publish.

**Authorship warning:** the Steam form may require the uploader to certify that they are the original creator. Set autoria_propria to true only for artwork you created. The assisted mode only leaves the final click to a human; it does not change the meaning of the certification. Permission to repost someone else's work is not the same as being its creator. Do not certify authorship unless it is true.

### Graphical launcher
- launcher_gui.py creates a desktop window with clickable buttons for scripts found in the project folder.
- Interactive scripts open in separate terminal windows so login prompts and S/N/P choices remain available.
- Includes a folder picker for artwork cataloging and a process-status indicator.
- Optional artwork buttons appear only when their scripts and local manifesto.json are present.

## Requirements

- Windows 10 or newer is recommended.
- Python 3.9 or newer.
- Playwright for the browser-based downloader and artwork tools.
- Beautiful Soup 4 for compiling saved review pages.
- Tkinter for the GUI and clipboard support; normally included with the standard Windows Python installer.
- Pillow is optional and only needed for artwork dimensions.

Install required packages:

~~~powershell
py -3 -m pip install -r requirements.txt
py -3 -m playwright install chromium
~~~

Optional image-dimension support:

~~~powershell
py -3 -m pip install -r requirements-optional.txt
~~~

## Quick start

### Start the graphical interface

Double-click iniciar_interface.bat, or run:

~~~powershell
py -3 launcher_gui.py
~~~

### Download review history

1. Set STEAM_ID in 1_baixar_paginas.py to your Steam profile vanity URL or profile identifier.
2. Run:

~~~powershell
py -3 1_baixar_paginas.py
~~~

3. Sign in manually in the browser if necessary, then press Enter in the terminal.

### Compile the review-history CSV

~~~powershell
py -3 2_criar_csv.py
~~~

The output is todos_jogos_com_comentarios.csv.

### Prepare review drafts

1. Copy tools/fila_reviews.example.csv to tools/fila_reviews.csv.
2. Add your own AppIDs, titles, review text, and DRAFT status.
3. Run tools/postarReview.bat.
4. Paste and publish manually; use S only after checking the result.

See docs/REVIEW_PREPARATION.md.

### Catalog artwork

~~~powershell
py -3 src/artwork_catalog.py "C:\path\to\artwork" --output artwork_inventory.csv
~~~

### Publish artwork

1. Copy envio/manifesto.example.json to envio/manifesto.json.
2. Edit the image path, title, description, and target games.
3. Review docs/ARTWORK_PUBLISHING.md before running.
4. Double-click envio/postar.bat for the automated workflow, or run envio/enviar_artwork.py envio/manifesto.json for the supervised workflow.
5. Use envio/inspecionar_form.bat for read-only form diagnostics.

## Private files

Do not commit personal queues, manifesto.json, historico_postados.json, generated review text, downloaded HTML, browser profiles, screenshots, logs, Steam cookies, API keys, passwords, or session tokens. The example manifest is safe to share; the real manifest and posting history remain local. Review .gitignore before committing new files.

## Optional Steam Library CSV exporter

The separate Steam Library Exporter can export an owned-game list, but it is not required by this project. Follow its own README for dependencies, Steam Web API key, SteamID64, and profile privacy requirements. Keep the key and personal library CSV private.

## Project scope

This is an independent community utility and is not affiliated with, endorsed by, or sponsored by Valve or Steam. Follow Steam's current rules. The scripts do not purchase games. Only use artwork you have the right to publish and never make a false authorship certification.

## License

MIT. See LICENSE.
