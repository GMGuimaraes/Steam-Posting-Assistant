# Steam Posting Assistant

**Um conjunto de ferramentas locais para organizar dados da Steam e apoiar fluxos de trabalho com reviews e artworks.** O projeto reúne exportação do histórico de reviews, conversão dos dados para CSV, preparação de rascunhos, catalogação de imagens e ferramentas de envio de artworks. Uma interface Tkinter centraliza os utilitários disponíveis na pasta do projeto.

O foco é manter os dados e a sessão no computador do usuário, com arquivos de exemplo no repositório e dados pessoais gerados localmente.

> **Uso responsável:** confira os dados e o texto antes de publicar. Reviews devem refletir sua experiência real. Para artworks, respeite os direitos do autor e nunca declare autoria se você não for o criador original.

## Features

### Steam review-history downloader
- Opens Steam Community in a persistent Playwright browser profile so the user can sign in manually.
- Downloads review-history pages sequentially and saves their HTML locally in the `html_pages` folder.
- Waits for review containers to render and applies delays between requests.
- Stops when it reaches an empty/end-of-history page.

### Review-history CSV compiler
- Reads saved HTML pages in numeric order.
- Extracts game names, Steam AppIDs, recommendation sentiment, and review text when available.
- Removes duplicate AppIDs and exports a UTF-8 CSV.
- Reports pages that could not be parsed while preserving successfully extracted records.

### Steam review draft queue
- Reads a private `fila_reviews.csv` queue based on `tools/fila_reviews.example.csv`.
- The queue workflow can open the Store page for each AppID and lets the user review the target game and draft.
- The manual queue helper supports the **S / N / P** choices to confirm a completed publication, leave a draft pending, or pause and resume later.
- Review text should be written or checked by the account owner and must accurately reflect their own experience.

**Automation warning:** the legacy `envio/preparar_review.py` uses PyAutoGUI to interact with the browser and can press the publication controls. It depends on window focus, screen layout, and tab order, so it is not a reliable substitute for checking the page yourself. Review every field and the target game before allowing it to continue. Do not publish generic or invented reviews as if they described a real play experience.

### Artwork catalog
- Recursively scans a local folder of images.
- Exports filename, relative path, extension, size, SHA-256, and dimensions when Pillow is installed.
- Identifies byte-identical files by SHA-256.
- Read-only: source images are not moved, renamed, or deleted.

### Artwork publishing and diagnostics
- `envio/postar_tudo.py` uses Playwright to upload artwork to the Steam Community hub selected in the manifest.
- Uses the Community upload action, not the profile-only save action.
- Tracks image hashes and AppIDs in a local history to avoid reposting the same image to the same game.
- Handles errors per target, saves manifest/history updates atomically, and writes logs and diagnostic screenshots/text.
- Tries to like and favorite confirmed uploads.
- Uses a limit of 10 uploads per run, up to 10 targets per image, 2 attempts per target, 120–300 second delays, and at most 5 free-game claims per run.
- If an upload form is unavailable because the game is not owned, it may claim the game only when it is free and passes the script's safety checks. It never buys paid games.
- Automatic deletion of original artwork is disabled; source files are preserved.
- `envio/enviar_artwork.py` is a supervised alternative: it opens the upload form, attaches the image, fills title/description, and waits for the user to review and publish manually.
- `envio/inspecionar_form.py` is a read-only diagnostic tool. It saves a screenshot and a list of form elements; it does not publish.

**Authorship warning:** the Steam form may require the uploader to certify that they are the original creator. Set `autoria_propria` to `true` only for artwork you created. The assisted mode only leaves the final click to a human; it does not change the meaning of the certification. Permission to repost someone else's work is not the same as being its creator. Do not certify authorship unless it is true.

### Graphical launcher
- `launcher_gui.py` creates a desktop window with clickable buttons for scripts found in the project folder.
- Interactive scripts open in separate terminal windows so login prompts and S/N/P choices remain available.
- Includes a folder picker for artwork cataloging and a process-status indicator.
- Optional artwork buttons appear only when their scripts and local `manifesto.json` are present.

## Requirements

- Windows 10 or newer is recommended.
- Python 3.9 or newer.
- Playwright for the browser-based downloader and artwork tools.
- Beautiful Soup 4 for compiling saved review pages.
- Tkinter for the GUI; normally included with the standard Windows Python installer.
- Pillow is optional and only needed for artwork dimensions.
- PyAutoGUI and Pyperclip are optional and are needed only by the legacy review-automation helper.

Install required packages:

~~~powershell
py -3 -m pip install -r requirements.txt
py -3 -m playwright install chromium
~~~

Install optional tools:

~~~powershell
py -3 -m pip install -r requirements-optional.txt
~~~

## Quick start

### Start the graphical interface

Double-click `iniciar_interface.bat`, or run:

~~~powershell
py -3 launcher_gui.py
~~~

### Download review history

1. Open `1_baixar_paginas.py` and set `STEAM_ID` to the **custom profile name** from your public Steam profile URL, for example the part after `/id/` in `https://steamcommunity.com/id/your-profile-name/`.
2. The downloader uses the `/id/` URL format. If your profile only has a numeric SteamID64 URL under `/profiles/`, set up a custom profile URL first or adapt the URL format before running the script.
3. Run:

~~~powershell
py -3 1_baixar_paginas.py
~~~

4. Sign in manually in the browser if necessary, complete Steam Guard yourself, then press Enter in the terminal.
5. The HTML pages are saved locally in `html_pages/`.

Do not put a password, Steam Guard code, cookie, API key, or session token in the script. The persistent browser profile stores session data on the computer; do not share or commit that folder.

### Compile the review-history CSV

After the download finishes, run:

~~~powershell
py -3 2_criar_csv.py
~~~

The output is `todos_jogos_com_comentarios.csv` in the project root. It contains the game name, AppID, recommendation sentiment, and review text extracted from the saved pages. This is an export of the existing review history; it is not automatically a queue for publishing new reviews.

### Prepare review drafts

1. Copy `tools/fila_reviews.example.csv` to `tools/fila_reviews.csv`.
2. Add your own AppIDs, titles, review text, and `DRAFT` status.
3. Run `tools/postarReview.bat`.
4. Check the target game and the full review text before publishing. Use the confirmation choice only after verifying the result.

See `docs/REVIEW_PREPARATION.md`.

### Catalog artwork

~~~powershell
py -3 src/artwork_catalog.py "C:\path\to\artwork" --output artwork_inventory.csv
~~~

### Publish artwork

1. Copy `envio/manifesto.example.json` to `envio/manifesto.json`.
2. Edit the image path, title, description, and target games.
3. Review `docs/ARTWORK_PUBLISHING.md` before running.
4. Double-click `envio/postar.bat` for the automated workflow, or run `envio/enviar_artwork.py envio/manifesto.json` for the supervised workflow.
5. Use `envio/inspecionar_form.bat` for read-only form diagnostics.

## Private files

Do not commit personal queues, `manifesto.json`, `historico_postados.json`, generated review text, downloaded HTML, browser profiles, screenshots, logs, Steam cookies, API keys, passwords, or session tokens. The example manifest is safe to share; the real manifest and posting history remain local. Review `.gitignore` before committing new files.

## Optional Steam Library CSV exporter

The separate Steam Library Exporter can export an owned-game list, but it is not required by this project. Follow its own README for dependencies, Steam Web API key, SteamID64, and profile privacy requirements. Keep the key and personal library CSV private.

## Project scope

This is an independent community utility and is not affiliated with, endorsed by, or sponsored by Valve or Steam. Follow Steam's current rules. The scripts do not purchase games. Only use artwork you have the right to publish and never make a false authorship certification.

## License

MIT. See `LICENSE`.
