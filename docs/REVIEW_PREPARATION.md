# Steam review draft queue (Windows)

The review helper processes one pending review at a time from a local CSV queue. It writes a backup text file, copies the complete title and review body to the clipboard, and opens the game's public Steam Store page for reference.

It does **not** sign in to Steam, open a review form, fill fields, submit, or publish anything. You must paste and publish manually.

## Requirements

- Windows 10 or newer.
- Python 3.9 or newer.
- Tkinter/Tcl-Tk installed with Python for clipboard support (normally included with the standard Windows installer).
- No third-party Python packages.

## Setup

1. Copy `tools/fila_reviews.example.csv` to `tools/fila_reviews.csv`.
2. Keep the personal queue private; it is excluded from version control by the repository's ignore rules.
3. Include these columns:

   | Column | Purpose |
   |---|---|
   | `appid` | Numeric Steam AppID |
   | `name` | Game title |
   | `hours_total` | Playtime value for your reference |
   | `store_url` | Public Steam Store URL |
   | `review_title` | Review title |
   | `review_text` | Review body |
   | `status` | Use `DRAFT` for a pending review |
   | `notes` | Optional notes; created automatically if absent |

4. Place the CSV beside `preparar_review.py`, inside the `tools` folder.

Example:

~~~csv
appid,name,hours_total,store_url,review_title,review_text,status
123456,Example Game,2.5,https://store.steampowered.com/app/123456/,"Example title","Replace this placeholder with a review based on your own experience.",DRAFT
~~~

The AppID and text above are placeholders.

## Run

Double-click:

~~~text
tools\postarReview.bat
~~~

Or run directly:

~~~powershell
cd tools
py -3 preparar_review.py
~~~

## Workflow and keyboard choices

For each pending row:

1. The helper opens the specific Store URL using the AppID.
2. Confirm whether the correct game's page opened. If it opened the general Steam page, does not exist, or is otherwise incorrect, answer **N** at this first prompt. The row is marked `UNAVAILABLE`, saved, and the helper advances to the next item.
3. If the page is correct, the helper writes `review_atual.txt`, then copies the title and complete review body to the clipboard.
4. Review the text, paste it into the appropriate Steam fields, and publish manually if you choose.
5. At the publication prompt, choose:

   | Key | Result |
   |---|---|
   | **S** | Confirm manual publication, save the row as `PUBLICADA`, and continue to the next pending draft. |
   | **N** | Leave the current row as `DRAFT` and exit. It will be available again next time. |
   | **P** | Save the queue and a timestamped pause note, leave the current row as `DRAFT`, and exit the script. |

The queue is saved atomically whenever a status changes or the user pauses. A local backup is created before the first update.

On the next execution, the helper selects the first row still marked `DRAFT`. Rows marked `PUBLICADA` and `UNAVAILABLE` are skipped, so completed or unavailable games from the previous run are not repeated.

**Important:** The helper does not independently verify Steam publication. Choose **S** only after you have manually published and verified the review.

## Files created locally

- `review_atual.txt`: readable backup of the current game's details and review.
- `fila_reviews.csv.backup-before-unavailable`: first-update backup of the queue.
- `fila_reviews.csv.tmp`: temporary file used during atomic saves; it is renamed to the queue after a successful write.

Do not commit these files, your personal queue, Steam credentials, cookies, or browser profiles.
