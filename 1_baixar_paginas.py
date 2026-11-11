import os
import time
from playwright.sync_api import sync_playwright

# --- CONFIGURAÇÃO ---
STEAM_ID = "YOUR_ID_STEAM"
PROFILE_DIR = "steam_perfil"
OUTPUT_DIR = "html_pages"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)


def baixar_paginas_review():
    with sync_playwright() as p:
        print("\n==========================================================")
        print("INICIANDO NAVEGADOR COM PERSISTÊNCIA DE SESSÃO...")
        print(f"Saves e cookies armazenados em: '{PROFILE_DIR}'")
        print("==========================================================\n")

        context = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR, headless=False, no_viewport=True
        )
        page = context.new_page()

        # Desativa limites de timeout padrão do Playwright
        page.set_default_navigation_timeout(0)
        page.set_default_timeout(0)

        # Abre o hub inicial da Steam para garantir o estado do login
        print("Carregando navegador inicial...")
        page.goto("https://steamcommunity.com/", wait_until="commit")

        print("\n==========================================================")
        print(" AGUARDANDO COMANDO MANUAL NO CMD")
        print(" Verifique se sua conta já aparece conectada no navegador.")
        print(" Caso precise logar, faça o login agora.")
        print(" VOLTE AQUI NO CMD E APERTE [ENTER] PARA INICIAR O DOWNLOAD.")
        print("==========================================================\n")

        # Trava aguardando o seu clique no CMD
        input("Aperte [ENTER] para iniciar o download sequencial das páginas...")

        page_number = 1

        while True:
            # FIX: Adicionada a barra '/' explícita após o '.com' para evitar a URL colada
            target_url = f"https://steamcommunity.com/id/{STEAM_ID}/reviews/?p={page_number}"
            print(f"\nNavegando para a página {page_number}...")
            print(f"URL: {target_url}")
            
            try:
                page.goto(target_url, wait_until="load")
            except Exception as e:
                print(f"Erro de conexão na página {page_number}: {e}")
                page.goto(target_url, wait_until="commit")

            # ÂNCORA DE SEGURANÇA: Espera as caixas de comentários renderizarem fisicamente na página
            try:
                page.wait_for_selector(".review_box, #leftContents", timeout=15000)
            except Exception:
                print("[Aviso] Bloco de reviews demorou para responder. Verificando conteúdo...")

            # COOLDOWN ATIVO: Pausa para a Steam carregar os textos por completo antes de ler o HTML
            print("Aguardando estabilização dos elementos visuais...")
            page.wait_for_timeout(5000)

            # Captura o conteúdo completo gerado
            html_content = page.content()
            
            # Condições de parada
            if "Nenhuma análise foi encontrada" in html_content or "No entries" in html_content:
                print(f"\n[FIM] Página {page_number} veio vazia ou sem análises. Encerrando.")
                break

            if "Showing 0-0 of" in html_content:
                print("\n[FIM] Fim das reviews alcançado.")
                break

            # Gravação do arquivo HTML local
            file_path = os.path.join(OUTPUT_DIR, f"pagina_{page_number}.html")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"[SUCESSO] Código-fonte da página {page_number} salvo em '{file_path}'.")

            # Pausa de segurança extra entre as páginas (Evita erro HTTP 429)
            time.sleep(3)
            
            page_number += 1

        print(f"\n[CONCLUÍDO] Processo finalizado! {page_number - 1} arquivos HTML gerados na pasta '{OUTPUT_DIR}'.")
        context.close()


if __name__ == "__main__":
    baixar_paginas_review()
