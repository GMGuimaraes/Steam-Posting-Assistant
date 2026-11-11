"""
Read-only diagnostic for the Steam artwork upload form.
Captures a screenshot and a text inventory of form elements; never submits anything.
Usage: python inspecionar_form.py [appid ...]
"""
import sys
import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

PROFILE = Path.home() / "SteamPost-perfil"
OUTPUT_DIR = Path(__file__).with_name("erros")

INSPECT_JS = """() => {
  const elements = [...document.querySelectorAll(
    'input, select, textarea, button, a, [onclick]'
  )].filter(e => e.type === 'hidden' || e.type === 'file' || e.offsetParent !== null);

  const labelFor = e => {
    const label = e.closest('label') ||
      (e.id && document.querySelector('label[for="' + e.id + '"]'));
    return label ? label.innerText.trim() : '';
  };

  return [
    'URL: ' + location.href,
    'TITLE: ' + document.title,
    'VISIBLE TEXT: ' + document.body.innerText.replace(/\\s+/g, ' ').slice(0, 2500),
    'ELEMENTS:',
    ...elements.map(e => [
      e.tagName,
      'id=' + e.id,
      'name=' + (e.name || ''),
      'type=' + (e.type || ''),
      'text=' + (e.innerText || '').trim().slice(0, 80),
      'value=' + (e.value || '').toString().slice(0, 80),
      'label=' + labelFor(e),
      'onclick=' + (e.getAttribute('onclick') || '').slice(0, 100)
    ].join(' | '))
  ].join('\\n');
}"""


def main(appids):
    OUTPUT_DIR.mkdir(exist_ok=True)
    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            str(PROFILE), headless=False
        )
        page = context.new_page()

        for appid in appids:
            url = f"https://steamcommunity.com/sharedfiles/edititem/{appid}/3/"
            print(f"Abrindo {url}", flush=True)
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=120000)
            except Exception as exc:
                print(f"Aviso de navegação: {type(exc).__name__}", flush=True)

            page.wait_for_timeout(8000)
            prefix = OUTPUT_DIR / f"form-{appid}-{datetime.datetime.now():%H%M%S}"

            try:
                page.screenshot(path=str(prefix) + ".png", full_page=True)
            except Exception as exc:
                print(f"Não foi possível salvar a captura: {exc}", flush=True)

            try:
                details = page.evaluate(INSPECT_JS)
                Path(str(prefix) + ".txt").write_text(details, encoding="utf-8")
                print(f"Diagnóstico salvo: {prefix.name}", flush=True)
            except Exception as exc:
                print(f"Não foi possível listar os campos: {exc}", flush=True)

        context.close()

    print("Inspeção concluída. Nenhum conteúdo foi publicado.")


if __name__ == "__main__":
    main(sys.argv[1:] or ["2452280", "767"])
