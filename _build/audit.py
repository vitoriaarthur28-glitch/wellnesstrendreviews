"""Audits the two live versions of a page against the rules in CLAUDE.md.

Usage: python _build/audit.py sodatide
Prints one line per check: PASS / FAIL / INFO. Exit code 1 if any check fails.
"""
import html
import json
import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import CHAT_ATIVO, DOMAIN, PAGES, plataforma_of  # noqa: E402

REF_WORDS = [266, 166, 192, 183, 201, 170, 213]  # /26-sodapeak-review/ copy blocks
UA = {"User-Agent": "Mozilla/5.0 (audit) Chrome/126.0"}
OFFER_WORDS = ["$", "price", "pricing", "discount", "free shipping", "per bottle", "coupon", "% off"]
# Páginas em alemão (CLAUDE.md, seção 14): mesmas regras, textos fixos em alemão. Produto sem "lang" = inglês.
OFFER_WORDS_DE = ["€", "eur", "euro", "preis", "preise", "rabatt", "gutschein", "versandkostenfrei", "kostenloser versand",
                  "pro flasche", "% rabatt", "sonderangebot"]


def fixed_texts(lang, n):
    """Títulos dos 8 blocos, as duas frases em vermelho, título dos cards e marcas do rodapé, por idioma."""
    if lang == "de":
        return {
            "heads": [f"Was ist {n} und wie wirkt es?", f"{n} Inhaltsstoffe", f"{n} Nebenwirkungen", f"{n} Dosierung",
                      f"{n} – Rückerstattung", f"{n} Kundenbewertungen", f"{n} – Wo kaufen?", f"Ist {n} Betrug?"],
            "n1": "Um sicherzugehen, dass Sie das Originalprodukt erhalten, besuchen die meisten Nutzer die offizielle Website.",
            "n2": f"Wer Produktdetails überprüfen oder die aktuelle Verfügbarkeit prüfen möchte, ist auf der offiziellen {n}-Website am sichersten aufgehoben.",
            "card": r"Verifizierter Kauf – [36] Flaschen", "card_plain": "Verifizierter Kauf",
            "footer": ("Affiliate-Hinweis", "Food and Drug Administration", "Copyright © | Alle Rechte vorbehalten"),
            "offer": OFFER_WORDS_DE, "html": 'lang="de-DE"'}
    return {
        "heads": [f"What Is {n} And How Does It Work?", f"{n} Ingredients", f"{n} Side Effects", f"{n} Dosage",
                  f"{n} – Refund Policy", f"{n} Customer Reviews", f"{n} – Where To Buy", f"Is {n} A Scam?"],
        "n1": "To ensure you’re getting the authentic product, most users choose to visit the official website.",
        "n2": f"For those who want to verify product details or check current availability, the official {n} website remains the safest option.",
        "card": r"Verified Purchase – [36] Bottles", "card_plain": "Verified Purchase",
        "footer": ("Affiliate disclosure", "Food and Drug Administration", "Copyright ©"),
        "offer": OFFER_WORDS, "html": 'lang="en-US"'}
fails = 0


def get(url):
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, dict((k.lower(), v) for k, v in r.headers.items()), r.read()
    except urllib.error.HTTPError as e:
        return e.code, {}, b""


def check(name, ok, detail=""):
    global fails
    if not ok:
        fails += 1
    print(f"{'PASS' if ok else 'FAIL'}  {name}{'  -> ' + str(detail) if detail else ''}")


def text_of(h):
    body = h[h.index("<header"):h.index("</footer>") + 9]
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", body))).strip()


def main(slug):
    p = PAGES[slug]
    aff = p["affiliate"]
    org_url = f"{DOMAIN}/{slug}-review-org/"
    ads_url = f"{DOMAIN}/{slug}-review/"
    so, ho, bo = get(org_url + "?audit=1")
    sa, ha, ba = get(ads_url + "?audit=1")
    o, a = bo.decode("utf-8"), ba.decode("utf-8")

    print("== both versions")
    check("both URLs answer 200", so == 200 and sa == 200, f"{so}/{sa}")
    check("copy identical in both versions", text_of(o) == text_of(a))
    lang = p.get("lang", "en")
    fx = fixed_texts(lang, p["name"])
    if p.get("tipo") == "ecom":
        # ecom (regra do usuário, 2026-10-19): Funktionen/Anwendung no lugar de Inhaltsstoffe/Dosierung, card sem
        # número de frascos, rodapé sem aviso de saúde/FDA, sem chat
        n_ = p["name"]
        fx["heads"][0] = f"Was ist {n_} und wie funktioniert es?" if lang == "de" else f"What Is {n_} And How Does It Work?"
        fx["heads"][1] = f"{n_} Funktionen" if lang == "de" else f"{n_} Features"
        fx["heads"][3] = f"{n_} Anwendung" if lang == "de" else f"{n_} How To Use"
        fx["card"] = fx["card_plain"]
        fx["footer"] = tuple(x for x in fx["footer"] if x != "Food and Drug Administration")
    check(f"page language is {lang}", fx["html"] in o and fx["html"] in a)
    low = text_of(o).lower()
    # whole words only, so "dropper bottle" is not read as "per bottle"
    found = [w for w in fx["offer"] if re.search(r"(?<![a-zäöüß])" + re.escape(w) + r"(?![a-zäöüß])", low)]
    check("no offer/price wording in the copy", not found, found)
    check("single <h1>", o.count("<h1") == 1 and a.count("<h1") == 1)
    heads = [html.unescape(re.sub(r"<[^>]+>", "", x)) for x in re.findall(r'<h2 class="band">(.*?)</h2>', o, re.S)]
    n = p["name"]
    expected = list(fx["heads"])
    if not p.get("testimonials", True):
        # official site has no testimonials: the page has no Customer Reviews block
        expected.remove(fx["heads"][5])
    ref_words = list(REF_WORDS)
    if not p.get("ingredients", True):
        # official site publishes no ingredient list or label: the page has no Ingredients block
        expected.remove(fx["heads"][1])
        ref_words.remove(REF_WORDS[1])
    if not p.get("side_effects", True):
        # official site has no side effects section: the page has no Side Effects block (user, 2026-10-19)
        expected.remove(fx["heads"][2])
        ref_words.remove(REF_WORDS[2])
    check(f"{len(expected)} section headings in the model's order", heads == expected, heads if heads != expected else "")
    words = []
    for sid, body in re.findall(r'<section id="([^"]+)">(.*?)</section>', o, re.S):
        m = re.search(r'<div class="copy">(.*?)</div>', body, re.S)
        if m:
            words.append(len(re.sub(r"<[^>]+>", " ", m.group(1)).split()))
    check("no copy block shorter than the reference", len(words) == len(ref_words) and all(w >= r for w, r in zip(words, ref_words)),
          f"{words} vs {ref_words}")
    n1 = f'<p class="official-notice">{fx["n1"]}</p>'
    n2 = f'<p class="official-notice">{fx["n2"]}</p>'
    check("both fixed red sentences present and literal", all(x in h for x in (n1, n2) for h in (o, a)))
    for label, h in (("org", o), ("ads", a)):
        anchors = re.findall(r"<a\b[^>]*>", h)
        check(f"{label}: every link is the exact affiliate link", all(f'href="{aff}"' in x for x in anchors), len(anchors))
        imgs = re.findall(r"<img\b[^>]*>", h)
        check(f"{label}: images have alt, width and height", all(all(k in i for k in ("alt=", "width=", "height=")) for i in imgs), len(imgs))
    cards = re.findall(r'<li class="review-card">(.*?)</li>', o, re.S)
    a_pagina = a.split("<!-- CHAT COM ESPECIALISTA")[0]  # o código do chat cita "#customer-reviews" para achar os cards
    if p.get("testimonials", True):
        # official site with fewer than 3 testimonials: "testimonials_count" (user rule: never invent one)
        n_cards = p.get("testimonials_count", 3)
        check(f"{n_cards} review cards with photo or initials, name, fixed title and text",
              len(cards) == n_cards and all(("<img" in c or "review-avatar" in c) and "review-name" in c and re.search(fx["card"], c) and "review-text" in c for c in cards))
    else:
        # official site has no testimonials: no Customer Reviews block, nothing invented
        check("no Customer Reviews block (no testimonials on the official site)",
              not cards and "customer-reviews" not in o and "customer-reviews" not in a_pagina
              and fx["card_plain"] not in o and fx["card_plain"] not in a_pagina)
    footer = o[o.index("<footer"):o.index("</footer>")]
    check("footer has disclaimer, 3 legal items without links and copyright",
          all(x in footer for x in fx["footer"]) and footer.count("<li>") == 3 and "<a " not in footer)
    css = get(f"{DOMAIN}/assets/review.css?audit=1")[2].decode("utf-8")
    check("brand color applied", f"--brand-primary:{p['colors']['primary']}" in o and f"--brand-primary:{p['colors']['primary']}" in a)
    check("top image same size as the second (43% / 86%)", ".shot-hero img{width:43%}" in css and ".shot-2 img{width:43%}" in css
          and css.count(".shot-hero img{width:86%}") == 1)
    for src in sorted(set(re.findall(r'src="(assets/[^"]+)"', o))):
        st, hd, body = get(org_url + src)
        check(f"image {src} is live and light", st == 200 and len(body) < 150_000, f"{len(body) // 1024} KB")

    print("== organic version")
    check("no redirect scripts", not any(x in o for x in ("exitStopper", "redirectURL", "addEventListener('click'")))
    check("index, follow + canonical to itself", 'content="index, follow' in o and f'<link rel="canonical" href="{org_url}">' in o)
    check("affiliate links open in a new tab with sponsored nofollow noopener",
          o.count(f'href="{aff}" rel="sponsored nofollow noopener" target="_blank"') == len(re.findall(r"<a\b", o)))
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', o, re.S)
    ld = json.loads(m.group(1)) if m else {}
    dump = json.dumps(ld)
    check("JSON-LD valid, without Product, offers or aggregateRating", bool(ld) and '"Product"' not in dump and "offers" not in dump and "aggregateRating" not in dump and "Price" not in dump)
    check("Open Graph and Twitter Card present", 'property="og:image"' in o and 'name="twitter:card"' in o)
    check("sticky CTA bar and exit pop-up present", 'class="sticky-cta"' in o and 'id="exit-pop"' in o)
    check("no X-Robots-Tag header", "x-robots-tag" not in ho)
    t = re.search(r"<title>(.*?)</title>", o).group(1)
    d = re.search(r'name="description" content="([^"]*)"', o).group(1)
    check("title <= 60 chars and description 140-160", len(html.unescape(t)) <= 60 and 140 <= len(d) <= 160, f"{len(html.unescape(t))}/{len(d)}")
    sm = get(f"{DOMAIN}/sitemap.xml?audit=1")[2].decode("utf-8")
    ll = get(f"{DOMAIN}/llms.txt?audit=1")[2].decode("utf-8")
    rb = get(f"{DOMAIN}/robots.txt?audit=1")[2].decode("utf-8")
    check("in sitemap.xml and llms.txt", org_url in sm and org_url in ll)

    print("== Google Ads version")
    check("noindex, nofollow meta and X-Robots-Tag header", '<meta name="robots" content="noindex, nofollow">' in a
          and "noindex" in ha.get("x-robots-tag", ""), ha.get("x-robots-tag"))
    check("no canonical, JSON-LD or Open Graph", not any(x in a for x in ('rel="canonical"', "ld+json", 'property="og:')))
    check("affiliate links in the same tab with sponsored nofollow",
          a.count(f'href="{aff}" rel="sponsored nofollow">') == len(re.findall(r"<a\b", a)) and 'target="_blank"' not in a)
    # o script do chat com especialista (seção 13) não conta: os scripts 1 e 2 continuam sendo os únicos de redirecionamento
    scripts = [s for s in re.findall(r"<script>(.*?)</script>", a, re.S) if "chat-lancador" not in s]
    check("scripts 1 and 2 once each, last thing before </body>", len(scripts) == 2 and a.rstrip().endswith("</script>\n</body>\n</html>")
          and "exitStopper" in scripts[0] and "addEventListener('click'" in scripts[1])
    check("affiliate link in script 1, no placeholder, no &amp;",
          f'window.redirectURL = "{aff}";' in a and "LINK DE AFILIADO" not in a and all("&amp;" not in s for s in scripts))
    # desde 2026-10-17: os redirects usam o link carimbado pela tag (subid com o clique), nunca um link fixo
    check("redirects use the link stamped by the tracking tag (no hard-coded link)",
          "function linkCarimbado()" in scripts[0] and "window.location.href = linkCarimbado();" in scripts[0]
          and "window.location.href = linkCarimbado();" in scripts[1] and "closest('a, button')" in scripts[1]
          and "window.location.href = '" not in a and "window.location.href = window.redirectURL" not in a)
    # BuyGoods: cdn.raads-hub.com; Digistore24: cdn.raadstag.com (CLAUDE.md, seção 14.4). A orgânica nunca tem nenhuma.
    plat, cfg_plat = plataforma_of(p)
    tag_src = re.search(r'src="([^"]+)"', cfg_plat["tag"]).group(1)
    check(f"tracking tag of {plat} once in the Google Ads version, never in the organic one",
          a.count(tag_src) == 1 and a.count("/tag.js") == 1 and "raads-hub.com" not in o and "raadstag.com" not in o, tag_src)
    check(f"redirect scripts look for the {plat} affiliate link ({cfg_plat['marcador']})",
          f'a[href*="{cfg_plat["marcador"]}"]' in scripts[0] and cfg_plat["marcador"] in aff)
    check("no sticky bar or pop-up", 'class="sticky-cta"' not in a and 'id="exit-pop"' not in a)
    check("absent from sitemap.xml and llms.txt, not blocked in robots.txt",
          ads_url not in sm and ads_url not in ll and f"{slug}-review" not in rb)

    chat_json = Path(__file__).resolve().parent / slug / "chat.json"
    print("== chat com especialista (seção 13)")
    check("organic version never has the chat", "chat-lancador" not in o)
    if CHAT_ATIVO and chat_json.exists():
        d = json.loads(chat_json.read_text(encoding="utf-8"))
        v = d["valores"]
        tabela = "especialistas.json" if lang == "en" else f"especialistas-{lang}.json"  # chat alemão: títulos em alemão
        esp = json.loads((Path(__file__).resolve().parent / "chat" / tabela).read_text(encoding="utf-8"))[d["nicho"]]
        check("chat once in the Google Ads version, before scripts 1 and 2",
              a.count('id="chat-lancador"') == 1 and a.index('id="chat-lancador"') < a.index("window.redirectURL"))
        check(f"specialist is the one of the niche {d['nicho']}",
              (v["CHAT_NOME"], v["CHAT_ESPECIALIDADE"], v["CHAT_FOTO"]) == (esp["nome"], esp["especialidade"], esp["foto"])
              and html.escape(esp["nome"]) in a and html.escape(esp["especialidade"], quote=True) in a, esp["nome"])
        check("chat product name is the page's product", v["PRODUTO"] == n, v["PRODUTO"])
        # BuyGoods: subid5 (sobra livre da tag). Digistore24: a tag usa cid e sid1..sid5; até um teste mostrar qual
        # parâmetro sobra livre, o chat não marca nada (vazio), para nunca apagar um parâmetro da tag (seção 14.4).
        sub = v.get("PARAMETRO_SUBID_CHAT", "")
        sub_ok = bool(sub) if plat == "buygoods" else (sub == "" or bool(p.get("subid_chat_testado")))
        check("chat cards use the exact affiliate link and the chat subid",
              v["LINK_AFILIADO"] == aff and f'data-subid-chat="{sub}"' in a and sub_ok, sub or "(sem marca)")
        for src in sorted({esp["foto"]} | set(re.findall(r'src="(\.\./[^"]+)"', a))):
            u = DOMAIN + src if src.startswith("/") else ads_url + src
            st, hd, body = get(u + "?audit=1")
            check(f"chat image {src} is live and light", st == 200 and len(body) < 150_000, f"{st} {len(body) // 1024} KB")
    else:
        check("no chat in the Google Ads version (chat switched off or no chat.json)", "chat-lancador" not in a)

    print(f"\n{'ALL CHECKS PASSED' if not fails else str(fails) + ' CHECK(S) FAILED'}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
