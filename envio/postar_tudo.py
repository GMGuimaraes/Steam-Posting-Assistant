"""
postar_tudo.py - publica artworks na Comunidade Steam para autoria propria, com modo assistido.

Resumo do comportamento:
- manifesto.json: cada imagem tem comunidades CANDIDATAS. Tenta uma a uma ate META_POR_IMAGEM.
- Sem upload por falta do jogo: resgata o jogo SE for gratuito e seguro; pago e pulado.
  Acabaram as candidatas: busca outros jogos gratuitos pelos "termos" do manifesto.
- NAO REPOSTA: guarda o hash (sha256) de cada imagem em historico_postados.json e pula
  qualquer combinacao imagem+jogo ja publicada (mesmo se o arquivo for renomeado).
- Depois de cada publicacao: curte e favorita o item, fechando popups.
- Erros inesperados nao derrubam o script: ele registra e segue para a proxima.
- Os arquivos originais sao preservados; a exclusao automatica esta desativada.
- A certificacao de autoria so pode ser confirmada quando for verdadeira; permissao de repostagem nao equivale a autoria.
- Pausas mostram contagem regressiva no log (nao e travamento).

O envio para a Central da Comunidade usa o botao "Salvar arte na Central da Comunidade"
(SubmitItem(false)); o botao de salvar apenas no perfil nunca e usado. O modo assistido
preenche o formulario, mas espera o usuario confirmar manualmente. So confirme autoria se
voce puder afirmar honestamente que e o criador original; permissao para repostar nao basta.
Uso: python postar_tudo.py manifesto.json
"""
import json, re, sys, time, random, datetime, subprocess, hashlib
import urllib.parse, urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

CONFIRMADO_COMUNIDADE = True   # botao 'Salvar arte na Central da Comunidade' = SubmitItem( false )
PERFIL = Path.home() / "SteamPost-perfil"
META_POR_IMAGEM = 10
MAX_POR_EXECUCAO = 10
MAX_RESGATES = 5
PAUSA_MIN, PAUSA_MAX = 120, 300
PAUSA_CURTA = (4, 10)
MAX_FALHAS_SEGUIDAS = 8
MAX_TENTATIVAS_POR_ALVO = 2
VISIBILIDADE = "0"            # 0 = publico, 1 = so amigos, 2 = privado
LOG = Path(__file__).with_name("postar.log")
ESTADO = {"assistido": False}


def log(msg):
    linha = f"[{datetime.datetime.now():%H:%M:%S}] {msg}"
    print(linha, flush=True)
    try:
        with LOG.open("a", encoding="utf-8") as f:
            f.write(linha + "\n")
    except Exception:
        pass


def pausar(segundos, motivo):
    log(f"{motivo}: aguardando {segundos}s (nao travou, e a pausa entre postagens)...")
    restante = segundos
    while restante > 0:
        passo = min(30, restante)
        time.sleep(passo)
        restante -= passo
        if restante > 0:
            log(f"... faltam {restante}s")


def http_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def sha256_arquivo(caminho):
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloco)
    return h.hexdigest()


def ir(pagina, url):
    try:
        pagina.goto(url, wait_until="domcontentloaded", timeout=120000)
    except Exception as e:
        log(f"Aviso: pagina lenta ou falhou ({type(e).__name__}); seguindo.")


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


# ---------- Steam: busca e posse de jogos ----------
def buscar_appid(nome):
    url = "https://store.steampowered.com/api/storesearch/?" + urllib.parse.urlencode(
        {"term": nome, "l": "english", "cc": "us"})
    try:
        itens = http_json(url).get("items", [])
    except Exception as e:
        log(f"Busca de '{nome}' falhou: {e}")
        return None
    if not itens:
        log(f"Nenhum resultado para '{nome}'.")
        return None
    topo = itens[0]
    if nome.lower() not in topo["name"].lower():
        log(f"Busca '{nome}' trouxe '{topo['name']}' - diferente, ignorando por seguranca.")
        return None
    log(f"Busca '{nome}' -> {topo['name']} (appid {topo['id']})")
    return topo["id"]


def detalhes_app(appid):
    try:
        d = http_json(f"https://store.steampowered.com/api/appdetails?appids={appid}&cc=us&l=english")
        r = d.get(str(appid), {})
        return r.get("data") if r.get("success") else None
    except Exception as e:
        log(f"appdetails {appid} falhou: {e}")
        return None


def app_seguro(dados):
    ids = set((dados.get("content_descriptors") or {}).get("ids") or [])
    try:
        idade = int(dados.get("required_age") or 0)
    except Exception:
        idade = 0
    return not (ids & {1, 3, 4}) and idade < 18


def possui(pagina, appid):
    ir(pagina, f"https://store.steampowered.com/app/{appid}/?l=english")
    pagina.wait_for_timeout(2500)
    if "agecheck" in pagina.url:
        return None
    try:
        return pagina.locator(".game_area_already_owned").count() > 0
    except Exception:
        return False


JS_RESGATE = """async (appid) => {
  const sid = window.g_sessionID || ((document.cookie.match(/sessionid=([^;]+)/) || [])[1]);
  const r = await fetch('/freelicense/addfreelicense/' + appid, {
    method: 'POST', credentials: 'include',
    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
    body: 'sessionid=' + encodeURIComponent(sid)});
  return r.status + ' ' + (await r.text()).replace(/\\s+/g, ' ').slice(0, 160);
}"""


def resgatar_gratuito(pagina, appid, nome):
    dados = detalhes_app(appid)
    if not dados or dados.get("type") != "game" or not dados.get("is_free"):
        return False, "jogo pago (ou nao e um jogo) e nao possuido"
    if not app_seguro(dados):
        return False, "conteudo adulto, ignorado"
    dono = possui(pagina, appid)
    if dono:
        return False, "ja possui, mas sem formulario de upload"
    if dono is None:
        return False, "pagina da loja com trava de idade"
    log(f"Resgatando jogo gratuito: {nome} ({appid})")
    try:
        res = pagina.evaluate(JS_RESGATE, appid)
    except Exception as e:
        return False, f"resgate falhou: {type(e).__name__}"
    pagina.wait_for_timeout(3000)
    if possui(pagina, appid):
        log("Resgate confirmado.")
        return True, "resgatado"
    return False, "resgate nao confirmado: " + res[:140]


# ---------- Steam: login, popups e publicacao ----------
def garantir_login(pagina):
    ir(pagina, "https://steamcommunity.com/my/")
    pagina.wait_for_timeout(3000)
    if "/login" in pagina.url:
        log("Sem sessao. Faca login no navegador aberto (ate 5 minutos)...")
        try:
            pagina.wait_for_url(re.compile(r"steamcommunity\.com/(id|profiles)/"), timeout=300000)
        except Exception:
            return False
    return True


def fechar_popups(pagina):
    seletores = [".newmodal .newmodal_close", ".newmodal_buttons .btn_green_steamui",
                 ".newmodal_buttons .btn_grey_steamui", ".newmodal .btn_grey_steamui",
                 ".modal_close", "button[aria-label=Close]", "button[aria-label=Fechar]"]
    for _ in range(3):
        fechou = False
        for sel in seletores:
            try:
                loc = pagina.locator(sel).first
                if loc.count() and loc.is_visible():
                    loc.click(timeout=3000)
                    fechou = True
                    pagina.wait_for_timeout(600)
                    break
            except Exception:
                continue
        if not fechou:
            break
    try:
        pagina.keyboard.press("Escape")
    except Exception:
        pass


def clicar_primeiro(pagina, seletores, timeout=5000):
    for sel in seletores:
        try:
            loc = pagina.locator(sel).first
            if loc.count() and loc.is_visible():
                loc.click(timeout=timeout)
                return True
        except Exception:
            continue
    return False


def curtir_e_favoritar(pagina, id_item, pasta_erros):
    try:
        pagina.wait_for_timeout(2000)
        fechar_popups(pagina)
        curtiu = clicar_primeiro(pagina, ["#VoteUpBtn", "a[id*=VoteUp]", "[onclick*=VoteUp]"])
        pagina.wait_for_timeout(1500)
        fechar_popups(pagina)
        fav = clicar_primeiro(pagina, ["#FavoriteItemBtn", "a[id*=Favorite]", "[onclick*=Favorite]"])
        if not fav:
            try:
                pagina.get_by_text(re.compile(r"^\s*\+?\s*(favoritos?|favorite)\s*$", re.I)).first.click(timeout=5000)
                fav = True
            except Exception:
                pass
        pagina.wait_for_timeout(1500)
        fechar_popups(pagina)
        log(f"Curtir: {curtiu} | Favoritar: {fav}")
        if not (curtiu and fav):
            salvar_diagnostico(pagina, pasta_erros, f"item{id_item}-interacao")
    except Exception as e:
        log(f"Curtir/favoritar falhou sem afetar o resto: {type(e).__name__}")


def motivo_pagina(pagina):
    try:
        texto = re.sub(r"\s+", " ", pagina.inner_text("body", timeout=3000)).strip()[:160]
        return f"titulo='{pagina.title()}' texto='{texto}'"
    except Exception:
        return "sem detalhes da pagina"


GRUPOS_BOTAO = [
    re.compile(r"save|salvar|publish|publicar", re.I),
    re.compile(r"submit|enviar|continue|continuar|concluir|upload|carregar", re.I),
]
JS_TEXTO = "e => (e.innerText || e.value || '').trim()"


def achar_botao(pagina):
    seletores = ["#SubmitItemBtn", "a[class*=btn_]", "input[type=submit]", "button", "a[onclick*=Submit]"]
    for grupo in GRUPOS_BOTAO:
        for sel in seletores:
            try:
                locs = pagina.locator(sel)
                for i in range(min(locs.count(), 25)):
                    l = locs.nth(i)
                    if not l.is_visible():
                        continue
                    txt = l.evaluate(JS_TEXTO)
                    if sel == "#SubmitItemBtn" or grupo.search(txt):
                        return l, f"{sel} | '{txt}'"
            except Exception:
                continue
    return None, None


REGEX_COMUNIDADE = re.compile(r"SubmitItem\(\s*false\s*\)")


def achar_botao_comunidade(pagina):
    # "Salvar arte na Central da Comunidade" = SubmitItem( false ).
    # "Salvar arte no meu perfil" = SubmitItem( true ) e NUNCA deve ser usado.
    try:
        locs = pagina.locator("a[onclick*='SubmitItem']")
        for i in range(locs.count()):
            l = locs.nth(i)
            onclick = l.get_attribute("onclick") or ""
            if REGEX_COMUNIDADE.search(onclick) and l.is_visible():
                return l, f"onclick={onclick.strip()} | '{l.evaluate(JS_TEXTO)}'"
    except Exception:
        pass
    return None, None


JS_SUBMETER = """() => {
  const f = [...document.forms].find(f => f.querySelector('input[type=file]'));
  if (!f) return 'sem form';
  if (f.requestSubmit) f.requestSubmit(); else f.submit();
  return 'ok';
}"""
JS_LISTAR = """() => [...document.querySelectorAll('a,button,input,select,textarea,[onclick],[class*=btn]')]
  .filter(e => e.offsetParent !== null).slice(0, 120)
  .map(e => [e.tagName, e.id, (e.className || '').toString().slice(0, 50), e.type || '',
     (e.innerText || e.value || '').trim().slice(0, 50),
     (e.getAttribute('onclick') || '').slice(0, 60)].join(' | ')).join('\\n')"""


def salvar_diagnostico(pagina, pasta_erros, rotulo):
    pasta_erros.mkdir(exist_ok=True)
    base = pasta_erros / f"{datetime.datetime.now():%Y%m%d-%H%M%S}-{rotulo}"
    try:
        pagina.screenshot(path=str(base) + ".png", full_page=True)
    except Exception:
        pass
    try:
        Path(str(base) + "-elementos.txt").write_text(pagina.evaluate(JS_LISTAR), encoding="utf-8")
    except Exception:
        pass
    return base.name


def aguardar_publicacao(pagina, ms):
    try:
        pagina.wait_for_url(re.compile(r"sharedfiles/filedetails"), timeout=ms)
        return True
    except Exception:
        return False


def concluir_assistido(pagina, pasta_erros, rotulo):
    # Modo assistido: o USUARIO marca a certificacao de autoria e clica em salvar.
    log("MODO ASSISTIDO: formulario preenchido. So marque a certificacao se puder afirmar que e o criador original; depois clique em "
        "'Salvar arte na Central da Comunidade'. Aguardando ate 5 minutos...")
    try:
        pagina.bring_to_front()
    except Exception:
        pass
    if aguardar_publicacao(pagina, 300000):
        return pagina.url, None, False
    return None, "assistido: nao concluido em 5 minutos (pulado)", False


def publicar(pagina, imagem, titulo, descricao, pasta_erros, rotulo):
    """Retorna (url, erro, incerto)."""
    try:
        pagina.wait_for_selector("input[type=file]", state="attached", timeout=25000)
    except Exception:
        return None, "sem formulario de upload nesta comunidade: " + motivo_pagina(pagina), False
    tentar(pagina, ["input[type=file]"], lambda l: l.set_input_files(str(imagem)))
    pagina.wait_for_timeout(1500)
    tentar(pagina, ["#title", "input[name=title]"], lambda l: l.fill(titulo[:100]))
    tentar(pagina, ["#description", "textarea[name=description]"], lambda l: l.fill(descricao))
    tentar(pagina, [f"input[name=visibility][value='{VISIBILIDADE}']"], lambda l: l.check())
    pagina.wait_for_timeout(1500)
    if ESTADO["assistido"]:
        return concluir_assistido(pagina, pasta_erros, rotulo)
    marcou = tentar(pagina, ["#agree_terms", "input[name=agree_terms]"], lambda l: l.check())
    if not marcou:
        try:
            pagina.get_by_label(re.compile(r"agree|concordo|acepto", re.I)).first.check(timeout=4000)
            marcou = True
        except Exception:
            pass
    log(f"Checkbox de aceite marcado: {marcou}")
    botao, desc = achar_botao_comunidade(pagina)
    if botao:
        log(f"Clicando em: {desc}")
        try:
            botao.click(timeout=15000, no_wait_after=True)
        except Exception as e:
            log(f"Clique demorou/falhou ({type(e).__name__}); verificando se a publicacao saiu mesmo assim.")
    else:
        try:
            raise RuntimeError("botao da Central da Comunidade nao encontrado")
        except Exception:
            nome = salvar_diagnostico(pagina, pasta_erros, rotulo)
            return None, f"botao Publicar nao encontrado (diagnostico {nome})", False
    if aguardar_publicacao(pagina, 60000):
        return pagina.url, None, False
    nome = salvar_diagnostico(pagina, pasta_erros, rotulo)
    return None, (f"nao confirmou a publicacao - VERIFIQUE MANUALMENTE (diagnostico {nome}): "
                  + motivo_pagina(pagina)), True


# ---------- candidatas extras, historico e lixeira ----------
def expandir_alvos(item):
    existentes = {a["appid"] for a in item["alvos"] if a.get("appid")}
    existentes |= {a["nome"].lower() for a in item["alvos"]}
    novos = 0
    for termo in item.get("termos", []):
        url = "https://store.steampowered.com/api/storesearch/?" + urllib.parse.urlencode(
            {"term": termo, "l": "english", "cc": "us"})
        try:
            itens = http_json(url).get("items", [])
        except Exception as e:
            log(f"Busca por tema '{termo}' falhou: {e}")
            continue
        for it in itens:
            if it.get("type") != "app" or ((it.get("price") or {}).get("final") or 0) > 0:
                continue
            if it["id"] in existentes or it["name"].lower() in existentes:
                continue
            item["alvos"].append({"nome": it["name"], "appid": it["id"], "origem": "busca"})
            existentes.add(it["id"])
            novos += 1
            if novos >= 6:
                return novos
    return novos


def excluir_para_lixeira(caminho):
    try:
        caminho = Path(caminho)
        if not caminho.exists():
            return True
        sq = chr(39)
        ps = ("Add-Type -AssemblyName Microsoft.VisualBasic; "
              "[Microsoft.VisualBasic.FileIO.FileSystem]::DeleteFile("
              + sq + str(caminho).replace(sq, sq * 2) + sq
              + ", 'OnlyErrorDialogs', 'SendToRecycleBin')")
        subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                       capture_output=True, text=True, timeout=60)
        return not caminho.exists()
    except Exception as e:
        log(f"Falha ao enviar para a Lixeira: {e}")
        return False


def salvar_json(caminho, dados):
    """Grava JSON de forma atomica para preservar manifesto/historico em caso de falha."""
    caminho = Path(caminho)
    temporario = caminho.with_name(caminho.name + ".tmp")
    conteudo = json.dumps(dados, ensure_ascii=False, indent=2)
    temporario.write_text(conteudo, encoding="utf-8")
    temporario.replace(caminho)


def main(manifesto_path):
    if not CONFIRMADO_COMUNIDADE:
        print("\nPARADO DE PROPOSITO: o envio para a COMUNIDADE ainda nao foi configurado.\n"
              "O botao atual salva a arte so no perfil. Rode inspecionar_form.bat e passe a\n"
              "pasta 'erros' para quem estiver ajudando; depois mude CONFIRMADO_COMUNIDADE.\n")
        return
    mpath = Path(manifesto_path).resolve()
    base = mpath.parent
    hpath = base / "historico_postados.json"
    itens = json.loads(mpath.read_text(encoding="utf-8"))
    hist = json.loads(hpath.read_text(encoding="utf-8")) if hpath.exists() else {}
    log("=== Inicio ===")
    log("ATENCAO: so publique conteudo cuja autoria possa ser certificada honestamente. Permissao de repostagem nao equivale a autoria.")
    feitos = falhas = resgates = 0
    vistos = set()
    try:
        with sync_playwright() as p:
            ctx = p.chromium.launch_persistent_context(str(PERFIL), headless=False)
            pagina = ctx.new_page()
            if not garantir_login(pagina):
                log("Login nao concluido. Encerrando.")
                ctx.close()
                return
            for item in itens:
                imagem = (base / item["arquivo"]).resolve()
                if item.get("arquivo_excluido"):
                    continue
                if not imagem.exists():
                    log(f"Arquivo nao existe: {imagem}")
                    continue
                ESTADO["assistido"] = bool(item.get("modo_assistido")) and not item.get("autoria_propria")
                if not (item.get("autoria_propria") or item.get("modo_assistido")):
                    log(f"Pulando '{imagem.name}': defina no manifesto 'autoria_propria': true (arte sua) "
                        "ou 'modo_assistido': true (voce mesmo marca a caixa de certificacao).")
                    continue
                h = sha256_arquivo(imagem)
                item["sha256"] = h
                if h in vistos:
                    log(f"Imagem repetida no manifesto, ignorando: {imagem.name}")
                    continue
                vistos.add(h)
                reg = hist.setdefault(h, {"arquivo": imagem.name, "appids": {}})
                for a in item["alvos"]:
                    if a.get("postado") and a.get("appid"):
                        reg["appids"].setdefault(str(a["appid"]), a.get("url", ""))
                    elif a.get("appid") and str(a["appid"]) in reg["appids"]:
                        a.update({"postado": True, "url": reg["appids"][str(a["appid"])],
                                  "obs": "ja postada antes (historico)"})
                salvar_json(hpath, hist)
                ok_img = sum(1 for a in item["alvos"] if a.get("postado"))
                extras = item.get("titulos_extra") or [item["titulo"]]
                concluida = False
                while ok_img < META_POR_IMAGEM and feitos < MAX_POR_EXECUCAO and falhas < MAX_FALHAS_SEGUIDAS:
                    alvo = next((a for a in item["alvos"] if not a.get("postado")
                                 and a.get("tentativas", 0) < MAX_TENTATIVAS_POR_ALVO), None)
                    if alvo is None:
                        if expandir_alvos(item) == 0:
                            log("Sem mais candidatas para esta imagem.")
                            concluida = True
                            break
                        salvar_json(mpath, itens)
                        continue
                    try:
                        alvo["tentativas"] = alvo.get("tentativas", 0) + 1
                        appid = alvo.get("appid") or buscar_appid(alvo["nome"])
                        if not appid:
                            alvo["erro"] = "appid nao encontrado"
                            salvar_json(mpath, itens)
                            continue
                        alvo["appid"] = appid
                        if str(appid) in reg["appids"]:
                            alvo.update({"postado": True, "url": reg["appids"][str(appid)],
                                         "obs": "ja postada antes (historico)"})
                            ok_img += 1
                            log(f"Ja postada antes em {alvo['nome']}; pulando.")
                            salvar_json(mpath, itens)
                            continue
                        if alvo.get("origem") == "busca":
                            dados = detalhes_app(appid)
                            if not dados or dados.get("type") != "game" or not app_seguro(dados):
                                alvo["erro"] = "ignorado (nao e jogo, ou conteudo adulto)"
                                alvo["tentativas"] = MAX_TENTATIVAS_POR_ALVO
                                salvar_json(mpath, itens)
                                continue
                        titulo = alvo.get("titulo") or (
                            extras[len(item["alvos"]) % len(extras)]
                            if alvo.get("origem") == "busca" else item["titulo"])
                        url_up = f"https://steamcommunity.com/sharedfiles/edititem/{appid}/3/"
                        log(f"Postando '{imagem.name}' em {alvo['nome']} (appid {appid})")
                        ir(pagina, url_up)
                        url, erro, incerto = publicar(pagina, imagem, titulo, item["descricao"],
                                                      base / "erros", str(appid))
                        if erro and erro.startswith("sem formulario") and resgates < MAX_RESGATES:
                            resgatou, nota = resgatar_gratuito(pagina, appid, alvo["nome"])
                            if resgatou:
                                resgates += 1
                                ir(pagina, url_up)
                                url, erro, incerto = publicar(pagina, imagem, titulo, item["descricao"],
                                                              base / "erros", str(appid))
                            else:
                                erro = f"{erro[:60]}... | {nota}"
                        if url:
                            alvo.update({"postado": True, "url": url})
                            alvo.pop("erro", None)
                            reg["appids"][str(appid)] = url
                            salvar_json(hpath, hist)
                            feitos += 1
                            ok_img += 1
                            falhas = 0
                            log(f"OK: {url}")
                            salvar_json(mpath, itens)
                            m = re.search(r"id=(\d+)", url)
                            curtir_e_favoritar(pagina, m.group(1) if m else "x", base / "erros")
                            if feitos < MAX_POR_EXECUCAO and ok_img < META_POR_IMAGEM:
                                pausar(random.randint(PAUSA_MIN, PAUSA_MAX), "Proxima postagem")
                        else:
                            alvo["erro"] = erro
                            if incerto:
                                alvo["tentativas"] = MAX_TENTATIVAS_POR_ALVO
                            if not erro.startswith(("sem formulario", "assistido")) \
                                    and "ja possui" not in erro and "pago" not in erro:
                                falhas += 1
                            log(f"FALHA/PULO: {erro}")
                            salvar_json(mpath, itens)
                            time.sleep(random.randint(*PAUSA_CURTA))
                    except Exception as e:
                        alvo["erro"] = f"erro inesperado: {type(e).__name__}: {str(e)[:150]}"
                        falhas += 1
                        log(f"ERRO INESPERADO (seguindo em frente): {alvo['erro']}")
                        salvar_json(mpath, itens)
                        try:
                            if pagina.is_closed():
                                pagina = ctx.new_page()
                        except Exception:
                            pagina = ctx.new_page()
                        time.sleep(random.randint(*PAUSA_CURTA))
                if ok_img >= META_POR_IMAGEM:
                    concluida = True
                incerta = any(str(a.get("erro", "")).startswith("nao confirmou") and not a.get("postado")
                              for a in item["alvos"])
                # Protecao: nunca apagar imagens automaticamente.
                # O estado "OK" atual pode apontar para uma arte salva apenas no perfil,
                # portanto nao comprova publicacao na comunidade nem autoriza exclusao.
                if concluida and not item.get("arquivo_excluido"):
                    log(f"Arquivo preservado; exclusao automatica desativada: {imagem.name}")
            salvar_json(mpath, itens)
            ctx.close()
    except Exception as e:
        log(f"ERRO FATAL (progresso ja salvo no manifesto): {type(e).__name__}: {e}")
    log(f"=== Fim. Publicadas: {feitos}. Resgatados: {resgates}. Falhas seguidas ao parar: {falhas}. ===")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "manifesto.json")