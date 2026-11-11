# Steam Art Assistant

A local-first toolkit for cataloging artwork files, preparing material for manual Steam publishing, and organizing draft Steam reviews for manual publication.

**This project does not automate actions on Steam.** It does not log in, upload artwork, fill review forms, submit content, accept terms, like, favorite, or claim games. The review helper only copies a draft to your clipboard and may open the game's public store page for reference. You remain in control of every action on the Steam website.

## Features

### Artwork catalog
- Scan a folder of artwork images recursively.
- Export a CSV inventory with file name, relative path, extension, file size, SHA-256, and image dimensions when Pillow is installed.
- Identify identical files by SHA-256 so you can review duplicates.
- Read-only operation: source images are never moved, renamed, or deleted.

### Steam review draft helper
- Select the first pending review draft from a local \`fila_reviews.csv\` queue.
- Save a readable backup as \`review_atual.txt\`.
- Copy the review title and body to the clipboard for you to paste manually.
- Optionally open only the game's public Steam Store page as a reference.
- Keep publication status under your control; mark a row as \`PUBLICADA\` yourself only after you publish and verify it.

See [Review preparation guide](docs/REVIEW_PREPARATION.md).

## Dependencies

### Artwork catalog
- **Python 3.9 or newer**.
- No mandatory third-party Python packages.
- Optional: **Pillow** to read image dimensions from more image formats.

Install the optional dependency:

\`\`\`bash
python -m pip install Pillow
\`\`\`

Or install the optional dependencies listed in this repository:

\`\`\`bash
python -m pip install -r requirements-optional.txt
\`\`\`

### Review draft helper
- **Python 3.9 or newer**.
- Tkinter (usually included with the Windows Python installer; the Tcl/Tk component must be installed).
- No third-party Python packages.

### Steam games CSV exporter (separate tool)

If you want a CSV containing your own Steam games, use the separate [Steam Library Exporter](https://github.com/FunnyEntity/steam_library_exporter). It is not bundled with this project and has its own requirements:

- Python 3.11 or newer.
- Its dependencies, installed from that project's \`requirements.txt\`.
- A Steam Web API key and your SteamID64.
- Your Steam profile and Game details must be set to **Public** for the Web API to return your library.

See [the CSV export instructions](docs/USAGE.md#export-your-steam-game-list-to-csv). Never publish your API key or the CSV containing your personal library.

## Quick start: catalog artwork

\`\`\`bash
python src/artwork_catalog.py "/path/to/artwork" --output artwork_inventory.csv
\`\`\`

On Windows, for example:

\`\`\`powershell
py -3 src\\artwork_catalog.py "C:\\Users\\YourName\\Pictures\\Steam Artwork" --output artwork_inventory.csv
\`\`\`

Open the generated CSV in a spreadsheet program. Review duplicate hashes before deciding what to keep.

## Quick start: prepare a review draft on Windows

1. Copy your own prepared \`fila_reviews.csv\` into the \`tools\` folder.
2. Run \`tools\\preparar_review.bat\`.
3. Review the copied title and text, then paste them into the appropriate Steam fields yourself.
4. Publish manually, if you choose, and update the queue status yourself.

The helper does not open a review form or fill any Steam page. See the [complete guide](docs/REVIEW_PREPARATION.md) for the required CSV columns and workflow.

## Manual publishing workflow

1. Use this tool to inventory and review your local artwork or prepare review drafts.
2. Prepare your title, description, review text, tags, and visibility settings separately.
3. Open Steam yourself in your normal browser and sign in directly on the official website.
4. Upload or paste content and publish manually, reviewing the page and all settings before submitting.
5. Verify the result on the Steam Community page before recording it as complete.

Never put passwords, session cookies, browser profiles, API tokens, personal game-library CSVs, or private review queues in this repository.


🛠️ Key Features

• Session Persistence: Uses Playwright's launch_persistent_context to store cookies locally (steam_perfil), keeping you logged in across script runs.
• Manual CMD Interlock: Pauses execution until you press [ENTER] in the terminal, allowing time for initial authentication and page loading.
• Direct URL Pagination: Injects numerical page parameters (?p=1, ?p=2) directly into the URL to ensure flawless navigation without relying on fragile UI buttons.
• Smart Screen Anchors: Uses wait_for_selector to pause saving until review containers (.review_box) physically load, preventing blank HTML files.
• Rate-Limit Prevention: Implements built-in cooldown delays (3 to 5 seconds per page) to mimic human browsing behavior safely.
• Automatic Termination: Scans page contents for end-of-history markers to safely close the script when finished.
• Beautiful Soup Compiler: Parses the raw cached HTML files, sanitizes game titles, drops duplicates, and exports a clean utf-8 encoded CSV file.


To download you review list

🚀 Quick Start


1. Prerequisites

bash
pip install playwright beautifulsoup4
playwright install
Use code with caution.

2. Download HTML Pages

bash
python 1_baixar_paginas.py
Use code with caution.
Log into Steam in the browser window if needed, return to your terminal, and press Enter.

3. Compile to CSV

bash
python 2_criar_csv.py
Use code with caution.


## Project scope and disclaimer

This is an independent community utility and is not affiliated with, endorsed by, or sponsored by Valve or Steam. Steam and Steam Community are trademarks of Valve Corporation. Follow the current Steam Subscriber Agreement and applicable community rules.

## License

MIT. See [LICENSE](LICENSE).
