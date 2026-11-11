# Preparador local de reviews Steam — nao automatiza a Steam.
# Coloque uma copia privada de fila_reviews.csv nesta mesma pasta.
import csv
import os
from pathlib import Path

BASE = Path(__file__).resolve().parent
QUEUE = BASE / "fila_reviews.csv"
OUTPUT = BASE / "review_atual.txt"


def main():
    if not QUEUE.exists():
        print("ERRO: fila_reviews.csv nao encontrada.")
        print(f"Coloque uma copia do arquivo em: {QUEUE}")
        return 2

    with QUEUE.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    pending = [
        row for row in rows
        if (row.get("status") or "").startswith("DRAFT")
        and (row.get("review_text") or "").strip()
    ]
    if not pending:
        print("Nenhum rascunho pendente com texto encontrado.")
        return 0

    # Mantem a ordem da fila: o primeiro rascunho pendente e apresentado.
    item = pending[0]
    title = (item.get("review_title") or "").strip()
    body = (item.get("review_text") or "").strip()
    appid = (item.get("appid") or "").strip()
    name = (item.get("name") or "").strip()
    hours = (item.get("hours_total") or "").strip()
    url = (item.get("store_url") or "").strip()

    content = (
        f"JOGO: {name}\nAPPID: {appid}\nHORAS REGISTRADAS: {hours}\n"
        f"LINK DA LOJA: {url}\n\n"
        f"TITULO DA REVIEW:\n{title}\n\n"
        f"TEXTO DA REVIEW:\n{body}\n\n"
        "IMPORTANTE: revise o texto para refletir sua experiencia real.\n"
        "Este preparador nao abre formularios, nao preenche campos e nao publica.\n"
        "Depois de publicar manualmente, atualize o status na fila para PUBLICADA.\n"
    )
    OUTPUT.write_text(content, encoding="utf-8")

    # Copia somente o titulo e o texto; o usuario cola manualmente.
    review_clipboard = f"{title}\r\n\r\n{body}"
    try:
        import tkinter as tk

        root = tk.Tk()
        root.withdraw()
        root.clipboard_clear()
        root.clipboard_append(review_clipboard)
        root.update()
        root.destroy()
    except Exception as exc:
        print(f"ERRO ao copiar para a area de transferencia: {exc}")
        print(f"O rascunho completo continua salvo em: {OUTPUT}")
        return 3

    print(f"Review copiada para a area de transferencia: {name} (AppID {appid})")
    print("Cole o titulo e o texto nos campos correspondentes da Steam.")
    print("Confira se ja existe uma review sua e revise o texto antes de salvar.")
    print(f"Copia de seguranca: {OUTPUT}")

    # Abre somente a pagina publica da loja; nao abre nem preenche formulario.
    if url.startswith("https://store.steampowered.com/"):
        try:
            os.startfile(url)
            print(f"Pagina publica da loja aberta no navegador: {url}")
        except OSError as exc:
            print(f"Nao foi possivel abrir o navegador automaticamente: {exc}")
            print(f"Abra manualmente: {url}")
    else:
        print("URL da loja ausente ou invalida; nenhum navegador foi aberto.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
