"""
Envio SUPERVISIONADO de artwork para a Comunidade Steam.
- Abre um navegador (perfil proprio, a sessao fica salva).
- Voce faz o login na Steam VOCE MESMO na primeira vez (Steam Guard incluso).
- Para cada alvo: abre a pagina de upload, anexa a imagem, preenche titulo e
  descricao e ESPERA voce revisar e clicar em Publicar. Nenhuma senha passa por aqui.
- ATENCAO: o formulario da Steam muda; os seletores abaixo NAO foram testados
  contra o site real. Se algum campo nao for preenchido, preencha na mao.
Uso: python enviar_artwork.py manifesto.json
"""
import json, sys, time, random
from pathlib import Path
from playwright.sync_api import sync_playwright

PERFIL = Path.home() / "SteamPost-perfil"
PAUSA_MIN, PAUSA_MAX = 90, 180  # segundos entre envios (evita parecer spam)


def ir(pagina, url):
    # Nao espera o evento 'load' completo e nao derruba o script se demorar.
    try:
        pagina.goto(url, wait_until="domcontentloaded", timeout=120000)
    except Exception as e:
        print(f"Aviso: a pagina demorou ou falhou ao carregar ({type(e).__name__}). "
              "Se ela estiver visivel no navegador, siga normalmente.")


def tentar(pagina, seletores, acao):
    for sel in seletores:
        try:
            loc = pagina.locator(sel).first
            if loc.count():
                acao(loc)
                return True
        except Exception:
            continue
    return False


def main(manifesto_path):
    base = Path(manifesto_path).resolve().parent
    itens = json.loads(Path(manifesto_path).read_text(encoding="utf-8"))
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(str(PERFIL), headless=False)
        pagina = ctx.new_page()
        ir(pagina, "https://steamcommunity.com/login/home/")
        input("Faca login na Steam no navegador aberto e aperte ENTER aqui... ")
        for item in itens:
            imagem = (base / item["arquivo"]).resolve()
            for alvo in item["alvos"]:
                print(f"\n== {imagem.name} -> {alvo['nome']}")
                url_upload = alvo.get("url_upload")
                if not url_upload and alvo.get("appid"):
                    url_upload = f"https://steamcommunity.com/sharedfiles/edititem/{alvo['appid']}/3/"
                if not url_upload:
                    print("Alvo sem AppID ou URL de upload; pulando.")
                    continue
                ir(pagina, url_upload)
                tentar(pagina, ["input[type=file]"], lambda l: l.set_input_files(str(imagem)))
                tentar(pagina, ["#title", "input[name=title]"], lambda l: l.fill(alvo.get("titulo", item["titulo"])))
                tentar(pagina, ["#description", "textarea[name=description]"], lambda l: l.fill(item["descricao"]))
                print("Revise o formulario. So confirme autoria se voce for o criador original; permissao para repostar nao equivale a autoria.")
                print("Clique em Publicar somente se todas as declaracoes da Steam forem verdadeiras.")
                resp = input("ENTER = proximo | 'p' = pular | 's' = sair: ").strip().lower()
                if resp == "s":
                    ctx.close(); return
                if resp != "p":
                    time.sleep(random.randint(PAUSA_MIN, PAUSA_MAX))
        ctx.close()


if __name__ == "__main__":
    main(sys.argv[1])