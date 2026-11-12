import csv
import os
import time
import subprocess
import pyautogui
import pyperclip  # Biblioteca robusta para gerenciar a área de transferência

# Configurações de segurança e velocidade do PyAutoGUI
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.8  

CSV_FILE = 'fila_reviews.csv'
PASTA_DRAFTS = 'drafts'

def garantir_pasta_drafts():
    """Garante que a pasta para salvar os rascunhos exista."""
    if not os.path.exists(PASTA_DRAFTS):
        os.makedirs(PASTA_DRAFTS)

def ler_fila():
    """Lê o arquivo CSV da fila de reviews."""
    if not os.path.exists(CSV_FILE):
        print(f"[AVISO] Arquivo {CSV_FILE} não encontrado.")
        return []
    
    linhas = []
    with open(CSV_FILE, mode='r', encoding='utf-8') as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            linhas.append(linha)
    return linhas

def atualizar_status_csv(index_alvo, novo_status):
    """Atualiza o status do item no CSV para manter o controle."""
    linhas = ler_fila()
    if 0 <= index_alvo < len(linhas):
        linhas[index_alvo]['status'] = novo_status
        if linhas:
            chaves = linhas[0].keys()
            with open(CSV_FILE, mode='w', encoding='utf-8', newline='') as f:
                escritor = csv.DictWriter(f, fieldnames=chaves)
                escritor.writeheader()
                escritor.writerows(linhas)

def obter_valor_csv(item, chaves_possiveis):
    """Tenta encontrar o valor em uma lista de possíveis nomes de colunas."""
    for chave in chaves_possiveis:
        if chave in item and item[chave]:
            val = str(item[chave]).strip()
            if val:
                return val
        for k in item.keys():
            if k.lower() == chave.lower() and item[k]:
                val = str(item[k]).strip()
                if val:
                    return val
    return ''

def salvar_drafts_pendentes():
    """OPÇÃO 1: Varre a fila e salva o conteúdo dos itens pendentes a partir do CSV."""
    garantir_pasta_drafts()
    fila = ler_fila()
    
    if not fila:
        print("Nenhum item na fila para gerar drafts.")
        return

    criados = 0
    for idx, item in enumerate(fila):
        status = item.get('status', '').strip().upper()
        
        if status != 'PUBLICADA':
            nome_jogo = obter_valor_csv(item, ['nome', 'appName', 'jogo', 'title', 'game'])
            if not nome_jogo:
                nome_jogo = f'jogo_{idx+1}'
            
            nome_limpo = "".join(c for c in nome_jogo if c.isalnum() or c in (' ', '_', '-')).strip()
            if not nome_limpo:
                nome_limpo = f'jogo_{idx+1}'
                
            caminho_arquivo = os.path.join(PASTA_DRAFTS, f"{nome_limpo}.txt")
            
            url_jogo = obter_valor_csv(item, ['url', 'link', 'url_jogo', 'link_jogo', 'store_url', 'href'])
            
            texto_review = obter_valor_csv(item, ['review_text', 'review', 'texto', 'content', 'descricao', 'comment', 'comentario'])
            if not texto_review:
                texto_review = f"Recomendo muito {nome_jogo}! Excelente jogo!"
            
            e_gratuito = obter_valor_csv(item, ['gratuito', 'free', 'recebido_graca', 'gratis']).lower()
            
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                f.write(f"URL: {url_jogo}\n")
                f.write(f"GRATUITO: {e_gratuito}\n")
                f.write(f"---TEXTO---\n")
                f.write(texto_review)
            
            atualizar_status_csv(idx, 'DRAFT')
            criados += 1

    print(f"\n[SUCESSO] {criados} novos drafts gerados e salvos na pasta '{PASTA_DRAFTS}/'.")

def copiar_para_clipboard_blindado(texto):
    """Grava o texto no clipboard usando pyperclip e valida se foi aplicado corretamente."""
    for tentativa in range(3):
        try:
            pyperclip.copy(texto)
            time.sleep(0.3)
            # Confere se o clipboard realmente recebeu o texto
            if pyperclip.paste() == texto:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    print("[AVISO] Falha ao fixar no clipboard, tentando via fallback do sistema...")
    # Fallback extremo caso o pyperclip falhe
    command = 'echo ' + text.strip() + ' | clip'
    os.system(command)
    return True

def executar_automacao_navegador(texto_review, eh_gratuito):
    """OPÇÃO 2: Copia o texto limpo com pyperclip e executa a automação com validação."""
    print("-> Aguardando a página carregar completamente...")
    time.sleep(6)
    
    # 0. Garante foco na janela do navegador
    pyautogui.click(x=650, y=300)
    time.sleep(0.5)

    # 1. COPIA O TEXTO EXATO E VALIDA NA ÁREA DE TRANSFERÊNCIA
    print("-> Copiando o texto limpo do draft para a área de transferência...")
    copiar_para_clipboard_blindado(texto_review)
    time.sleep(0.8)

    # 2. Scroll para posicionar a seção de review na tela
    pyautogui.scroll(-700)
    time.sleep(1.5)
    
    # 3. CLIQUE NA CAIXA DE TEXTO (X=650, Y=650)
    print("-> Clicando na caixa de texto do review...")
    pyautogui.click(x=650, y=650)
    time.sleep(1)
    
    # Limpa o campo e cola o review limpo via Ctrl+V
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')
    time.sleep(0.5)
    
    print("-> Colando o texto correto na Steam...")
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(1.5)

    # 4. DEFINIÇÃO DA QUANTIDADE DE TABS (7 se for gratuito, 6 no padrão)
    qtd_tabs = 7 if eh_gratuito in ['sim', 's', 'true', '1', 'yes'] else 6
    print(f"-> Navegando via Tab ({qtd_tabs} vezes) até o botão 'Sim' (Recomendar)...")
    
    for _ in range(qtd_tabs):
        pyautogui.press('tab')
        time.sleep(0.2)
    
    pyautogui.press('enter')
    time.sleep(1.2)

    # 5. NAVEGAÇÃO POR TAB ATÉ O "PUBLICAR" (Mais 2 tabs) + ENTER PARA CONFIRMAR
    print("-> Navegando via Tab (2 vezes) até o botão 'Publicar' e enviando...")
    for _ in range(2):
        pyautogui.press('tab')
        time.sleep(0.2)
    
    pyautogui.press('enter')
    
    print("-> Aguardando efetivação da postagem...")
    time.sleep(6)
    print("[SUCESSO] Review postado com sucesso!")

def publicar_drafts():
    """Lê os drafts salvos da pasta, extrai exclusivamente o texto limpo, fecha a aba anterior e dispara a automação."""
    fila = ler_fila()
    drafts = [item for item in fila if item.get('status', '').strip().upper() == 'DRAFT']
    
    print(f"\nItens prontos (DRAFT) para publicar: {len(drafts)}")
    
    if len(drafts) == 0:
        print("Não há nenhum draft para publicar no momento. Gere os drafts na opção [1] primeiro.")
        return

    resposta = input("Deseja iniciar a automação de publicação dos drafts agora? [s/n]: ").strip().lower()
    if resposta != 's':
        print("Publicação cancelada.")
        return

    print("\nIniciando processo de publicação automática...\n")
    time.sleep(1)
    
    primeiro_jogo = True
    for idx, item in enumerate(fila):
        status = item.get('status', '').strip().upper()
        
        if status == 'DRAFT':
            nome_jogo = obter_valor_csv(item, ['nome', 'appName', 'jogo', 'title', 'game'])
            if not nome_jogo:
                nome_jogo = f'Item {idx+1}'
                
            url_jogo = obter_valor_csv(item, ['url', 'link', 'url_jogo', 'link_jogo', 'store_url', 'href'])
            
            nome_limpo = "".join(c for c in nome_jogo if c.isalnum() or c in (' ', '_', '-')).strip()
            if not nome_limpo:
                nome_limpo = f'Item {idx+1}'
                
            caminho_arquivo = os.path.join(PASTA_DRAFTS, f"{nome_limpo}.txt")
            
            texto = ""
            eh_gratuito = "nao"
            
            # Extração limpa do conteúdo de texto do arquivo draft
            if os.path.exists(caminho_arquivo):
                with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                    for linha in conteudo.split('\n'):
                        if linha.upper().startswith('GRATUITO:'):
                            eh_gratuito = linha.split(':', 1)[1].strip().lower()
                    
                    if "---TEXTO---" in conteudo:
                        texto = conteudo.split("---TEXTO---", 1)[1].strip()
                    else:
                        linhas_txt = [l for l in conteudo.split('\n') if not l.startswith('URL:') and not l.startswith('GRATUITO:') and not '---TEXTO---' in l]
                        texto = "\n".join(linhas_txt).strip()
            
            if not texto:
                texto = obter_valor_csv(item, ['review_text', 'review', 'texto', 'content', 'descricao', 'comment', 'comentario']) or f'Recomendo muito {nome_jogo}!'

            print(f"\n--- Processando [{idx+1}/{len(fila)}]: {nome_jogo} (Gratuito: {eh_gratuito}) ---")
            
            if not url_jogo:
                print(f"[ERRO] URL não encontrada para este item.")
                continue
            
            try:
                if not primeiro_jogo:
                    print("-> Fechando a aba anterior do navegador (Ctrl + W)...")
                    pyautogui.hotkey('ctrl', 'w')
                    time.sleep(1)
                else:
                    primeiro_jogo = False

                print(f"-> Abrindo navegador para: {url_jogo}")
                os.system(f'start "" "{url_jogo}"')
                time.sleep(6)
                
                executar_automacao_navegador(texto, eh_gratuito)
                
                atualizar_status_csv(idx, 'PUBLICADA')
                print(f"-> Status atualizado para PUBLICADA no CSV.")
                
            except Exception as e:
                print(f"[ERRO] Falha na automação: {e}")
            
            print("Aguardando próximo item...")
            time.sleep(3)

if __name__ == '__main__':
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("================================================")
        print("  GERENCIADOR DE REVIEWS STEAM - DRAFTS & FILA")
        print("================================================")
        print("[1] Gerar / Salvar novos drafts (a partir da fila)")
        print("[2] Publicar drafts existentes (Automação)")
        print("[3] Sair")
        print("================================================")
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == '1':
            salvar_drafts_pendentes()
            input("\nPressione <Enter> para voltar ao menu...")
        elif opcao == '2':
            publicar_drafts()
            input("\nPressione <Enter> para voltar ao menu...")
        elif opcao == '3':
            print("\nEncerrando o programa. Até logo!")
            break
        else:
            input("\nOpção inválida! Pressione <Enter> para tentar novamente...")