# Steam Posting Assistant

A local-first toolkit for collecting and organizing Steam review history, preparing review drafts in a persistent queue, and cataloging artwork files. It keeps account actions under the user's control: review publication is always manual, and the cataloger never modifies source images.

## Features

### Steam review-history downloader
- Opens Steam Community in a persistent Playwright browser profile so the user can sign in manually and reuse the session locally.
- Downloads review-history pages sequentially using page-number URLs.
- Waits for review containers to render and applies delays between requests.
- Saves the retrieved HTML pages locally in `html_pages/` for offline processing.
- Stops when the profile's review history reaches an empty/end-of-history page.

### Review-history CSV compiler
- Reads the locally saved HTML pages in numeric page order.
- Extracts game names, Steam AppIDs, recommendation sentiment, and review text when available.
- Removes duplicate AppIDs and writes a UTF-8 CSV file.
- Reports pages that could not be parsed and preserves successfully extracted records in the output.

### Steam review draft queue
- Reads a private `fila_reviews.csv` queue based on `tools/fila_reviews.example.csv`.
- Opens the specific public Steam Store URL for each AppID; the user confirms whether the correct game page opened.
- Marks invalid AppIDs or pages that fail/redirect to a general Steam page as `UNAVAILABLE` and advances to the next row.
- Saves the current review to `review_atual.txt` and copies the complete title and body to the clipboard.
- Offers three controls after manual publication:
  - **S** — confirm that the user published the review; save `PUBLICADA` and continue.
  - **N** — leave the current row as `DRAFT` and exit.
  - **P** — save the queue, record a pause note, leave the current row as `DRAFT`, and exit.
- Resumes from the first pending `DRAFT` on the next run. Rows marked `PUBLICADA` or `UNAVAILABLE` are not presented again.
- Saves queue updates atomically and creates a local backup before the first update.

The helper does **not** sign in, open or fill a review form, submit, or publish anything on Steam. The user pastes and publishes the review manually, then confirms it with **S**.

### Artwork catalog
- Recursively scans a folder of artwork images.
- Exports file name, relative path, extension, size, SHA-256, and image dimensions when Pillow is installed.
- Identifies byte-identical files by SHA-256.
- Read-only: source images are never moved, renamed, or deleted.

### Graphical launcher
- Provides a Tkinter desktop window with clickable buttons for the scripts found in the project folder.
- Opens interactive tools in separate terminal windows so login prompts and S/N/P choices remain available.
- Includes a folder picker for artwork cataloging and a live process-status indicator.
- Detects optional artwork posting and diagnostic scripts when those files are present.

## Requirements

- Windows 10 or newer is recommended for the included batch launcher and clipboard workflow.
- Python 3.9 or newer.
- For review-history download: Playwright and its Chromium browser.
- For CSV compilation: Beautiful Soup 4.
- For review draft preparation: Tkinter/Tcl-Tk (normally included with the Windows Python installer); no third-party package is required.
- Optional for artwork dimensions: Pillow.

Install the dependencies used by the review-history downloader/compiler:

~~~powershell
py -3 -m pip install playwright beautifulsoup4
py -3 -m playwright install chromium
~~~

Optional image-dimension support:

~~~powershell
py -3 -m pip install Pillow
~~~

Or install Pillow from `requirements-optional.txt`.

## Start the graphical interface

Double-click `iniciar_interface.bat`, or run:

~~~powershell
py -3 launcher_gui.py
~~~

The launcher shows buttons only for scripts available beside it. Interactive scripts open in their own terminal window; the interface remains available to start another tool and display process status.

## Quick start

### 1. Download review-history pages

1. Open `1_baixar_paginas.py` and replace `YOUR_ID_STEAM` in the `STEAM_ID` setting with your Steam profile vanity URL or profile identifier.
2. Run:

~~~powershell
py -3 1_baixar_paginas.py
~~~

3. Sign in to Steam manually in the browser window if necessary.
4. Return to the terminal and press Enter to begin downloading pages.

The persistent browser profile and downloaded HTML files remain local to your computer.

### 2. Compile the downloaded pages

After the download is complete, run:

~~~powershell
py -3 2_criar_csv.py
~~~

The output is `todos_jogos_com_comentarios.csv`.

### 3. Prepare review drafts

1. Copy `tools/fila_reviews.example.csv` to `tools/fila_reviews.csv`.
2. Add your own AppIDs, game names, hours, public Store URLs, review titles, review text, and initial `DRAFT` status.
3. Double-click `tools/postarReview.bat`.

After the script prepares a review, paste the clipboard contents into Steam yourself, publish manually if you choose, and answer **S** only after verifying publication. Use **N** to leave the draft pending and exit, or **P** to save the current queue and pause. On the next run, completed and unavailable rows are skipped.

See [Review preparation guide](docs/REVIEW_PREPARATION.md).

### 4. Catalog artwork

~~~powershell
py -3 src/artwork_catalog.py "C:\path\to\artwork" --output artwork_inventory.csv
~~~

The cataloger does not alter the source images.

## Private files and safety

Keep these files and folders on your own computer. Do not commit them:
- Personal review queues such as `fila_reviews.csv`.
- Generated review text such as `review_atual.txt`.
- Steam browser profiles, cookies, and session data.
- Downloaded HTML pages and personal CSV exports.
- Steam API keys, passwords, session cookies, or other credentials.

The repository's `.gitignore` excludes common local data, generated outputs, and browser state. Review it before committing new files.

## Steam Library CSV exporter (optional, separate project)

If you need a CSV of your owned Steam games, use the separate [Steam Library Exporter](https://github.com/FunnyEntity/steam_library_exporter). It is not bundled here and has its own dependencies, Steam Web API key, and SteamID64 requirements. Your profile and Game details must be public while exporting. Never commit the API key or personal library export.

## Project scope

This is an independent community utility and is not affiliated with, endorsed by, or sponsored by Valve or Steam. Steam and Steam Community are trademarks of Valve Corporation.

The tools are preparation and data-management aids. They do not automate review submission or other account actions on Steam.

## License

MIT. See [LICENSE](LICENSE).
