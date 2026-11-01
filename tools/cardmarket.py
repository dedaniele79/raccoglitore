"""Ogni notte: scarica il listino pubblico di Cardmarket per i Pokémon e lo prepara per l'app.

Cardmarket pubblica ogni notte il listino prezzi (le stesse cifre delle pagine prodotto) e l'elenco delle carte singole.
L'app sul telefono non può leggerli direttamente (Cardmarket non lo permette da altri siti), quindi li legge da qui.
Uscita (cartella indicata come argomento):
  cm/info.json        data del listino e quantità
  cm/cerca.json       [idProduct, nome, idExpansion, numero] di tutte le carte singole (per collegare una carta)
  cm/p/<n>.json       prezzi per gruppi di idProduct (n = idProduct // 10000): {id: [trend, low, avg30, trendHolo, avg30Holo, avg]}
  cm/espansioni.json  {idExpansion: [nome dell'espansione, data della prima carta]}
                      Il nome viene dal catalogo TCGdex (che per ogni carta indica il prodotto Cardmarket) e, se lì non c'è,
                      dai prodotti sigillati della stessa espansione (buste, box).
  cm/esempio.json     alcune righe originali, per controllo
"""
import json, os, re, sys, time, urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor

BASE = "https://downloads.s3.cardmarket.com/productCatalog"
GAME = 6  # Pokémon


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "raccoglitore-tcg/1.0 (uso personale)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def tcgdex_names(exp_of, budget=300):
    """Nome dell'espansione Cardmarket preso da TCGdex: per ogni espansione TCGdex leggo due carte e il loro prodotto Cardmarket.
    Così le promo (es. «MEP Black Star Promos») non prendono il nome di una scatola che le contiene."""
    t0, votes = time.time(), defaultdict(Counter)
    try:
        sets = get("https://api.tcgdex.net/v2/en/sets")
    except Exception as ex:
        print("TCGdex non disponibile:", ex)
        return {}

    def one(s):
        if time.time() - t0 > budget:
            return []
        try:
            cards = get(f"https://api.tcgdex.net/v2/en/sets/{urllib.request.quote(s['id'])}").get("cards") or []
        except Exception:
            return []
        found = []
        for c in [cards[0], cards[len(cards) // 2]] if cards else []:
            try:
                pid = ((get(f"https://api.tcgdex.net/v2/en/cards/{urllib.request.quote(c['id'])}").get("pricing") or {}).get("cardmarket") or {}).get("idProduct")
            except Exception:
                continue
            if pid in exp_of:
                found.append((exp_of[pid], s["name"]))
        return found

    with ThreadPoolExecutor(8) as ex:
        for found in ex.map(one, sets):
            for e, n in found:
                votes[e][n] += 1
    print("nomi da TCGdex:", len(votes), "espansioni in", round(time.time() - t0), "s")
    return {e: c.most_common(1)[0][0] for e, c in votes.items()}


def main(out):
    prices = get(f"{BASE}/priceGuide/price_guide_{GAME}.json")
    products = get(f"{BASE}/productList/products_singles_{GAME}.json")
    os.makedirs(f"{out}/cm/p", exist_ok=True)
    plist = products.get("products", [])
    num = re.compile(r"\(([^()]*?)\)\s*$")
    cerca = []
    for p in plist:
        m = num.search(p.get("name", ""))
        cerca.append([p.get("idProduct"), p.get("name", ""), p.get("idExpansion"), m.group(1) if m else ""])
    json.dump({"creato": prices.get("createdAt"), "prodotti": len(plist), "prezzi": len(prices.get("priceGuides", []))},
              open(f"{out}/cm/info.json", "w"), ensure_ascii=False)
    json.dump(cerca, open(f"{out}/cm/cerca.json", "w"), ensure_ascii=False, separators=(",", ":"))
    buckets = {}
    r2 = lambda v: None if v is None else round(v, 2)
    for g in prices.get("priceGuides", []):
        pid = g.get("idProduct")
        if pid is None:
            continue
        buckets.setdefault(pid // 10000, {})[pid] = [r2(g.get("trend")), r2(g.get("low")), r2(g.get("avg30")),
                                                    r2(g.get("trend-holo")), r2(g.get("avg30-holo")), r2(g.get("avg"))]
    for b, d in buckets.items():
        json.dump(d, open(f"{out}/cm/p/{b}.json", "w"), separators=(",", ":"))
    # Cardmarket non pubblica i nomi delle espansioni: li ricavo dai prodotti sigillati (buste, box) della stessa espansione.
    names = {}
    try:
        sealed = get(f"{BASE}/productList/products_nonsingles_{GAME}.json").get("products", [])
        strip = re.compile(r"\s*(Booster Box|Booster Display|Booster Bundle|Booster Pack|Sleeved Booster|Booster|Display|Elite Trainer Box|Build & Battle Box|Collection Box|Premium Collection|Blister|Case|Tin)\b.*$", re.I)
        for p in sealed:
            e, n = p.get("idExpansion"), (p.get("name") or "").strip()
            if not e or not n:
                continue
            base = strip.sub("", n).strip(" -:") or n
            if e not in names or len(base) < len(names[e]):
                names[e] = base
    except Exception as ex:
        print("prodotti sigillati non disponibili:", ex)
    first = {}
    for p in plist:
        d = (p.get("dateAdded") or "")[:10]
        if d and d != "0000-00-00" and (p["idExpansion"] not in first or d < first[p["idExpansion"]]):
            first[p["idExpansion"]] = d
    exp_of = {p.get("idProduct"): p.get("idExpansion") for p in plist}
    official = tcgdex_names(exp_of)
    exps = {e: [official.get(e) or names.get(e, ""), first.get(e, "")] for e in {p.get("idExpansion") for p in plist}}
    json.dump(exps, open(f"{out}/cm/espansioni.json", "w"), ensure_ascii=False, separators=(",", ":"))
    sample = {"chiavi_prodotti": list(products.keys()), "primi": plist[:15],
              "sawsbuck": [p for p in plist if "sawsbuck" in p.get("name", "").lower()][:40],
              "gem_pack": [p for p in plist if "gem pack" in json.dumps(p).lower()][:20]}
    json.dump(sample, open(f"{out}/cm/esempio.json", "w"), ensure_ascii=False, indent=1)
    print("ok", len(plist), "prodotti,", len(prices.get("priceGuides", [])), "prezzi,", len(buckets), "gruppi")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "out")
