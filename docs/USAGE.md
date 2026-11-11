# Usage guide

## 1. Start the graphical launcher

On Windows, double-click iniciar_interface.bat, or run:

~~~powershell
py -3 launcher_gui.py
~~~

The launcher discovers scripts available in the project folder and creates a button for each one. Interactive scripts open in a separate terminal so login prompts and S/N/P choices remain available. The interface includes a folder picker for artwork cataloging and a process-status indicator.

## 2. Install dependencies

Python 3.9 or newer is recommended. Install the required packages:

~~~powershell
py -3 -m pip install -r requirements.txt
py -3 -m playwright install chromium
~~~

The GUI and review clipboard use Tkinter/Tcl-Tk, normally included with the standard Windows Python installer. Optional image-dimension support:

~~~powershell
py -3 -m pip install -r requirements-optional.txt
~~~

This installs Pillow. Without Pillow, the artwork cataloger still calculates file hashes but leaves image dimensions blank.

## 3. Download Steam review history

1. Edit STEAM_ID in 1_baixar_paginas.py and replace YOUR_ID_STEAM with your profile vanity URL or profile identifier.
2. Run:

~~~powershell
py -3 1_baixar_paginas.py
~~~

3. Sign in manually in the browser if needed.
4. Return to the terminal and press Enter to begin.

Pages are stored locally in html_pages/.

## 4. Compile review history to CSV

~~~powershell
py -3 2_criar_csv.py
~~~

The compiler reads saved pages in numeric order, extracts game title, AppID, sentiment, and review text when available, removes duplicate AppIDs, and writes todos_jogos_com_comentarios.csv.

## 5. Prepare Steam review drafts

1. Copy tools/fila_reviews.example.csv to tools/fila_reviews.csv.
2. Add your own data and set pending rows to DRAFT.
3. Run tools/postarReview.bat.
4. Paste and publish manually. S confirms a verified publication; N leaves the current row as DRAFT and exits; P saves the queue and pauses.
5. Later runs skip PUBLICADA and UNAVAILABLE rows.

See REVIEW_PREPARATION.md.

## 6. Catalog artwork

~~~powershell
py -3 src/artwork_catalog.py "C:\path\to\artwork" --output artwork_inventory.csv
~~~

The cataloger scans recursively by default and never changes source images.

## 7. Publish artwork

1. Copy envio/manifesto.example.json to envio/manifesto.json.
2. Update the image path, title, description, authorship flags, and target games.
3. Run the automated workflow:

~~~powershell
py -3 envio/postar_tudo.py envio/manifesto.json
~~~

Or double-click envio/postar.bat.

For supervised manual upload:

~~~powershell
py -3 envio/enviar_artwork.py envio/manifesto.json
~~~

For read-only diagnostics:

~~~powershell
py -3 envio/inspecionar_form.py 2452280 767
~~~

See ARTWORK_PUBLISHING.md for manifest fields, rate limits, and safety rules.

## 8. Privacy and safety

Keep personal review queues, manifesto.json, historico_postados.json, generated review text, downloaded HTML, browser profiles, error screenshots, logs, cookies, passwords, API keys, and session tokens private. The repository ignores common generated/private files and tracks only the example manifest.

Only publish artwork you created when the Steam form requires creator certification. Assisted mode does not change what the certification means; permission to repost is not the same as authorship. Never make a certification that is not true.
