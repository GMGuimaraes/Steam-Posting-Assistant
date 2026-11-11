# Usage guide

## 1. Install dependencies

The project uses Python 3.9 or newer.

For Steam review-history download and compilation:

~~~powershell
py -3 -m pip install playwright beautifulsoup4
py -3 -m playwright install chromium
~~~

The review draft helper uses Python standard-library modules. Tkinter/Tcl-Tk is required for automatic clipboard copying and is normally included in the Windows Python installer.

Optional image-dimension support for the artwork cataloger:

~~~powershell
py -3 -m pip install -r requirements-optional.txt
~~~

This installs Pillow. Without Pillow, the cataloger still scans image files and calculates hashes, but width and height remain blank.

## 2. Download Steam review history

1. Edit the \`STEAM_ID\` setting in \`1_baixar_paginas.py\` and replace \`YOUR_ID_STEAM\` with your profile vanity URL or profile identifier.
2. Run:

~~~powershell
py -3 1_baixar_paginas.py
~~~

3. Sign in manually in the Playwright browser if necessary.
4. Return to the terminal and press Enter to start sequential page downloads.

The script uses a persistent local browser profile and stores downloaded pages in \`html_pages/\`. Keep both private.

## 3. Compile review history to CSV

After the HTML download finishes:

~~~powershell
py -3 2_criar_csv.py
~~~

The compiler reads pages in numeric order, attempts to extract game title, AppID, sentiment, and review text, removes duplicate AppIDs, and writes \`todos_jogos_com_comentarios.csv\`.

The parser depends on Steam's page markup and may report pages where no supported review structure was found.

## 4. Prepare individual review drafts

See [Review preparation guide](REVIEW_PREPARATION.md).

In short:

1. Copy \`tools/fila_reviews.example.csv\` to \`tools/fila_reviews.csv\`.
2. Fill it with your own review data and mark pending rows as \`DRAFT\`.
3. Run \`tools/postarReview.bat\`.
4. Paste and publish manually. Use **S** only after confirming publication; **N** leaves the row pending and exits; **P** saves the queue and pauses.
5. Later runs skip rows marked \`PUBLICADA\` or \`UNAVAILABLE\`.

The helper does not submit reviews or verify publication automatically.

## 5. Catalog artwork

Run:

~~~powershell
py -3 src/artwork_catalog.py "C:\path\to\artwork" --output artwork_inventory.csv
~~~

Recursive scanning is enabled by default. Use \`--no-recursive\` to scan only the selected folder.

The generated inventory contains file name, relative path, extension, size, SHA-256, optional width and height, and a duplicate reference when matching hashes are found. Source images are never changed.

## 6. Optional Steam Library CSV export

The Steam game-library CSV is separate from the review-history CSV and artwork inventory. To export your owned games, use the third-party [Steam Library Exporter](https://github.com/FunnyEntity/steam_library_exporter).

It has its own requirements, including Python 3.11 or newer, its own dependencies, a Steam Web API key, and your SteamID64. Your Steam profile and Game details must be public while exporting. Keep the API key and personal library export private.

## 7. Privacy checklist

Do not upload:
- Personal review queues or game-library CSVs.
- Generated review text or downloaded HTML pages.
- Browser profiles, cookies, or session files.
- Passwords, API keys, session tokens, or other credentials.

Review the repository's \`.gitignore\` before committing files.
