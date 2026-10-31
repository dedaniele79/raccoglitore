"""Ogni notte: scarica il listino pubblico di Cardmarket per i Pokémon e lo prepara per l'app.

Cardmarket pubblica ogni notte il listino prezzi (le stesse cifre delle pagine prodotto) e l'elenco delle carte singole.
L'app sul telefono non può leggerli direttamente (Cardmarket non lo permette da altri siti), quindi li legge da qui.
Uscita (cartella indicata come argomento):
  cm/info.json        data del listino e quantità
  cm/cerca.json       [idProduct, nome, idExpansion, numero] di tutte le carte singole (per collegare una carta)
  cm/p/<n>.json       prezzi per gruppi di idProduct (n = idProduct // 10000): {id: [trend, low, avg30, trendHolo, avg30Holo, avg]}
  cm/esempio.json     alcune righe originali, per controllo
"""
import json, os, re, sys, urllib.request

BASE = "https://downloads.s3.cardmarket.com/productCatalog"
GAME = 6  # Pokémon


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "raccoglitore-tcg/1.0 (uso personale)"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


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
    sample = {"chiavi_prodotti": list(products.keys()), "primi": plist[:15],
              "sawsbuck": [p for p in plist if "sawsbuck" in p.get("name", "").lower()][:40],
              "gem_pack": [p for p in plist if "gem pack" in json.dumps(p).lower()][:20]}
    json.dump(sample, open(f"{out}/cm/esempio.json", "w"), ensure_ascii=False, indent=1)
    print("ok", len(plist), "prodotti,", len(prices.get("priceGuides", [])), "prezzi,", len(buckets), "gruppi")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "out")
