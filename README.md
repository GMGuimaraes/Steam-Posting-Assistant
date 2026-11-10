# Steam Art Assistant

A small, local-first toolkit for cataloging and preparing artwork files before you publish them manually.

**This project does not connect to Steam or automate actions on Steam.** It does not log in, open a browser, upload artwork, submit forms, accept terms, like, favorite, or claim games. You remain in control of every action on the Steam website.

## Features

- Scan a folder of artwork images recursively.
- Export a CSV inventory with file name, relative path, extension, file size, SHA-256, and image dimensions when Pillow is installed.
- Identify identical files by SHA-256 so you can review duplicates.
- Read-only operation: source images are never moved, renamed, or deleted.

## Dependencies

### Steam Art Assistant

- **Python 3.9 or newer**.
- No mandatory third-party Python packages.
- Optional: **Pillow** to read image dimensions from more image formats.

Install the optional dependency:

```bash
python -m pip install Pillow
```

Or install the optional dependencies listed in this repository:

```bash
python -m pip install -r requirements-optional.txt
```

### Steam games CSV exporter (separate tool)

If you want a CSV containing your own Steam games, use the separate [Steam Library Exporter](https://github.com/FunnyEntity/steam_library_exporter). It is not bundled with this project and has its own requirements:

- Python 3.11 or newer.
- Its dependencies, installed from that project's `requirements.txt`.
- A Steam Web API key and your SteamID64.
- Your Steam profile and Game details must be set to **Public** for the Web API to return your library.

See [the CSV export instructions](docs/USAGE.md#export-your-steam-game-list-to-csv). Never publish your API key or the CSV containing your personal library.

## Quick start: catalog artwork

```bash
python src/artwork_catalog.py "/path/to/artwork" --output artwork_inventory.csv
```

On Windows, for example:

```powershell
py -3 src\artwork_catalog.py "C:\Users\YourName\Pictures\Steam Artwork" --output artwork_inventory.csv
```

Open the generated CSV in a spreadsheet program. Review duplicate hashes before deciding what to keep.

## Manual publishing workflow

1. Use this tool to inventory and review your local artwork.
2. Prepare your title, description, tags, and visibility settings separately.
3. Open Steam yourself in your normal browser and sign in directly on the official website.
4. Upload and publish manually, reviewing the page and all settings before submitting.
5. Update your own records after verifying the result on the Steam Community page.

Never put passwords, session cookies, browser profiles, API tokens, personal game-library CSVs, or other private account data in this repository.

## Project scope and disclaimer

This is an independent community utility and is not affiliated with, endorsed by, or sponsored by Valve or Steam. Steam and Steam Community are trademarks of Valve Corporation. Follow the current Steam Subscriber Agreement and applicable community rules.

## License

MIT. See [LICENSE](LICENSE).
