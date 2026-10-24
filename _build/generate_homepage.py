"""Generate the homepage (public/index.html) for wellnesstrendreviews.fun.

Reads every -review-org/ folder, extracts product name + description + bottle
image, categorises each product, and writes a catalogue-style homepage.

Run:  python _build/generate_homepage.py
"""

import os, re, html as ht
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ── category definitions (slug → category) ────────────────────────────
CATEGORIES = {
    "Blood Sugar Support": [
        "glucocontrol","glucotide","glucotonic","glucotrustbites","glucovive",
        "glycobalance","glycofree","glycopezil","glycoreset","glpro","glpropatch",
        "honey-harmony","insufend","payarmin","regenvive","sugarbind","sugarmute",
        "sugarreset","zensulin",
    ],
    "Weight Management": [
        "alkaburn","aquafit","aquasculpt","burntide","fitspresso","floranew",
        "gelatide","gelatide1","gelatinesculpt","gumitide","lipoflow","metarise",
        "slimforce","slimrise","slimset","slimtide","sodaburn","sodafit",
        "sodaslim","vittaburn",
    ],
    "Brain & Memory": [
        "brainlive","javacept","memocept","memoclear","memodyne","memohoney",
        "memopezil","honeypezil","mindvault","neuromind-pro","neurosharp","synaptigen","vapocept",
    ],
    "Nerve Support": [
        "arialief","nervecalm","nervecept","nerve-harmony","nervolyn","nervovive",
        "neuro-cinnamon","neurosalt",
    ],
    "Male Vitality": [
        "alphasteel","alphasurge","blackwoodtea","boostaro","gelafil","giantmax",
        "heroup","honeyboost","horseboost","horsefil","horsewood","jellyboost",
        "jellyfil","maxforce","maxorin","maxvitalize","nitricboost","ragnaroak",
        "sodaboost","sodahorsepeak","sodapeak","tupitea","vigorhorse","vigorpeak",
        "vigorrise",
    ],
    "Digestive & Gut Health": [
        "alkatide","digestsync","gutsave","sodamelt","sodatide","synogut",
    ],
    "Heart & Blood Pressure": [
        "bloodpril","colestzen","melonex","presspril","pressurecalmx",
    ],
    "Hearing Support": [
        "audifort","audileaf","echoxen","neuroquiet","ringzen6",
    ],
    "Respiratory & Lung": [
        "breathe","breatheasex","breathizen","pulmobalance",
    ],
    "Oral Health": [
        "dentabiome","dentanol","oradentum","purdentix",
    ],
    "Skin & Beauty": [
        "dermapure","gelagen","kerafen","kerafirmpro","prime-age","synevra",
    ],
    "Vision & Eye Health": [
        "optiplax","retinaclear","visiflora","visivra",
    ],
    "Joint & Mobility": [
        "backbiome","fleximove","jointbrex","jointrix",
    ],
    "Prostate Health": [
        "potentstream","prostadefend","prostatemax",
    ],
    "Women's Health": [
        "femicore","menosoothe","thyrafemme",
    ],
    "Immune Support": [
        "herpafend","tonicgreens",
    ],
    "Sleep": [
        "yu-sleep",
    ],
    "Pet Health": [
        "pawbiotix",
    ],
}

# German-language products go in a separate section
GERMAN_SLUGS = {
    "beatbuds","bodyon","bottle-of-angels","cartekit","curaball","faulsauber",
    "flexora","guardian","gutera","heatguard","herz-p1","homepro",
    "lifegauge-breeze","liostrong","loriax","mendorex","miticast","movaryn",
    "nanoklean","nerven-meister","neuroview","nofuzz","osseowave","podbloom",
    "quikheat","sawshark","ultragrip","vantrek","veluflex","whirlclean",
}

# ── extract product data ──────────────────────────────────────────────
def extract(slug):
    folder = ROOT / f"{slug}-review-org"
    idx = folder / "index.html"
    if not idx.exists():
        return None
    text = idx.read_text(encoding="utf-8", errors="replace")

    # product display name from <title>
    m = re.search(r"<title>([^<]+)</title>", text)
    if not m:
        return None
    raw_title = m.group(1)
    # tombstones of removed pages stay out of the catalog
    if raw_title.startswith("Page removed"):
        return None
    # extract just the product name (before "Reviews" or "Review" or "Erfahrungen")
    name = re.split(r"\s+(?:Reviews?|Erfahrungen)", raw_title)[0].strip()

    # meta description (short blurb)
    m = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', text)
    desc = m.group(1) if m else ""
    # shorten: take the part after the colon
    if ": " in desc:
        desc = desc.split(": ", 1)[1]
    # capitalize first letter
    if desc:
        desc = desc[0].upper() + desc[1:]

    # bottle image
    assets = folder / "assets"
    bottle = ""
    if assets.is_dir():
        for f in sorted(assets.iterdir()):
            if "bottle" in f.name and f.suffix in (".webp", ".jpg", ".png"):
                bottle = f"{slug}-review-org/assets/{f.name}"
                break

    return {"slug": slug, "name": name, "desc": desc, "bottle": bottle, "de": "Erfahrungen" in raw_title}

# ── collect all products ──────────────────────────────────────────────
all_slugs = set()
for cat_slugs in CATEGORIES.values():
    all_slugs.update(cat_slugs)
all_slugs.update(GERMAN_SLUGS)

products = {}
for s in sorted(all_slugs):
    info = extract(s)
    if info:
        products[s] = info

# also find any product not yet categorised
for d in sorted(ROOT.iterdir()):
    if d.is_dir() and d.name.endswith("-review-org"):
        slug = d.name.replace("-review-org", "")
        if slug not in all_slugs:
            info = extract(slug)
            if info:
                products[slug] = info
                if slug in GERMAN_SLUGS or info.get("de"):
                    GERMAN_SLUGS.add(slug)
                else:
                    # add to a catch-all
                    if "Other" not in CATEGORIES:
                        CATEGORIES["Other"] = []
                    CATEGORIES["Other"].append(slug)

total_en = sum(1 for s in products if s not in GERMAN_SLUGS)
total_de = sum(1 for s in products if s in GERMAN_SLUGS)
total = len(products)

# ── build product card HTML ───────────────────────────────────────────
def card(p):
    img = ""
    if p["bottle"]:
        img = f'<img src="{ht.escape(p["bottle"])}" alt="{ht.escape(p["name"])} bottle" width="200" height="200" loading="lazy" onerror="this.closest(\'.card-img\').hidden=true">'
    # truncate desc to ~120 chars
    short = p["desc"]
    if len(short) > 130:
        short = short[:127].rsplit(" ", 1)[0] + "..."
    link = f'{p["slug"]}-review-org/'
    return f'''<a href="{link}" class="card">
  <div class="card-img">{img}</div>
  <h3>{ht.escape(p["name"])}</h3>
  <p>{ht.escape(short)}</p>
  <span class="read">Read Full Review &rarr;</span>
</a>'''

# ── category section HTML ─────────────────────────────────────────────
def section(cat_name, slugs, id_prefix="cat"):
    items = [products[s] for s in slugs if s in products]
    if not items:
        return ""
    sid = id_prefix + "-" + cat_name.lower().replace(" & ", "-").replace(" ", "-")
    cards = "\n".join(card(p) for p in items)
    return f'''<section id="{sid}">
  <h2>{ht.escape(cat_name)} <span class="count">({len(items)})</span></h2>
  <div class="grid">{cards}</div>
</section>'''

# ── full page ─────────────────────────────────────────────────────────
cat_nav = "\n".join(
    f'    <a href="#cat-{c.lower().replace(" & ","-").replace(" ","-")}">{c}</a>'
    for c in CATEGORIES if any(s in products for s in CATEGORIES[c])
)

cat_sections = "\n".join(
    section(c, CATEGORIES[c]) for c in CATEGORIES
)

german_section = ""
german_items = sorted([products[s] for s in GERMAN_SLUGS if s in products], key=lambda x: x["name"])
if german_items:
    gcards = "\n".join(card(p) for p in german_items)
    german_section = f'''<section id="de-reviews">
  <h2>Produkt-Bewertungen (Deutsch) <span class="count">({len(german_items)})</span></h2>
  <p class="section-intro">Unsere Bewertungen auf Deutsch &mdash; Gadgets, Nahrungserg&auml;nzungsmittel und Haushaltsprodukte.</p>
  <div class="grid">{gcards}</div>
</section>'''

page = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<link rel="icon" href="/favicon-r.ico" sizes="16x16 32x32 48x48">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Wellness Trend Reviews &mdash; Honest Product Reviews</title>
<meta name="description" content="Independent product reviews based on real user feedback. We research ingredients, side effects, dosage and refund policies so you don't have to. Browse {total}+ reviews.">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<link rel="canonical" href="https://wellnesstrendreviews.fun/">
<meta property="og:type" content="website">
<meta property="og:title" content="Wellness Trend Reviews — Honest Product Reviews">
<meta property="og:description" content="Independent product reviews based on real user feedback. {total}+ products reviewed.">
<meta property="og:url" content="https://wellnesstrendreviews.fun/">
<meta property="og:site_name" content="Wellness Trend Reviews">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="Wellness Trend Reviews — Honest Product Reviews">
<script type="application/ld+json">
{{
  "@context":"https://schema.org",
  "@type":"WebSite",
  "name":"Wellness Trend Reviews",
  "url":"https://wellnesstrendreviews.fun/",
  "description":"Independent product reviews based on real user feedback"
}}
</script>
<script type="application/ld+json">
{{
  "@context":"https://schema.org",
  "@type":"CollectionPage",
  "name":"Product Review Catalog",
  "url":"https://wellnesstrendreviews.fun/",
  "description":"Browse {total}+ independent product reviews covering supplements, health products and gadgets",
  "numberOfItems":{total},
  "isPartOf":{{"@type":"WebSite","name":"Wellness Trend Reviews","url":"https://wellnesstrendreviews.fun/"}}
}}
</script>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --bg:#f8f9fa;--surface:#fff;--text:#1a1a2e;--muted:#64748b;
  --accent:#5b21b6;--accent-light:#ede9fe;--border:#e2e8f0;
  --radius:12px;--max:1200px;
}}
body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
  background:var(--bg);color:var(--text);line-height:1.6}}
a{{color:inherit;text-decoration:none}}

/* hero */
.hero{{background:linear-gradient(135deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%);
  color:#fff;padding:4rem 1rem 3rem;text-align:center}}
.hero h1{{font-size:clamp(1.8rem,5vw,3rem);font-weight:800;margin-bottom:.5rem}}
.hero h1 span{{color:#a78bfa}}
.hero .tagline{{font-size:clamp(1rem,2.5vw,1.25rem);opacity:.85;max-width:600px;margin:0 auto 1.5rem}}
.hero .stats{{display:flex;gap:2rem;justify-content:center;flex-wrap:wrap;margin-top:1.5rem}}
.hero .stat{{text-align:center}}
.hero .stat strong{{display:block;font-size:2rem;color:#a78bfa}}
.hero .stat span{{font-size:.85rem;opacity:.7}}

/* about */
.about{{max-width:var(--max);margin:0 auto;padding:3rem 1rem 2rem;text-align:center}}
.about h2{{font-size:1.5rem;margin-bottom:1rem}}
.about p{{max-width:700px;margin:0 auto .75rem;color:var(--muted);font-size:1.05rem}}

/* category nav */
.cat-nav{{max-width:var(--max);margin:0 auto;padding:1rem;display:flex;flex-wrap:wrap;gap:.5rem;
  justify-content:center;position:sticky;top:0;background:var(--bg);z-index:10;
  border-bottom:1px solid var(--border)}}
.cat-nav a{{padding:.4rem .9rem;border-radius:20px;font-size:.85rem;font-weight:500;
  background:var(--accent-light);color:var(--accent);transition:all .2s;white-space:nowrap}}
.cat-nav a:hover{{background:var(--accent);color:#fff}}

/* sections */
section{{max-width:var(--max);margin:0 auto;padding:2.5rem 1rem 1rem}}
section h2{{font-size:1.4rem;margin-bottom:.25rem;padding-bottom:.5rem;border-bottom:2px solid var(--accent)}}
section h2 .count{{color:var(--muted);font-weight:400;font-size:.9rem}}
.section-intro{{color:var(--muted);margin-bottom:1rem;font-size:.95rem}}

/* grid */
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:1.25rem;margin-top:1.25rem}}

/* card */
.card{{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);
  padding:1.25rem;display:flex;flex-direction:column;align-items:center;text-align:center;
  transition:box-shadow .25s,transform .25s}}
.card:hover{{box-shadow:0 8px 25px rgba(0,0,0,.1);transform:translateY(-3px)}}
.card-img{{width:120px;height:120px;display:flex;align-items:center;justify-content:center;margin-bottom:.75rem}}
.card-img img{{max-width:100%;max-height:100%;object-fit:contain;border-radius:8px}}
.card h3{{font-size:1rem;margin-bottom:.4rem;line-height:1.3}}
.card p{{font-size:.82rem;color:var(--muted);flex:1;margin-bottom:.75rem;
  display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}}
.card .read{{font-size:.8rem;color:var(--accent);font-weight:600}}

/* footer */
footer{{text-align:center;padding:3rem 1rem;color:var(--muted);font-size:.85rem;
  border-top:1px solid var(--border);margin-top:3rem}}
footer span{{margin:0 .5rem}}

@media(max-width:600px){{
  .grid{{grid-template-columns:repeat(2,1fr);gap:.75rem}}
  .card{{padding:.75rem}}
  .card-img{{width:80px;height:80px}}
  .cat-nav{{padding:.75rem;gap:.35rem}}
  .cat-nav a{{font-size:.75rem;padding:.3rem .6rem}}
}}
</style>
</head>
<body>

<header class="hero">
  <h1>Redi<span>THub</span></h1>
  <p class="tagline">Honest Product Reviews Based on Real User Feedback</p>
  <p style="max-width:650px;margin:0 auto;opacity:.75;font-size:.95rem">
    We dig into official websites, read the fine print, check ingredient labels and compare
    real customer experiences &mdash; so you can make an informed decision before you buy.
  </p>
  <div class="stats">
    <div class="stat"><strong>{total}+</strong><span>Products Reviewed</span></div>
    <div class="stat"><strong>{total_en}</strong><span>English Reviews</span></div>
    <div class="stat"><strong>{total_de}</strong><span>German Reviews</span></div>
  </div>
</header>

<div class="about">
  <h2>What We Do</h2>
  <p>Every review on this site follows the same process: we visit the product's official page,
  read every claim, check the ingredient label against published research, look for real user
  feedback, and lay out what we found &mdash; the good and the bad.</p>
  <p>We cover ingredients, side effects, dosage instructions, refund policies and customer
  support. No hype, no fake urgency. Just the facts you need.</p>
</div>

<nav class="cat-nav" aria-label="Categories">
{cat_nav}
    <a href="#de-reviews">Deutsch</a>
</nav>

{cat_sections}

{german_section}

<footer>
  <p>&copy; Wellness Trend Reviews. All product names and trademarks are property of their respective owners.</p>
  <p><span>Terms Of Use</span> &middot; <span>Disclaimer</span> &middot; <span>Privacy Policy</span></p>
</footer>

</body>
</html>'''

out = ROOT / "index.html"
out.write_text(page, encoding="utf-8")
print(f"Homepage generated: {out}")
print(f"Total products: {total} ({total_en} EN, {total_de} DE)")
print(f"Categories: {len([c for c in CATEGORIES if any(s in products for s in CATEGORIES[c])])}")
