"""Interface gráfica simples para executar as ferramentas do projeto."""

from pathlib import Path
import os
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


ROOT = Path(__file__).resolve().parent
NEW_CONSOLE = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)


class SteamPostingAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("Steam Posting Assistant")
        self.root.geometry("760x560")
        self.root.minsize(640, 460)
        self.running = {}
        self.status = tk.StringVar(value="Pronto para executar.")
        self._build()
        self.root.after(800, self._poll_processes)

    def _build(self):
        outer = ttk.Frame(self.root, padding=18)
        outer.pack(fill="both", expand=True)

        ttk.Label(
            outer, text="Steam Posting Assistant",
            font=("Segoe UI", 20, "bold")
        ).pack(anchor="w")
        ttk.Label(
            outer,
            text="Escolha uma ferramenta. Scripts interativos abrem em um terminal separado.",
            wraplength=700
        ).pack(anchor="w", pady=(4, 16))

        self.actions = ttk.LabelFrame(outer, text="Ferramentas disponíveis", padding=14)
        self.actions.pack(fill="both", expand=True)
        self.action_count = 0

        self._register_available_actions()

        if self.action_count == 0:
            ttk.Label(
                self.actions,
                text="Nenhum script conhecido foi encontrado nesta pasta."
            ).grid(row=0, column=0, sticky="w")

        footer = ttk.Frame(outer)
        footer.pack(fill="x", pady=(14, 0))
        ttk.Label(footer, textvariable=self.status, wraplength=520).pack(
            side="left", fill="x", expand=True
        )
        ttk.Button(
            footer, text="Abrir pasta do projeto", command=self._open_project_folder
        ).pack(side="right", padx=(8, 0))
        ttk.Button(footer, text="Fechar", command=self.root.destroy).pack(side="right")

    def _add_action(self, label, description, callback):
        row, col = divmod(self.action_count, 2)
        card = ttk.Frame(self.actions, padding=8)
        card.grid(row=row, column=col, sticky="nsew", padx=6, pady=6)
        ttk.Button(card, text=label, command=callback).pack(fill="x")
        ttk.Label(card, text=description, wraplength=300).pack(
            anchor="w", pady=(5, 0)
        )
        self.actions.columnconfigure(col, weight=1)
        self.action_count += 1

    def _first_existing(self, candidates):
        return next((path for path in candidates if path.is_file()), None)

    def _register_available_actions(self):
        downloader = ROOT / "1_baixar_paginas.py"
        if downloader.is_file():
            self._add_action(
                "1. Baixar histórico de reviews",
                "Abre o navegador Steam e baixa as páginas do histórico.",
                lambda p=downloader: self._run_python("Download do histórico", p)
            )

        compiler = ROOT / "2_criar_csv.py"
        if compiler.is_file():
            self._add_action(
                "2. Gerar CSV das reviews",
                "Processa os HTML salvos e gera a planilha consolidada.",
                lambda p=compiler: self._run_python("Gerar CSV", p)
            )

        review_batch = self._first_existing([
            ROOT / "tools" / "postarReview.bat",
            ROOT / "tools" / "preparar_review.bat",
            ROOT / "envio" / "postarReview.bat",
            ROOT / "envio" / "preparar_review.bat",
        ])
        review_script = self._first_existing([
            ROOT / "tools" / "preparar_review.py",
            ROOT / "envio" / "preparar_review.py",
        ])
        if review_batch:
            self._add_action(
                "3. Preparar e postar reviews",
                "Abre a fila de rascunhos. Use S, N ou P no terminal.",
                lambda p=review_batch: self._run_batch("Fila de reviews", p)
            )
        elif review_script:
            self._add_action(
                "3. Preparar e postar reviews",
                "Abre a fila de rascunhos. Use S, N ou P no terminal.",
                lambda p=review_script: self._run_python("Fila de reviews", p)
            )

        cataloger = ROOT / "src" / "artwork_catalog.py"
        if cataloger.is_file():
            self._add_action(
                "4. Catalogar artes",
                "Escolha uma pasta para criar inventário e identificar duplicatas.",
                lambda p=cataloger: self._catalog_artwork(p)
            )

        artwork_batch = self._first_existing([
            ROOT / "envio" / "postar.bat",
            ROOT / "postar.bat",
        ])
        if artwork_batch and (artwork_batch.parent / "manifesto.json").is_file():
            self._add_action(
                "5. Postar artworks",
                "Executa o manifesto local de artes. Requer manifesto.json.",
                lambda p=artwork_batch: self._run_batch("Postagem de artworks", p)
            )

        inspector = self._first_existing([
            ROOT / "envio" / "inspecionar_form.bat",
            ROOT / "inspecionar_form.bat",
        ])
        if inspector:
            self._add_action(
                "6. Inspecionar formulário",
                "Executa o diagnóstico do formulário sem publicar conteúdo.",
                lambda p=inspector: self._run_batch("Inspeção do formulário", p)
            )

        assisted = ROOT / "envio" / "enviar_artwork.py"
        manifest = ROOT / "envio" / "manifesto.json"
        if assisted.is_file() and manifest.is_file():
            self._add_action(
                "7. Envio assistido de artwork",
                "Preenche os dados e deixa a confirmação final com você.",
                lambda p=assisted, m=manifest: self._run_python(
                    "Envio assistido", p, [str(m)]
                )
            )

    def _python_executable(self):
        executable = Path(sys.executable)
        if executable.name.lower() == "pythonw.exe":
            console_python = executable.with_name("python.exe")
            if console_python.exists():
                return str(console_python)
            return "py"
        return str(executable)

    def _launch(self, label, command, cwd, shell=False):
        existing = self.running.get(label)
        if existing and existing.poll() is None:
            messagebox.showinfo(
                "Já está em execução",
                f"{label} já está aberto em outra janela."
            )
            return

        try:
            process = subprocess.Popen(
                command,
                cwd=str(cwd),
                shell=shell,
                creationflags=NEW_CONSOLE if os.name == "nt" else 0
            )
        except Exception as exc:
            messagebox.showerror("Não foi possível iniciar", str(exc))
            self.status.set(f"Falha ao iniciar: {label}")
            return

        self.running[label] = process
        self.status.set(f"Executando: {label}")

    def _run_python(self, label, script, args=None):
        if not script.is_file():
            messagebox.showerror("Arquivo não encontrado", str(script))
            return
        command = [self._python_executable(), str(script)]
        command.extend(args or [])
        self._launch(label, command, script.parent if script.parent.name in ("tools", "envio") else ROOT)

    def _run_batch(self, label, batch):
        if not batch.is_file():
            messagebox.showerror("Arquivo não encontrado", str(batch))
            return
        command = f'call "{batch}"'
        self._launch(label, command, batch.parent, shell=True)

    def _catalog_artwork(self, script):
        folder = filedialog.askdirectory(
            title="Selecione a pasta com as artes"
        )
        if not folder:
            return
        output = ROOT / "artwork_inventory.csv"
        self._run_python(
            "Catalogar artes",
            script,
            [folder, "--output", str(output)]
        )

    def _poll_processes(self):
        finished = []
        for label, process in list(self.running.items()):
            code = process.poll()
            if code is not None:
                finished.append((label, code))
                del self.running[label]

        if finished:
            label, code = finished[-1]
            self.status.set(
                f"{label}: concluído." if code == 0
                else f"{label}: terminou com código {code}."
            )
        elif self.running:
            self.status.set(
                "Em execução: " + ", ".join(self.running.keys())
            )

        self.root.after(800, self._poll_processes)

    def _open_project_folder(self):
        try:
            if os.name == "nt":
                os.startfile(ROOT)
            else:
                subprocess.Popen(["xdg-open", str(ROOT)])
        except Exception as exc:
            messagebox.showerror("Não foi possível abrir a pasta", str(exc))


def main():
    window = tk.Tk()
    SteamPostingAssistant(window)
    window.mainloop()


if __name__ == "__main__":
    main()