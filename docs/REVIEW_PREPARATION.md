# Prepare Steam review drafts (Windows)

This optional helper takes the next pending draft from a local CSV queue, writes a backup text file, copies the title and review body to the Windows clipboard, and may open the game's **public store page** for reference.

It does **not** sign in to Steam, open a review form, fill fields, upload, submit, or publish anything. You must review and paste the text yourself.

## Requirements

- Windows 10 or newer.
- Python 3.9 or newer.
- Tkinter/Tcl-Tk installed with Python (normally available in the standard Windows installer).
- No third-party Python packages.

## Setup

1. Copy \`tools/fila_reviews.example.csv\` to \`tools/fila_reviews.csv\`.
2. Fill the queue with your own review drafts. Keep this personal file private and do not commit it.
3. Each row must include these columns:

   | Column | Purpose |
   |---|---|
   | \`appid\` | Steam AppID |
   | \`name\` | Game title |
   | \`hours_total\` | Playtime value to display for your own reference |
   | \`store_url\` | Public store URL, such as \`https://store.steampowered.com/app/APPID/\` |
   | \`review_title\` | Draft review title |
   | \`review_text\` | Draft review body |
   | \`status\` | Use a value beginning with \`DRAFT\` for pending drafts |

   Other columns may be present; the helper ignores them.

4. Keep the CSV next to \`preparar_review.py\`, inside the \`tools\` folder.

Example header and row:

\`\`\`csv
appid,name,hours_total,store_url,review_title,review_text,status
123456,Example Game,2.5,https://store.steampowered.com/app/123456/,"Example title","Replace this placeholder with a review that reflects your own experience.",DRAFT - REVIEW BEFORE MANUAL POST
\`\`\`

The example AppID and text are placeholders only.

## Run

Double-click:

\`\`\`text
tools\\preparar_review.bat
\`\`\`

Or run from a terminal:

\`\`\`powershell
cd tools
py -3 preparar_review.py
\`\`\`

The helper:
1. Reads the queue in its existing row order.
2. Selects the first row whose \`status\` starts with \`DRAFT\` and whose \`review_text\` is not empty.
3. Writes \`review_atual.txt\` with the game details, title, body, and manual-review reminder.
4. Copies the title and body, separated by a blank line, to the clipboard.
5. Opens \`store_url\` only if it begins with the official public Steam Store URL prefix.

If clipboard access fails, the backup text file is still available. If there are no pending drafts, the helper reports that and exits.

## Manual publication and queue tracking

1. Review the title and body in \`review_atual.txt\`.
2. Make sure the text accurately reflects your own experience and check whether you already reviewed the game.
3. Open the Steam page yourself, paste the title and body into the correct fields, and publish manually if you choose.
4. Verify that your review is visible.
5. Only then, edit your local \`fila_reviews.csv\` and change that row's status to \`PUBLICADA\`.

The helper does not change queue statuses automatically and does not verify whether a review was published. Run it again to prepare the next pending row.

## Privacy

Do not commit \`fila_reviews.csv\`, \`review_atual.txt\`, personal library exports, Steam credentials, API keys, cookies, or browser profiles. The repository's \`.gitignore\` excludes CSV and generated text files by default.
