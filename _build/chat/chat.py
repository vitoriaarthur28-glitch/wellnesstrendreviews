"""Chat com especialista: só na versão Google Ads (/<slug>-review/). Ver CLAUDE.md, seção 13.

render(slug, affiliate) devolve o HTML do chat (<style> + HTML + <script>) ou "" se o produto não tem _build/<slug>/chat.json.
Recusa (SystemExit) quando algo não confere, para nunca publicar um chat errado:
- "nicho" que não está em _build/chat/especialistas.json;
- especialista (nome, título, foto) diferente da linha do nicho: a especialista é SEMPRE a do nicho do produto;
- LINK_AFILIADO diferente do link da página;
- campo faltando, conta de preço errada ou imagem de pacote que não existe.

Idioma: produto com "lang": "de" em PAGES usa _build/chat/de/ (chat.html e chat.js em alemão) e especialistas-de.json;
o chat.css é o mesmo. Sem "lang", tudo como sempre (inglês). Ver CLAUDE.md, seção 14.

Teste local de um produto (sem publicar):  python _build/chat/chat.py <slug>
O código do chat (chat.css, chat.html, chat.js) é desenvolvido e testado no projeto C:\\claude\\chat-especialista e copiado
para cá; não edite só aqui.
"""
import html as _html
import json
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ROOT = AQUI.parent.parent
HTML_SUFIXOS = ("_CORPO", "_FRETE")
# links vão crus, iguais aos da página (o audit compara href="{affiliate}"; com "&" no link o escape quebrava a igualdade)
HTML_EXATOS = {"ALERTA_TEXTO", "LINK_AFILIADO", "LINK_PACOTE_1", "LINK_PACOTE_2", "LINK_PACOTE_3"}


def _erro(slug, msg):
    sys.exit(f"[chat {slug}] {msg}")


def _opcionais(texto, opc):
    def tira(t, marca, manter):
        padrao = re.compile(r"[ \t]*<!-- %s -->\n?(.*?)[ \t]*<!-- /%s -->\n?" % (re.escape(marca), re.escape(marca)), re.S)
        return padrao.sub(lambda m: m.group(1) if manter else "", t)
    precos, deps = opc.get("PRECOS", True), opc.get("DEPOIMENTOS", True)
    texto = tira(texto, "OPCIONAL:PRECOS", precos)
    texto = tira(texto, "SE_NAO:PRECOS", not precos)
    return tira(texto, "OPCIONAL:DEPOIMENTOS", deps)


def _num(s, idioma="en"):
    s = str(s)
    if idioma == "de":  # 1.234,56 -> 1234.56
        s = s.replace(".", "").replace(",", ".")
    return float(re.sub(r"[^\d.]", "", s) or 0)


def _pasta(idioma):
    return AQUI if idioma == "en" else AQUI / idioma


def _tabela(idioma):
    nome = "especialistas.json" if idioma == "en" else f"especialistas-{idioma}.json"
    return json.loads((AQUI / nome).read_text(encoding="utf-8"))


def _conferir(slug, d, v, affiliate, idioma="en"):
    tabela = _tabela(idioma)
    nicho = d.get("nicho")
    if nicho not in tabela:
        _erro(slug, f'"nicho" ausente ou desconhecido: {nicho!r}. Nichos válidos: {", ".join(sorted(tabela))}')
    esp = tabela[nicho]
    for campo, chave in (("CHAT_NOME", "nome"), ("CHAT_ESPECIALIDADE", "especialidade"), ("CHAT_FOTO", "foto")):
        if v.get(campo) != esp[chave]:
            _erro(slug, f"{campo} = {v.get(campo)!r}, mas o nicho {nicho} usa {esp[chave]!r}")
    if not (ROOT / "public" / esp["foto"].lstrip("/")).exists():
        _erro(slug, f"foto da especialista não existe em public{esp['foto']}")
    if v.get("LINK_AFILIADO") != affiliate:
        _erro(slug, f"LINK_AFILIADO diferente do link da página ({v.get('LINK_AFILIADO')} != {affiliate})")
    if d.get("opcionais", {}).get("PRECOS", True):
        for n in (1, 2, 3):
            fr = int(re.match(r"\d+", v[f"PACOTE_{n}_NOME"]).group())
            un, de, tot = (_num(v[f"PACOTE_{n}_{c}"], idioma) for c in ("PRECO_UN", "DE", "TOTAL"))
            if round(un * fr, 2) != round(tot, 2) or (str(v[f"PACOTE_{n}_DE"]).strip() and de <= tot):
                _erro(slug, f"pacote {n}: {fr} x {un} = {un * fr}, total {tot}, de {de}")
            img = v[f"PACOTE_{n}_IMG"]
            if not (ROOT / "public" / f"{slug}-review" / img).resolve().exists():
                _erro(slug, f"imagem do pacote {n} não existe: {img}")


def render(slug, affiliate, idioma="en"):
    arq = ROOT / "_build" / slug / "chat.json"
    if not arq.exists():
        return ""
    d = json.loads(arq.read_text(encoding="utf-8"))
    v = dict(d["valores"])
    for n in (1, 2, 3):
        v.setdefault(f"LINK_PACOTE_{n}", v.get("LINK_AFILIADO", ""))
    if d.get("idioma", "en") != idioma:
        _erro(slug, f'chat.json é "{d.get("idioma", "en")}" mas a página é "{idioma}": o chat sai no idioma da página')
    _conferir(slug, d, v, affiliate, idioma)
    h = (_pasta(idioma) / "chat.html").read_text(encoding="utf-8")
    h = _opcionais(h[h.index("-->") + 3:].lstrip("\n"), d.get("opcionais", {}))
    css = (AQUI / "chat.css").read_text(encoding="utf-8")
    faltam = []

    def troca(m):
        k = m.group(1)
        if k not in v:
            faltam.append(k)
            return m.group(0)
        x = str(v[k])
        return x if (k in HTML_EXATOS or k.endswith(HTML_SUFIXOS)) else _html.escape(x, quote=True)

    h = re.sub(r"\{\{([A-Z0-9_]+)\}\}", troca, h)
    css = re.sub(r"\{\{([A-Z0-9_]+)\}\}", troca, css)
    if faltam:
        _erro(slug, "faltam campos no chat.json: " + ", ".join(sorted(set(faltam))))
    js = (_pasta(idioma) / "chat.js").read_text(encoding="utf-8")
    return f"<!-- CHAT COM ESPECIALISTA ({d['nicho']}) -->\n<style>\n{css}</style>\n{h}<script>\n{js}</script>\n"


if __name__ == "__main__":
    sys.path.insert(0, str(AQUI.parent))
    from build import PAGES  # noqa: E402
    s = sys.argv[1]
    out = render(s, PAGES[s]["affiliate"], PAGES[s].get("lang", "en"))
    print(f"ok: chat de {s} conferido ({len(out)} bytes)" if out else f"{s} não tem _build/{s}/chat.json")
