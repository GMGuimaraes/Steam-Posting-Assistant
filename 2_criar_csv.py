import csv
import os
import re
from bs4 import BeautifulSoup

INPUT_DIR = "html_pages"
OUTPUT_CSV = "todos_jogos_com_comentarios.csv"


def extrair_html_para_csv():
    if not os.path.exists(INPUT_DIR):
        print(
            f"Erro: A pasta '{INPUT_DIR}' não existe. Rode o primeiro script antes."
        )
        return

    arquivos = [f for f in os.listdir(INPUT_DIR) if f.endswith(".html")]
    if not arquivos:
        print("Nenhum arquivo HTML encontrado para processar.")
        return

    # Ordena as páginas numericamente para manter a ordem cronológica no CSV
    arquivos.sort(
        key=lambda f: int(re.search(r"\d+", f).group())
        if re.search(r"\d+", f)
        else 0
    )

    print(f"Processando {len(arquivos)} arquivos HTML encontrados...")

    jogos_extraidos = []

    for arquivo in arquivos:
        caminho_arquivo = os.path.join(INPUT_DIR, arquivo)
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        # Procura as linhas de jogos avaliados na tabela do histórico do perfil
        # A estrutura comum na aba de reviews do perfil usa a classe 'review_history_row' ou blocos de jogos
        game_rows = soup.find_all("div", class_="game_title")

        if not game_rows:
            # Seletor alternativo baseado em links de análises salvos no histórico da comunidade
            game_rows = soup.find_all("a", class_="header_link")

        for row in game_rows:
            nome_jogo = row.get_text().strip()
            if nome_jogo and nome_jogo not in jogos_extraidos:
                jogos_extraidos.append(nome_jogo)

    if not jogos_extraidos:
        print(
            "Não foi possível identificar nomes de jogos nos arquivos HTML salvos."
        )
        print(
            "Verifique se o primeiro script realmente capturou as páginas com você logado."
        )
        return

    # Salvando a lista unificada no arquivo CSV
    with open(OUTPUT_CSV, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Nome do Jogo"])  # Cabeçalho da tabela
        for jogo in jogos_extraidos:
            writer.writerow([jogo])

    print(
        f"Sucesso! Planilha criada com {len(jogos_extraidos)} jogos únicos em: {OUTPUT_CSV}"
    )


if __name__ == "__main__":
    extrair_html_para_csv()
