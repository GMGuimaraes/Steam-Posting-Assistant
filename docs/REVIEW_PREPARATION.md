# Prepare Steam review drafts (Windows)

This helper prepares one review draft at a time from a private local CSV queue. It can open the game's public store page for reference, save the draft to a text file, and copy the complete title and body to the Windows clipboard.

It does **not** sign in to Steam, open or fill a review form, upload, submit, or publish anything. You must review, paste, and publish manually.

## Requirements

- Windows 10 or newer.
- Python 3.9 or newer.
- Tkinter/Tcl-Tk installed with Python.
- No third-party Python packages.

## Setup

1. Copy `tools/fila_reviews.example.csv` to `tools/fila_reviews.csv`.
2. Fill the queue with your own review drafts. Keep this personal file private and do not commit it.
3. Each row should include:

   | Column | Purpose |
   |---|---|
   | `appid` | Steam AppID |
   | `name` | Game title |
   | `hours_total` | Playtime value for your reference |
   | `store_url` | Public store URL (the helper builds the page from AppID) |
   | `review_title` | Draft review title |
   | `review_text` | Draft review body |
   | `status` | A value beginning with `DRAFT` for pending drafts |
   | `notes` | Optional notes; created if missing |

4. Keep the CSV next to `preparar_review.py`, inside the `tools` folder.

Example:

```csv
appid,name,hours_total,store_url,review_title,review_text,status,notes
123456,Example Game,2.5,https://store.steampowered.com/app/123456/,"Example title","Replace this placeholder with a review that reflects your own experience.",DRAFT - REVIEW BEFORE MANUAL POST,
```

The AppID and text above are placeholders.

## Run

Double-click:

```text
tools\preparar_review.bat
```

Or run:

```powershell
cd tools
py -3 preparar_review.py
```

## Workflow

1. The helper selects the first row whose status starts with `DRAFT` and whose `review_text` is not empty.
2. It opens the public store URL constructed from the AppID. Confirm whether the specific game page loaded. If it did not load or redirected to a generic Steam page, answer **N**; the row is marked `UNAVAILABLE` and the helper moves on.
3. When the page is confirmed, the helper writes `review_atual.txt` with the game details, title, body, and a reminder to review the text.
4. It copies the title and complete body to the clipboard and verifies the copied text by reading it back.
5. Review the draft and publish manually if you choose.
6. At the prompt, choose:
   - **S** — only after manual publication and verification. The row becomes `PUBLICADA`, the queue is saved, and the helper moves to the next draft.
   - **N** — keep the current row as `DRAFT` and exit.
   - **P** — save the current queue, add a timestamped pause note, keep the current row as `DRAFT`, and exit. Run the helper again to resume from the first pending draft.

Rows marked `PUBLICADA` and `UNAVAILABLE` are not selected again. A paused row remains `DRAFT`, so it will be offered again on the next run. Queue updates use an atomic temporary-file replacement and an initial backup is created before the first modification.

The helper cannot determine whether a review was actually published. It relies on your confirmation; choose **S** only after you have checked the result yourself.

## Privacy

Do not commit `fila_reviews.csv`, `review_atual.txt`, personal library exports, Steam credentials, API keys, cookies, or browser profiles.
