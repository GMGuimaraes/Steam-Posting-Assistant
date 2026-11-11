import csv
import os
import re
from bs4 import BeautifulSoup

INPUT_DIR = "html_pages"
OUTPUT_CSV = "todos_jogos_com_comentarios.csv"


def extrair_dados_completos():
    if not os.path.exists(INPUT_DIR):
        print(
            f"Erro: A pasta '{INPUT_DIR}' não existe. Rode o primeiro script antes."
        )
        return

    arquivos = [f for f in os.listdir(INPUT_DIR) if f.endswith(".html")]
    if not arquivos:
        print("Nenhum arquivo HTML encontrado para processar.")
        return

    # Ordena as páginas numericamente para manter a consistência
    arquivos.sort(
        key=lambda f: int(re.search(r"\d+", f).group())
        if re.search(r"\d+", f)
        else 0
    )

    print(f"Processando {len(arquivos)} arquivos HTML encontrados...\n")

    dados_planilha = []
    jogos_processados = set()
    paginas_com_sucesso = 0
    paginas_com_erro = 0

    for arquivo in arquivos:
        caminho_arquivo = os.path.join(INPUT_DIR, arquivo)
        try:
            with open(caminho_arquivo, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), "html.parser")

            # Seletor Amplo: Tenta capturar as caixas de review por classes comuns do ecossistema Steam
            review_boxes = soup.find_all("div", class_="review_box")
            if not review_boxes:
                review_boxes = soup.find_all(
                    "div", class_="review_history_row"
                )
            if not review_boxes:
                review_boxes = soup.find_all(
                    "div", class_=["left_column", "right_column"]
                )

            # Se ainda assim não achar blocos isolados, tenta buscar todas as divs de conteúdo
            if not review_boxes:
                review_boxes = soup.find_all("div", class_="content")

            achou_na_pagina = False

            for box in review_boxes:
                # 1. Extração do Nome do Jogo e App ID através dos links da loja presentes no bloco
                game_link_tag = box.find(
                    "a", href=re.compile(r"store\.steampowered\.com/app/\d+")
                )
                if not game_link_tag:
                    # Tenta seletor de link alternativo para links internos de recomendação
                    game_link_tag = box.find(
                        "a", href=re.compile(r"recommended/\d+")
                    )

                if not game_link_tag:
                    continue

                href = game_link_tag["href"]
                nome_jogo = game_link_tag.get_text().strip()

                # Ignora textos institucionais globais do menu da Steam
                if nome_jogo in [
                    "Store",
                    "Community",
                    "About",
                    "Support",
                    "Suporte",
                    "Loja",
                    "Comunidade",
                ]:
                    continue

                # Extrai o ID numérico do jogo
                match_id = re.search(r"/(\d+)", href)
                app_id = match_id.group(1) if match_id else "Desconhecido"

                if app_id in jogos_processados:
                    continue

                # 2. Extração do Sentimento (Recomendado vs Não Recomendado)
                # Procura por textos de recomendação nos cabeçalhos ou no próprio bloco
                box_text = box.get_text()
                if (
                    "Não recomendado" in box_text
                    or "Not Recommended" in box_text
                ):
                    sentimento = "Negativo"
                else:
                    sentimento = "Positivo"

                # 3. Extração do Texto do Comentário escrito por você
                # Tenta pegar o parágrafo ou o texto da div interna de conteúdo limpo
                inner_content = box.find("div", class_="content")
                if inner_content:
                    comentario = inner_content.get_text().strip()
                else:
                    comentario = box.get_text().strip()

                # Limpeza final do comentário para remover especificações de PC e quebras de linhas
                comentario = re.sub(r"\s+", " ", comentario)
                # Corta textos repetidos do título se eles vazarem para o comentário
                comentario = comentario.replace(nome_jogo, "").strip()

                dados_planilha.append([nome_jogo, app_id, sentimento, comentario])
                jogos_processados.add(app_id)
                achou_na_pagina = True

            if achou_na_pagina:
                paginas_com_sucesso += 1
                # Mostra o progresso no terminal a cada 20 páginas para não poluir
                if paginas_com_sucesso % 20 == 0:
                    print(
                        f"[INFO] {paginas_com_sucesso} páginas processadas com sucesso..."
                    )
            else:
                print(
                    f"[AVISO] Nenhum dado estruturado extraído do arquivo: '{arquivo}'."
                )
                paginas_com_erro += 1

        except Exception as e:
            print(f"[ERRO CRÍTICO] Falha ao ler o arquivo '{arquivo}': {e}")
            paginas_com_erro += 1

    # SALVAMENTO SALVA-VIDAS: Grava tudo o que foi coletado até o momento do erro
    if dados_planilha:
        with open(OUTPUT_CSV, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["Nome do Jogo", "ID do Jogo", "Sentiment", "Comentário"]
            )
            for linha in dados_planilha:
                writer.writerow(linha)

        print("\n==========================================================")
        print(
            f"[SUCESSO PARCIAL] Arquivo '{OUTPUT_CSV}' gerado com dados recuperados."
        )
        print(f" -> Páginas lidas com sucesso: {paginas_com_sucesso}")
        print(f" -> Páginas que falharam/vazias: {paginas_com_erro}")
        print(f" -> Total de jogos salvos na planilha: {len(dados_planilha)}")
        print("==========================================================\n")
    else:
        print(
            "\n[ERRO] Nenhum jogo pôde ser extraído de nenhum dos arquivos HTML."
        )


if __name__ == "__main__":
    extrair_dados_completos()
