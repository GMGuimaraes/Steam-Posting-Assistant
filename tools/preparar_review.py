# Preparador local de reviews Steam — fila offline, postagem manual.
import csv
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
QUEUE = BASE / "fila_reviews.csv"
OUTPUT = BASE / "review_atual.txt"
BACKUP = BASE / "fila_reviews.csv.backup-before-unavailable"


def save_queue(rows, fieldnames):
    """Salva a fila atomicamente e preserva uma cópia de segurança inicial."""
    if not BACKUP.exists():
        shutil.copy2(QUEUE, BACKUP)
        print(f"Backup da fila criado: {BACKUP}", flush=True)
    temp = QUEUE.with_suffix(".csv.tmp")
    with temp.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temp, QUEUE)


def open_game_page(appid):
    # Abre somente a página pública da loja; não interage com a Steam.
    url = f"https://store.steampowered.com/app/{appid}/"
    try:
        os.startfile(url)
        print(f"Página específica solicitada: {url}", flush=True)
        return url
    except Exception as exc:
        print(f"os.startfile falhou: {exc}", flush=True)
    try:
        subprocess.Popen(["cmd", "/c", "start", "", url], shell=False)
        print(f"Página específica solicitada via Windows: {url}", flush=True)
        return url
    except Exception as exc:
        print(f"Não foi possível abrir o navegador: {exc}", flush=True)
        return None


def add_note(row, message):
    old = (row.get("notes") or "").strip()
    row["notes"] = (old + " | " + message).strip(" |")


def main():
    if not QUEUE.exists():
        print(f"ERRO: fila_reviews.csv não encontrada em {BASE}", flush=True)
        return 2

    with QUEUE.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    if "status" not in fieldnames:
        print("ERRO: a fila não possui coluna status.", flush=True)
        return 2
    if "notes" not in fieldnames:
        fieldnames.append("notes")
        for row in rows:
            row.setdefault("notes", "")

    while True:
        # PUBLICADA e UNAVAILABLE não são selecionados novamente.
        pending = next((r for r in rows
            if (r.get("status") or "").startswith("DRAFT")
            and (r.get("review_text") or "").strip()), None)
        if pending is None:
            print("Fila concluída: não há mais rascunhos DRAFT.", flush=True)
            return 0

        appid = (pending.get("appid") or "").strip()
        name = (pending.get("name") or "").strip()
        if not appid.isdigit():
            pending["status"] = "UNAVAILABLE"
            add_note(pending, "AppID ausente ou inválido")
            save_queue(rows, fieldnames)
            print(f"AppID inválido; marcado UNAVAILABLE: {name}. Próximo item.", flush=True)
            continue

        url = open_game_page(appid)
        if not url:
            answer = "n"
        else:
            print("Confira o navegador. Se caiu na página geral da Steam ou a página do jogo não existe, responda N.", flush=True)
            answer = input("A página específica deste jogo abriu corretamente? [s/n]: ").strip().lower()

        if answer not in ("s", "sim", "y", "yes"):
            pending["status"] = "UNAVAILABLE"
            add_note(pending, "Página específica não abriu ou redirecionou para página geral; confirmado pelo usuário")
            save_queue(rows, fieldnames)
            print(f"{name} marcado UNAVAILABLE. Abrindo o próximo item...", flush=True)
            continue

        title = (pending.get("review_title") or "").strip()
        body = (pending.get("review_text") or "").strip()
        hours = (pending.get("hours_total") or "").strip()
        content = (
            f"JOGO: {name}\nAPPID: {appid}\nHORAS REGISTRADAS: {hours}\n"
            f"LINK DA LOJA: {url}\n\nTÍTULO DA REVIEW:\n{title}\n\n"
            f"TEXTO DA REVIEW:\n{body}\n\n"
            "Revise o texto para refletir sua experiência real.\n"
            "Este programa não preenche formulários nem publica na Steam.\n"
            "Depois de publicar manualmente, confirme no terminal para avançar a fila.\n"
        )
        OUTPUT.write_text(content, encoding="utf-8")
        print(f"Rascunho preparado: {name} (AppID {appid})", flush=True)
        print(f"Texto completo salvo em: {OUTPUT}", flush=True)

        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            clipboard_text = f"{title}\r\n\r\n{body}"
            root.clipboard_clear()
            root.clipboard_append(clipboard_text)
            root.update()
            copied_text = root.clipboard_get()
            root.destroy()
            if copied_text != clipboard_text:
                raise RuntimeError("A verificação da área de transferência não corresponde ao texto completo.")
            print("Título e CORPO COMPLETO da review copiados e verificados na área de transferência.", flush=True)
        except Exception as exc:
            print(f"Não foi possível copiar automaticamente: {exc}", flush=True)
            print("Use o arquivo review_atual.txt.", flush=True)

        print("Agora revise e publique manualmente na Steam.", flush=True)
        done = input(
            "Você concluiu a postagem manual deste jogo? "
            "[s=marcar PUBLICADA e próximo / n=manter DRAFT e sair / p=pausar e fechar]: "
        ).strip().lower()

        if done in ("s", "sim", "y", "yes"):
            pending["status"] = "PUBLICADA"
            add_note(pending, "Usuário confirmou postagem manual")
            save_queue(rows, fieldnames)
            print(f"{name} marcado PUBLICADA. Preparando o próximo item...", flush=True)
            continue

        if done in ("p", "pausar", "pause"):
            timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
            add_note(pending, f"Execução pausada pelo usuário em {timestamp}; rascunho preservado")
            save_queue(rows, fieldnames)
            print("Execução pausada. O jogo atual continua como DRAFT e será retomado na próxima execução.", flush=True)
            print("Os jogos PUBLICADA e UNAVAILABLE continuarão fora da fila.", flush=True)
            return 0

        print("Status mantido como DRAFT. Execute o arquivo .bat novamente quando quiser continuar.", flush=True)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
