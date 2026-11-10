# Steam Art Assistant

A small, local-first toolkit for cataloging and preparing artwork files before you publish them manually.

**This project does not connect to Steam or automate actions on Steam.** It does not log in, open a browser, upload artwork, submit forms, accept terms, like, favorite, or claim games. You remain in control of every action on the Steam website.

## Features

- Scan a folder of artwork images recursively.
- Export a CSV inventory with file name, relative path, extension, file size, SHA-256, and image dimensions when Pillow is installed.
- Identify identical files by SHA-256 so you can review duplicates.
- Read-only operation: source images are never moved, renamed, or deleted.

## Requirements

- Python 3.9 or newer.
- Optional: Pillow for image dimensions across more formats.

Install the optional dependency:

```bash
python -m pip install Pillow
```

## Quick start

```bash
python src/artwork_catalog.py "/path/to/artwork" --output artwork_inventory.csv
```

On Windows, for example:

```powershell
py -3 src\artwork_catalog.py "C:\Users\YourName\Pictures\Steam Artwork" --output artwork_inventory.csv
```

Open the CSV in a spreadsheet program. Review duplicate hashes before deciding what to keep.

## Manual publishing workflow

1. Use this tool to inventory and review your local artwork.
2. Prepare your title, description, tags, and visibility settings separately.
3. Open Steam yourself in your normal browser and sign in directly on the official website.
4. Upload and publish manually, reviewing the page and all settings before submitting.
5. Update your own records after verifying the result on the Steam Community page.

Never put passwords, session cookies, browser profiles, API tokens, or private account data in this repository.

## Project scope and disclaimer

This is an independent community utility and is not affiliated with, endorsed by, or sponsored by Valve or Steam. Steam and Steam Community are trademarks of Valve Corporation. Follow the current Steam Subscriber Agreement and applicable community rules.

## License

MIT. See [LICENSE](LICENSE).
