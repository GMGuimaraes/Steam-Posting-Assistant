# Artwork publishing tools

The artwork workflow contains an automated Playwright script, a supervised manual alternative, and a read-only form inspector. All scripts use the local persistent browser profile at the user's home folder named SteamPost-perfil. Sign in manually in the opened browser the first time.

## Requirements

- Windows 10 or newer is recommended.
- Python 3.9 or newer.
- Playwright installed from requirements.txt.
- Chromium installed with:

~~~powershell
py -3 -m playwright install chromium
~~~

## Prepare the manifest

1. Copy envio/manifesto.example.json to envio/manifesto.json.
2. Update the image path. Paths in the manifest are resolved relative to envio/.
3. Replace the placeholder title and description.
4. Add real target game names and numeric AppIDs.
5. Keep the real manifesto.json and historico_postados.json private. They are ignored by Git.

Important fields:

| Field | Meaning |
|---|---|
| arquivo | Image path relative to the manifest folder |
| titulo | Main artwork title |
| descricao | Artwork description |
| autoria_propria | Set true only if you created the artwork and can truthfully certify that |
| modo_assistido | Fills the form but waits for a human to finish; it does not change the authorship certification |
| termos | Search terms used to expand candidate games if the initial targets are exhausted |
| titulos_extra | Alternative titles for discovered targets |
| alvos | Candidate game list with nome, appid, and optional titulo |

The example manifest is deliberately disabled: both authorship flags are false, so the script skips the item until you edit it. Only set an authorship flag when the Steam creator certification would be truthful. Permission to repost another person's artwork does not make you its creator. If you cannot truthfully certify authorship, do not use this upload form.

## Automated workflow

Run:

~~~powershell
py -3 envio/postar_tudo.py envio/manifesto.json
~~~

Or double-click envio/postar.bat.

The script:
- Uses the Community upload action, not the profile-only save action.
- Tracks SHA-256 hashes and target AppIDs to avoid reposting the same image to the same game.
- Saves manifest and history updates atomically.
- Tries to like and favorite confirmed uploads.
- Handles errors per target and saves diagnostics in envio/erros/.
- Preserves original image files; automatic deletion is disabled.

Current built-in limits:
- Up to 10 successful uploads per run.
- Up to 10 targets per image.
- Up to 2 attempts per target.
- Random 120–300 second delays between successful uploads.
- At most 5 free-game claims per run.

If a target has no upload form because the game is not owned, the script may claim that game only when Steam reports it as free and the script's age/content checks pass. It never purchases paid games. Review every candidate and every action; Steam page structure and account rules can change.

## Supervised workflow

Run:

~~~powershell
py -3 envio/enviar_artwork.py envio/manifesto.json
~~~

Or launch it from the GUI if the manifest exists.

The script opens the upload page, attaches the image, and fills title/description fields. You review the form and perform the final action yourself. It accepts either an AppID or a full url_upload value in each target.

Only confirm any creator/authorship statement if it is true. The script does not certify authorship for you.

## Read-only form inspection

Run:

~~~powershell
py -3 envio/inspecionar_form.py 2452280 767
~~~

Or double-click envio/inspecionar_form.bat. The inspector saves screenshots and a text inventory of visible and hidden form fields in envio/erros/. It does not upload or publish anything.

## Logs and local state

- envio/postar.log: run log.
- envio/historico_postados.json: hashes and AppIDs already posted.
- envio/manifesto.json: per-image targets and progress.
- envio/erros/: screenshots and element inventories for diagnostics.
- SteamPost-perfil: persistent browser session profile under the user's home folder.

Do not commit these local files. The repository includes only manifesto.example.json.
