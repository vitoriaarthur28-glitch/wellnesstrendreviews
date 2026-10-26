"""Generates the two versions of a review page from one body template.

Usage: python _build/build.py sodatide

  public/<slug>-review-org/index.html  organic (SEO) version, no redirect scripts
  public/<slug>-review/index.html      Google Ads version, noindex + redirect scripts
                                       (+ chat com especialista, se existir _build/<slug>/chat.json)

The copy lives in _build/<slug>/body.html and is shared by both versions.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "chat"))
from chat import render as chat_render  # noqa: E402

# Chat com especialista DESLIGADO em todas as páginas (regra do usuário, 2026-10-23: "o chat não está ajudando").
# Os _build/<slug>/chat.json ficam guardados; para religar, troque para True e gere as páginas de novo.
CHAT_ATIVO = False

ROOT = Path(__file__).resolve().parent.parent
DOMAIN = "https://wellnesstrendreviews.fun"
SITE_NAME = "wellnesstrendreviews.fun"

# Idioma da página (CLAUDE.md, seção 14). Produto sem "lang" = inglês americano, como sempre foi.
# "de" = produtos com página oficial em alemão (em geral Digistore24), anunciados na Alemanha, Áustria e Suíça.
LANGS = {
    "en": {"html": "en-US", "og": "en_US", "close": "Close", "official": "official website", "bottles": "bottles",
           "home": "Home", "review": "Review"},
    "de": {"html": "de-DE", "og": "de_DE", "close": "Schließen", "official": "offizielle Website", "bottles": "Flaschen",
           "home": "Startseite", "review": "Erfahrungen"},
    # "fr" = produtos anunciados só em francês (pedido do usuário em 2026-10-26, primeiro: Nervexa). Mesmas regras da seção 14.
    "fr": {"html": "fr-FR", "og": "fr_FR", "close": "Fermer", "official": "site officiel", "bottles": "flacons",
           "home": "Accueil", "review": "Avis"},
}


def lang_of(p):
    return LANGS[p.get("lang", "en")]

PAGES = {
    "breathizen": {
        "name": "BreathiZen",
        "affiliate": "https://forbreathizen.com/btz-aff-buy-dtc/?aff_id=514",
        "official": "https://forbreathizen.com/",
        "title": "BreathiZen Review 2026: Does This Lung Spray Really Work?",
        "description": "Our BreathiZen review covers the oral spray for lungs and breathing: the mullein, ginger and lemon blend, how to use it, side effects, refunds and where to buy.",
        "product_description": "BreathiZen is a liquid oral spray in a 2 oz (60 ml) bottle with Mullein leaf extract, Ginger root extract and Organic Lemon extract, designed to support clear breathing and healthy lung function.",
        "published": "2026-10-16",
        "modified": "2026-10-16",
        "colors": {
            # the label background is a light lavender blue (#B8C8E8); white text needs this darker shade of the same hue
            "primary": "#34508C",
            "primary-hover": "#283F70",
            "secondary": "#B8C8E8",
            "bg": "#FFFFFF",
            "text": "#000000",
            "cta": "#FFCC00",
            "cta-hover": "#E7B900",
            "cta-text": "#000000",
        },
        "hero_image": "breathizen-sprays-marble-lavender.webp",
        "hero_size": (442, 443),
        "og_image": "breathizen-og-v2.jpg",
        "popup_text": "Buying directly from the official source ensures you receive the authentic original product.",
        "cta_text": "Check Availability On Official Website",
    },
    "olivaro": {
        "name": "Olivaro",
        "affiliate": "https://theolivaro.com/olv-aff-buy-dtc/?aff_id=32610",
        "official": "https://theolivaro.com/home/",
        "title": "Olivaro Review 2026: Do These Blood Sugar Drops Really Work?",
        "description": "Our Olivaro review covers the liquid blood sugar support drops: the chromium and herbal blend, how many droppers to take, safety notes, refunds, where to buy.",
        "product_description": "Olivaro is a liquid dietary supplement for balanced blood sugar support in a 30 ml (1 fl oz) dropper bottle with chromium picolinate and a 200 mg blend including Gymnema, African Mango, Green Tea, Maca and Panax Ginseng; 1 to 2 droppers a day.",
        "published": "2026-10-24",
        "modified": "2026-10-24",
        "colors": {
            # navy blue of the official sales page sections (rgb 18,58,99), darker #0C2A49
            "primary": "#123A63",
            "primary-hover": "#0C2A49",
            "secondary": "#E17300",
            "bg": "#FFFFFF",
            "text": "#000000",
            "cta": "#FFCC00",
            "cta-hover": "#E7B900",
            "cta-text": "#000000",
        },
        "hero_image": "olivaro-bottle-olive-kitchen.webp",
        "hero_size": (550, 550),
        "og_image": "olivaro-og.jpg",
        "popup_text": "Buying directly from the official source ensures you receive the authentic original product.",
        "cta_text": "Check Availability On Official Website",
    },
    "nervexa-fr": {
        "name": "Nervexa",
        "lang": "fr",
        # Digistore24 (checkout-ds24.com) pela página do produtor get-nervexa.com, que repassa aff e sid1..sid5 ao checkout.
        # Produto anunciado só em francês ou alemão (usuário, 2026-10-26); esta é a versão francesa.
        "affiliate": "https://get-nervexa.com/dtc-fr/?aff=YuryFerreira",
        "plataforma": "digistore24",
        "marcador_link": "get-nervexa.com",
        "official": "https://get-nervexa.com/fr/",
        "title": "Nervexa : Avis, Ingrédients et Mode d’Emploi en 2026",
        "description": "Avis Nervexa : composition détaillée, mode d’emploi quotidien, avertissements sur l’EGCG, politique de remboursement et conseils pour acheter en sécurité.",
        "product_description": "Nervexa est un complément alimentaire en gélules (30 par flacon) associant acide alpha-lipoïque, zinc, chrome, thé vert, chardon-Marie, berbérine, resvératrol, Cayenne, ginseng coréen et lilas des Indes.",
        "published": "2026-10-26",
        "modified": "2026-10-26",
        "colors": {
            "primary": "#34519E",
            "primary-hover": "#22346B",
            "secondary": "#4A6FC4",
            "bg": "#FFFFFF",
            "text": "#000000",
            "cta": "#FFCC00",
            "cta-hover": "#E7B900",
            "cta-text": "#000000",
        },
        "hero_image": "nervexa-fr-bottle.webp",
        "hero_size": (550, 550),
        "og_image": "nervexa-fr-og.jpg",
        "popup_text": "En achetant directement auprès de la source officielle, vous recevez le produit authentique d’origine.",
        "cta_text": "Vérifier la disponibilité sur le site officiel",
        "testimonials": False,
    },
    "memo-meister-fr": {
        "name": "Memo Meister",
        "lang": "fr",
        # Digistore24 (checkout-ds24.com) pela página do produtor get-meister.com, que repassa aff e sid1..sid5 ao checkout.
        "affiliate": "https://get-meister.com/dtc-fr?aff=YuryFerreira",
        "plataforma": "digistore24",
        "marcador_link": "get-meister.com",
        "official": "https://get-meister.com/fr/",
        "title": "Memo Meister : Avis, Ingrédients et Mode d’Emploi (2026)",
        "description": "Avis Memo Meister : composition détaillée, mode d’emploi, contre-indications, politique de remboursement et conseils pour acheter en toute sécurité.",
        "product_description": "Memo Meister est un complément alimentaire en gélules (30 par flacon) avec vitamine B3, zinc, L-citrulline, L-carnitine, écorce de pin, maca, raisin et safran.",
        "published": "2026-10-26",
        "modified": "2026-10-26",
        "colors": {
            "primary": "#1C54A1",
            "primary-hover": "#213570",
            "secondary": "#1855AA",
            "bg": "#FFFFFF",
            "text": "#000000",
            "cta": "#FFCC00",
            "cta-hover": "#E7B900",
            "cta-text": "#000000",
        },
        "hero_image": "memo-meister-fr-bottle.webp",
        "hero_size": (550, 550),
        "og_image": "memo-meister-fr-og.jpg",
        "popup_text": "En achetant directement auprès de la source officielle, vous recevez le produit authentique d’origine.",
        "cta_text": "Vérifier la disponibilité sur le site officiel",
    },
    "gelatin-meister-fr": {
        "name": "Gelatin Meister",
        "lang": "fr",
        # Digistore24 (checkout-ds24.com) pela página do produtor gelatinmeister.com, que repassa aff e sid1..sid5 ao checkout.
        "affiliate": "https://gelatinmeister.com/dtc-fr?aff=YuryFerreira",
        "plataforma": "digistore24",
        "marcador_link": "gelatinmeister.com",
        "official": "https://gelatinmeister.com/fr/",
        "title": "Gelatin Meister : Avis, Ingrédients et Mode d’Emploi",
        "description": "Avis Gelatin Meister : composition détaillée, mode d’emploi, contre-indications, politique de remboursement et conseils pour acheter en toute sécurité.",
        "product_description": "Gelatin Meister est un complément alimentaire en gélules (30 par flacon) avec chrome, thé vert, vinaigre de cidre, berbérine, gingembre, cannelle, orange amère, Cayenne, lilas des Indes, ginseng coréen et resvératrol.",
        "published": "2026-10-26",
        "modified": "2026-10-26",
        "colors": {
            "primary": "#C2185B",
            "primary-hover": "#9C1349",
            "secondary": "#E91E7A",
            "bg": "#FFFFFF",
            "text": "#000000",
            "cta": "#FFCC00",
            "cta-hover": "#E7B900",
            "cta-text": "#000000",
        },
        "hero_image": "gelatin-meister-fr-bottle.webp",
        "hero_size": (550, 550),
        "og_image": "gelatin-meister-fr-og.jpg",
        "popup_text": "En achetant directement auprès de la source officielle, vous recevez le produit authentique d’origine.",
        "cta_text": "Vérifier la disponibilité sur le site officiel",
        "testimonials": False,
    },
    "nervexa-de": {
        "name": "Nervexa",
        "lang": "de",
        # Digistore24 pela página do produtor (repassa aff e sid1..sid5 ao checkout); versão alemã (usuário, 2026-10-26).
        "affiliate": "https://get-nervexa.com/dtc-de/?aff=YuryFerreira",
        "plataforma": "digistore24",
        "marcador_link": "get-nervexa.com",
        "official": "https://get-nervexa.com/de/",
        "title": "Nervexa: Erfahrungen, Inhaltsstoffe und Anwendung 2026",
        "description": "Nervexa Erfahrungen: detaillierte Zusammensetzung, tägliche Anwendung, EGCG-Hinweise, Rückerstattung und Tipps für einen sicheren Kauf auf der Website.",
        "product_description": "Nervexa ist ein Nahrungsergänzungsmittel in Kapseln (30 pro Flasche) mit Alpha-Liponsäure, Zink, Chrom, Grüntee, Mariendistel, Berberin, Resveratrol, Cayenne, Koreanischem Ginseng und Königinblume.",
        "published": "2026-10-26",
        "modified": "2026-10-26",
        "colors": {
            "primary": "#34519E",
            "primary-hover": "#22346B",
            "secondary": "#4A6FC4",
            "bg": "#FFFFFF",
            "text": "#000000",
            "cta": "#FFCC00",
            "cta-hover": "#E7B900",
            "cta-text": "#000000",
        },
        "hero_image": "nervexa-de-bottle.webp",
        "hero_size": (550, 550),
        "og_image": "nervexa-de-og.jpg",
        "popup_text": "Beim Kauf direkt über die offizielle Quelle erhalten Sie das authentische Originalprodukt.",
        "cta_text": "Verfügbarkeit auf der offiziellen Website prüfen",
        "testimonials": False,
    },
    "memo-meister-de": {
        "name": "Memo Meister",
        "lang": "de",
        # Digistore24 pela página do produtor (repassa aff e sid1..sid5 ao checkout); versão alemã (usuário, 2026-10-26).
        "affiliate": "https://get-meister.com/dtc-de?aff=YuryFerreira",
        "plataforma": "digistore24",
        "marcador_link": "get-meister.com",
        "official": "https://get-meister.com/de/",
        "title": "Memo Meister: Erfahrungen, Inhaltsstoffe und Anwendung",
        "description": "Memo Meister Erfahrungen: detaillierte Zusammensetzung, tägliche Anwendung, Gegenanzeigen, Rückerstattung und Tipps für einen sicheren Kauf auf der Website.",
        "product_description": "Memo Meister ist ein Nahrungsergänzungsmittel in Kapseln (30 pro Flasche) mit Vitamin B3, Zink, L-Citrullin, L-Carnitin, Pinienrinde, Maca, Traubenschale und Safran.",
        "published": "2026-10-26",
        "modified": "2026-10-26",
        "colors": {
            "primary": "#1C54A1",
            "primary-hover": "#213570",
            "secondary": "#1855AA",
            "bg": "#FFFFFF",
            "text": "#000000",
            "cta": "#FFCC00",
            "cta-hover": "#E7B900",
            "cta-text": "#000000",
        },
        "hero_image": "memo-meister-de-bottle-official.webp",
        "hero_size": (550, 550),
        "og_image": "memo-meister-de-og.jpg",
        "popup_text": "Beim Kauf direkt über die offizielle Quelle erhalten Sie das authentische Originalprodukt.",
        "cta_text": "Verfügbarkeit auf der offiziellen Website prüfen",
    },
    "gelatin-meister-de": {
        "name": "Gelatin Meister",
        "lang": "de",
        # Digistore24 pela página do produtor (repassa aff e sid1..sid5 ao checkout); versão alemã (usuário, 2026-10-26).
        "affiliate": "https://gelatinmeister.com/dtc-de?aff=YuryFerreira",
        "plataforma": "digistore24",
        "marcador_link": "gelatinmeister.com",
        "official": "https://gelatinmeister.com/de/",
        "title": "Gelatin Meister: Erfahrungen, Inhaltsstoffe, Anwendung",
        "description": "Gelatin Meister Erfahrungen: detaillierte Zusammensetzung, tägliche Anwendung, Gegenanzeigen, Rückerstattung und Tipps für einen sicheren Kauf auf der Website.",
        "product_description": "Gelatin Meister ist ein Nahrungsergänzungsmittel in Kapseln (30 pro Flasche) mit Chrom, Grüntee, Apfelessig, Berberin, Ingwer, Zimt, Bitterorange, Cayenne, Königinblume, Koreanischem Ginseng und Resveratrol.",
        "published": "2026-10-26",
        "modified": "2026-10-26",
        "colors": {
            "primary": "#C2185B",
            "primary-hover": "#9C1349",
            "secondary": "#E91E7A",
            "bg": "#FFFFFF",
            "text": "#000000",
            "cta": "#FFCC00",
            "cta-hover": "#E7B900",
            "cta-text": "#000000",
        },
        "hero_image": "gelatin-meister-de-bottle-official.webp",
        "hero_size": (550, 605),
        "og_image": "gelatin-meister-de-og.jpg",
        "popup_text": "Beim Kauf direkt über die offizielle Quelle erhalten Sie das authentische Originalprodukt.",
        "cta_text": "Verfügbarkeit auf der offiziellen Website prüfen",
        "testimonials": False,
    },
}

# Ratoeira Ads tracking tag (carries the ad click id to the affiliate link so sales can be
# reported back to Google Ads). Google Ads version only, in <head>; same tag for every product.
TRACKING_TAG = '''<script defer src="https://cdn.raads-hub.com/tag.js" data-tag-id="61-8a9d4c88dff047069a476aae153dcb11" data-event-host="api.raads-hub.com" data-plat-params="subid,subid2,subid3,subid4,subid5"></script>'''
# Tag da Ratoeira para produtos Digistore24 (enviada pelo usuário em 2026-10-19; CLAUDE.md, seção 14.4). Outra tag e outros
# parâmetros: a Digistore24 usa cid e sid1..sid5 no lugar de subid..subid5.
TRACKING_TAG_DS24 = '''<script defer src="https://cdn.raadstag.com/tag.js" data-tag-id="61-15185804035b42a5ba1c9b9e0c747217" data-event-host="api.raadstag.com" data-plat-params="cid,sid1,sid2,sid3,sid4,sid5"></script>'''
# Tag da Ratoeira para produtos GuruMedia (Everflow, links fasttrack20.com), enviada pelo usuário em 2026-10-19 para todos
# os produtos GuruMedia (nutra e ecom). Parâmetros sub1..sub5.
TRACKING_TAG_GURUMEDIA = '''<script defer src="https://cdn.raadstag.com/tag.js" data-tag-id="61-d488820eb4ad4d4fb156b9ed71ae970a" data-event-host="api.raadstag.com" data-plat-params="sub1,sub2,sub3,sub4,sub5"></script>'''
# Por plataforma: a tag e o trecho que identifica o link de afiliado (os scripts 1 e 2 procuram o link carimbado por ele).
PLATAFORMAS = {
    "buygoods": {"tag": TRACKING_TAG, "marcador": "aff_id="},
    "digistore24": {"tag": TRACKING_TAG_DS24, "marcador": "digistore24.com"},
    "gurumedia": {"tag": TRACKING_TAG_GURUMEDIA, "marcador": "fasttrack20.com"},
}


def plataforma_of(p):
    """Plataforma do produto: "plataforma" em PAGES, senão pelo link (digistore24.com = Digistore24; o resto, BuyGoods)."""
    nome = p.get("plataforma") or ("digistore24" if "digistore24.com" in p["affiliate"] else
                                   "gurumedia" if "fasttrack20.com" in p["affiliate"] else "buygoods")
    return nome, {**PLATAFORMAS[nome], **({"marcador": p["marcador_link"]} if p.get("marcador_link") else {})}

# Scripts 1 e 2 (versão Google Ads). Desde 2026-10-17 eles levam ao link JÁ CARIMBADO pela tag da Ratoeira (subid com o
# clique), e não ao link puro: antes, o link fixo passava por cima do link carimbado e as vendas chegavam sem o clique
# (diagnóstico em C:\claude\diagnostico-rastreamento-ratoeira-2026-10-17.md). Sem a tag carregada, cai no link puro.
SCRIPT_1 = """<script>
window.redirectURL = "LINK DE AFILIADO";
window.indoAoAfiliado = false;
function linkCarimbado() {
  var a = document.querySelector('a[href*="aff_id="]:not([data-link-pacote])');
  return (a && a.href) || window.redirectURL;
}
document.addEventListener('click', function(e) {
  var a = e.target.closest && e.target.closest('a[href]');
  if (a && a.href.indexOf('aff_id=') !== -1) { window.indoAoAfiliado = true; }
}, true);
function exitStopper() {
  if (window.indoAoAfiliado) { return; }
  if (window.redirectURL) {
    window.indoAoAfiliado = true;
    window.location.href = linkCarimbado();
  }
}

window.addEventListener('blur', exitStopper);
document.body.addEventListener("mouseleave", function(e) {
  if (e.clientY <= 0) {
    exitStopper();
  }
}, false);

window.addEventListener('beforeunload', exitStopper);
window.addEventListener('pagehide', exitStopper);

window.addEventListener('popstate', function() {
  exitStopper();
});
</script>"""

SCRIPT_2 = """<script>
  // Clique fora de links e botões leva ao link carimbado; clique num link deixa o próprio link (carimbado) agir
  document.addEventListener('click', function(e) {
    if (e.target.closest && e.target.closest('a, button')) { return; }
    window.indoAoAfiliado = true;
    window.location.href = linkCarimbado();
  });
</script>"""

EXIT_POPUP_JS = """<script>
(function () {
  var pop = document.getElementById('exit-pop');
  if (!pop || !window.matchMedia('(min-width: 769px)').matches) return;
  var KEY = 'exitPopShown';
  function seen() { try { return sessionStorage.getItem(KEY) === '1'; } catch (e) { return false; } }
  function mark() { try { sessionStorage.setItem(KEY, '1'); } catch (e) {} }
  function close() { pop.hidden = true; document.removeEventListener('keydown', onKey); }
  function onKey(e) { if (e.key === 'Escape') close(); }
  function open() {
    if (seen()) return;
    mark();
    pop.hidden = false;
    document.addEventListener('keydown', onKey);
    pop.querySelector('.exit-close').focus();
  }
  document.documentElement.addEventListener('mouseleave', function (e) { if (e.clientY <= 0) open(); });
  pop.onclick = function (e) { if (e.target === pop) close(); };
  pop.querySelector('.exit-close').onclick = close;
})();
</script>"""


def root_vars(colors):
    return ":root{" + ";".join(f"--brand-{k}:{v}" for k, v in colors.items()) + "}"


def json_ld(p, url, img_url):
    L = lang_of(p)
    org = {"@type": "Organization", "@id": f"{DOMAIN}/#organization", "name": SITE_NAME, "url": f"{DOMAIN}/"}
    graph = [
        org,
        {"@type": "WebSite", "@id": f"{DOMAIN}/#website", "url": f"{DOMAIN}/", "name": SITE_NAME,
         "publisher": {"@id": org["@id"]}, "inLanguage": L["html"]},
        {"@type": "WebPage", "@id": f"{url}#webpage", "url": url, "name": p["title"],
         "description": p["description"], "isPartOf": {"@id": f"{DOMAIN}/#website"},
         "breadcrumb": {"@id": f"{url}#breadcrumb"}, "primaryImageOfPage": img_url,
         "datePublished": p["published"], "dateModified": p["modified"], "inLanguage": L["html"]},
        {"@type": "Article", "@id": f"{url}#article", "headline": p["title"], "description": p["description"],
         "image": img_url, "datePublished": p["published"], "dateModified": p["modified"],
         "author": {"@id": org["@id"]}, "publisher": {"@id": org["@id"]},
         "mainEntityOfPage": {"@id": f"{url}#webpage"}, "inLanguage": L["html"],
         # The reviewed item is described as a plain Thing. A Product node needs offers, a rating or a
         # rated review to be valid for Google, and these pages carry no price and no rating.
         "about": {"@type": "Thing", "name": p["name"], "description": p["product_description"], "url": p["official"]}},
        {"@type": "BreadcrumbList", "@id": f"{url}#breadcrumb", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": L["home"], "item": f"{DOMAIN}/"},
            {"@type": "ListItem", "position": 2, "name": f"{p['name']} {L['review']}", "item": url}]},
    ]
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1)


def head_common(p):
    return f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{p['title']}</title>
<meta name="description" content="{p['description']}">"""


def head_assets(p):
    return f"""<meta name="theme-color" content="{p['colors']['primary']}">
<link rel="icon" href="/favicon-r.ico" sizes="16x16 32x32 48x48">
<link rel="preload" href="/assets/fonts/poppins-400-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/review.css?v=9">
<style>{root_vars(p['colors'])}</style>"""


def build(slug):
    p = PAGES[slug]
    aff = p["affiliate"]
    L = lang_of(p)
    # Os scripts 1 e 2 acham o link carimbado pela tag da Ratoeira pelo marcador da plataforma ("aff_id=" na BuyGoods,
    # "digistore24.com" na Digistore24). Link sem o marcador cairia no link puro e as vendas voltariam sem o clique.
    plat, cfg_plat = plataforma_of(p)
    marcador = cfg_plat["marcador"]
    if marcador not in aff:
        sys.exit(f"[{slug}] link de afiliado sem {marcador!r} (plataforma {plat}): os scripts 1 e 2 não achariam o link "
                 "carimbado. Confira o link ou ponha \"marcador_link\" no produto (CLAUDE.md, seção 14.4)")
    body = (ROOT / "_build" / slug / "body.html").read_text(encoding="utf-8")

    # --- organic version ---
    org_slug = f"{slug}-review-org"
    url = f"{DOMAIN}/{org_slug}/"
    img_url = f"{url}assets/{p['hero_image']}"
    og_url = f"{url}assets/{p['og_image']}"
    a_org = f'href="{aff}" rel="sponsored nofollow noopener" target="_blank"'
    org_body = body.replace("@@AFF@@", a_org).replace("@@IMG@@", "assets/")
    org_html = f"""<!DOCTYPE html>
<html lang="{L['html']}">
<head>
{head_common(p)}
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<meta property="og:type" content="article">
<meta property="og:title" content="{p['title']}">
<meta property="og:description" content="{p['description']}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{og_url}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:locale" content="{L['og']}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{p['title']}">
<meta name="twitter:description" content="{p['description']}">
<meta name="twitter:image" content="{og_url}">
<link rel="preload" href="assets/{p['hero_image']}" as="image" type="image/webp" fetchpriority="high">
{head_assets(p)}
<script type="application/ld+json">
{json_ld(p, url, img_url)}
</script>
</head>
<body class="has-sticky">
{org_body}
<div class="sticky-cta"><a class="btn" {a_org}>{p['cta_text']}</a></div>
<div class="exit-pop" id="exit-pop" role="dialog" aria-modal="true" aria-label="{p['name']} {L['official']}" hidden>
  <div class="exit-box">
    <button type="button" class="exit-close" aria-label="{L['close']}">&times;</button>
    <a {a_org}><img src="assets/{p['hero_image']}" alt="{p['name']} {L['bottles']}" width="220" height="{round(220 * p['hero_size'][1] / p['hero_size'][0])}" loading="lazy" onerror="this.hidden=true"></a>
    <p>{p['popup_text']}</p>
    <a class="btn" {a_org}>{p['cta_text']}</a>
  </div>
</div>
{EXIT_POPUP_JS}
</body>
</html>
"""
    out = ROOT / org_slug / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(org_html, encoding="utf-8", newline="\n")

    # --- Google Ads version ---
    if not cfg_plat["tag"]:
        # plataforma sem tag da Ratoeira cadastrada: nunca usar a tag de outra plataforma (CLAUDE.md, seção 14.4)
        print(f"built {org_slug} only: plataforma {plat} sem tag da Ratoeira, versão Google Ads não gerada")
        return
    ads_slug = f"{slug}-review"
    a_ads = f'href="{aff}" rel="sponsored nofollow"'
    ads_body = body.replace("@@AFF@@", a_ads).replace("@@IMG@@", f"../{org_slug}/assets/")
    # chat com especialista do nicho: só na versão Google Ads, antes dos scripts 1 e 2 (CLAUDE.md, seção 13)
    chat = chat_render(slug, aff, p.get("lang", "en")) if CHAT_ATIVO else ""
    ads_html = f"""<!DOCTYPE html>
<html lang="{L['html']}">
<head>
{head_common(p)}
<meta name="robots" content="noindex, nofollow">
{head_assets(p)}
{cfg_plat["tag"]}
</head>
<body>
{ads_body}
{chat}{SCRIPT_1.replace("LINK DE AFILIADO", aff).replace("aff_id=", marcador)}
{SCRIPT_2.replace("LINK DE AFILIADO", aff)}
</body>
</html>
"""
    out = ROOT / ads_slug / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(ads_html, encoding="utf-8", newline="\n")
    print(f"built {org_slug} and {ads_slug}")


if __name__ == "__main__":
    for s in sys.argv[1:] or PAGES:
        build(s)
