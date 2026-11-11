# Steam Posting Assistant

A local-first toolkit for organizing Steam-related media and preparing review drafts for **manual** publication. It includes an offline artwork catalog, local review-queue management, text-file backups, and clipboard preparation.

**Safety and scope:** this project does not automate Steam interactions. It does not log in, upload, fill forms, submit reviews, accept terms, like, favorite, or claim games. The review helper may open a public store page for reference, but all review checks, editing, and publication are performed manually by the user.

## Features

### Artwork catalog
- Recursively scan a local folder of artwork images.
- Export a CSV inventory with filename, relative path, extension, file size, SHA-256, and image dimensions when Pillow is installed.
- Identify byte-identical files by SHA-256.
- Read-only source handling: original images are not moved, renamed, or deleted.

### Review draft queue (Windows)
- Read a private local `fila_reviews.csv` and select the first pending row whose status begins with `DRAFT`.
- Open the game's public store page using its AppID and let the user confirm whether the specific game page loaded.
- Mark unavailable or incorrectly redirected game pages as `UNAVAILABLE` and continue to the next draft.
- Save the current game's full review information to `review_atual.txt`.
- Copy the complete title and review body to the clipboard, with a read-back verification.
- Offer three end-of-item choices:
  - **S** — the user confirms they manually published the review; mark the row `PUBLICADA`, save the queue, and continue.
  - **N** — keep the current row as `DRAFT` and exit.
  - **P** — pause and exit, save the queue and a timestamped note, and preserve the current row as `DRAFT` for the next run.
- Skip rows already marked `PUBLICADA` or `UNAVAILABLE`, so completed or unavailable games are not repeated.
- Save queue changes atomically and create an initial backup before the first change.

The helper does not independently verify publication. Choose **S** only after you have published and checked the review yourself. Review text should accurately reflect your own experience.

See [Review preparation guide](docs/REVIEW_PREPARATION.md).

## Requirements

### Artwork catalog
- Python 3.9 or newer.
- No mandatory third-party packages.
- Optional: Pillow for broader image-dimension support.

```bash
python -m pip install -r requirements-optional.txt
```

### Review draft helper
- Windows 10 or newer.
- Python 3.9 or newer.
- Tkinter/Tcl-Tk (normally included with the standard Windows Python installer).
- No third-party Python packages.

## Quick start: catalog artwork

```bash
python src/artwork_catalog.py "./artwork" --output inventory.csv
```

## Quick start: prepare review drafts on Windows

1. Copy `tools/fila_reviews.example.csv` to `tools/fila_reviews.csv`.
2. Add your own draft text and keep this personal CSV private.
3. Run `tools/preparar_review.bat`.
4. Confirm whether the specific game store page opened correctly.
5. Review the generated `review_atual.txt` and clipboard text, then paste and publish manually if you choose.
6. At the end of each prepared item, choose **S**, **N**, or **P** as described above.

The queue is local state. Rows marked `PUBLICADA` or `UNAVAILABLE` are skipped on later runs; paused rows remain `DRAFT` and resume in queue order.

## Steam game-library CSV (optional input)

To export your own library, use the separate [Steam Library Exporter](https://github.com/FunnyEntity/steam_library_exporter). Follow its current README for setup, dependencies, Python version, Steam Web API key, SteamID64, and profile privacy requirements. Keep the API key and exported personal library CSV private; never commit them here.

## Privacy

Never commit passwords, session cookies, browser profiles, API tokens, personal game-library exports, private review queues, or generated personal review text. The repository's ignore rules exclude private CSV and generated text files by default; verify before committing.

## Project scope

This is an independent community utility and is not affiliated with, endorsed by, or sponsored by Valve or Steam. Steam and Steam Community are trademarks of Valve Corporation. Follow the current Steam Subscriber Agreement and applicable community rules.

## License

MIT. See [LICENSE](LICENSE).
