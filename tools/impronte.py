"""Impronte delle carte per il riconoscimento per immagine (come fanno le app tipo PokéCardex).

Per ogni carta del catalogo TCGdex (edizione internazionale) scarica l'immagine piccola e calcola un'impronta
dell'illustrazione: è la stessa in tutte le lingue occidentali, quindi vale anche per le carte italiane.
L'app calcola la stessa impronta sulla carta inquadrata e trova la carta più simile in pochi millisecondi.

Impronta (versione 1), sulla zona dell'illustrazione x 12-88 %, y 14-44 % della carta:
  - «forma»: hash percettivo DCT a 64 bit sui grigi ridotti a 32x32 (media per aree);
  - «colore»: la stessa zona ridotta a 3x3, 27 valori RGB.
L'app (app.html, funzione fingerprint) usa esattamente gli stessi passi.

Uscita (cartella indicata come argomento): impronte.json {versione, creato, carte: [[id, hash esadecimale, colore base64]]}
Incrementale: riusa le impronte già calcolate (file precedente, se c'è) e calcola solo le carte nuove.
Con --prova aggiunge una verifica: deforma 300 immagini come foto (prospettiva, sfocatura, luce, colore, JPEG)
e misura quante volte la carta giusta è la prima trovata.
"""
import base64, io, json, math, os, random, sys, time, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor

from PIL import Image, ImageEnhance, ImageFilter

API = "https://api.tcgdex.net/v2/en"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15 raccoglitore-tcg/1.0"
REGION = (0.12, 0.88, 0.14, 0.44)  # x0, x1, y0, y1
POCKET = lambda s: s in ("tcgp",) or (len(s) <= 4 and s[:1] in "AB" and s[1:2].isdigit()) or s in ("P-A", "P-B")


def get(url, tries=3, raw=False):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
                return data if raw else json.loads(data)
        except urllib.error.HTTPError as ex:
            if ex.code == 404 or i == tries - 1:
                raise
            time.sleep(2 * (i + 1))
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(2 * (i + 1))


def box_resize(gray, w, h, ow, oh):
    """Riduzione per medie d'area (come il ricampionamento «box»): ogni pixel d'uscita è la media dei pixel che copre."""
    out = [0.0] * (ow * oh)
    for oy in range(oh):
        y0, y1 = oy * h / oh, (oy + 1) * h / oh
        for ox in range(ow):
            x0, x1 = ox * w / ow, (ox + 1) * w / ow
            tot = area = 0.0
            yy = int(y0)
            while yy < y1 and yy < h:
                fy = min(y1, yy + 1) - max(y0, yy)
                xx = int(x0)
                while xx < x1 and xx < w:
                    fx = min(x1, xx + 1) - max(x0, xx)
                    a = fx * fy
                    tot += gray[yy * w + xx] * a
                    area += a
                    xx += 1
                yy += 1
            out[oy * ow + ox] = tot / area if area else 0.0
    return out


COS = [[math.cos((2 * x + 1) * u * math.pi / 64) for x in range(32)] for u in range(8)]


def fingerprint(img):
    """img: carta intera dritta (PIL). Restituisce (hash esadecimale a 16 cifre, colore base64)."""
    img = img.convert("RGB")
    W, H = img.size
    x0, x1, y0, y1 = REGION
    reg = img.crop((round(W * x0), round(H * y0), round(W * x1), round(H * y1)))
    rw, rh = reg.size
    # Prima riduzione veloce a 128x128 con PIL (media per aree), poi la riduzione esatta a 32x32 come nell'app.
    reg = reg.resize((128, 128), Image.BOX)
    px = list(reg.getdata())
    gray = [0.299 * r + 0.587 * g + 0.114 * b for r, g, b in px]
    g32 = box_resize(gray, 128, 128, 32, 32)
    # DCT 2D, solo le frequenze basse 8x8.
    tmp = [[sum(g32[y * 32 + x] * COS[u][x] for x in range(32)) for u in range(8)] for y in range(32)]
    dct = [[sum(tmp[y][u] * COS[v][y] for y in range(32)) for u in range(8)] for v in range(8)]
    vals = [dct[v][u] for v in range(8) for u in range(8)][1:]  # senza la media
    med = sorted(vals)[len(vals) // 2]
    bits = 0
    for i, c in enumerate(vals):
        if c > med:
            bits |= 1 << i
    rgb = bytes(v for p in reg.resize((3, 3), Image.BOX).getdata() for v in p)
    return f"{bits:016x}", base64.b64encode(rgb).decode()


def hamming(a, b):
    return bin(int(a, 16) ^ int(b, 16)).count("1")


def color_dist(a, b):
    A, B = base64.b64decode(a), base64.b64decode(b)
    ma = [sum(A[k] for k in range(ch, 27, 3)) / 9 for ch in range(3)]
    mb = [sum(B[k] for k in range(ch, 27, 3)) / 9 for ch in range(3)]
    return sum(abs((A[k] - ma[k % 3]) - (B[k] - mb[k % 3])) for k in range(27)) / 27


def cards_list():
    sets = get(f"{API}/sets")
    out = []
    for s in sets:
        if POCKET(s["id"]):
            continue
        try:
            d = get(f"{API}/sets/{urllib.request.quote(s['id'])}")
        except Exception as ex:
            print("salto", s["id"], ex)
            continue
        if (d.get("serie") or {}).get("id") == "tcgp":
            continue
        for c in d.get("cards") or []:
            if c.get("image"):
                out.append((c["id"], c["image"]))
    return out


def one(item):
    cid, base = item
    try:
        im = Image.open(io.BytesIO(get(f"{base}/low.webp", raw=True)))
        h, col = fingerprint(im)
        return cid, h, col, im if PROVA else None
    except Exception as ex:
        return cid, None, None, None


def distort(im, rnd):
    """Simula una foto col telefono: carta un po' storta e ritagliata male, sfocata, più chiara o più scura, JPEG."""
    im = im.convert("RGB").resize((600, 825))
    W, H = im.size
    j = lambda: rnd.uniform(-0.025, 0.025)
    # Ritaglio imperfetto (come un raddrizzamento non preciso): angoli spostati fino al 2,5 %.
    quad = [W * j(), H * j(), W * j(), H * (1 + j()), W * (1 + j()), H * (1 + j()), W * (1 + j()), H * j()]
    im = im.transform((W, H), Image.QUAD, quad, Image.BILINEAR)
    im = im.filter(ImageFilter.GaussianBlur(rnd.uniform(0.3, 1.6)))
    im = ImageEnhance.Brightness(im).enhance(rnd.uniform(0.7, 1.25))
    im = ImageEnhance.Contrast(im).enhance(rnd.uniform(0.75, 1.2))
    im = ImageEnhance.Color(im).enhance(rnd.uniform(0.8, 1.2))
    # Riflesso: una macchia chiara in un punto a caso.
    if rnd.random() < 0.5:
        glare = Image.new("L", (W, H), 0)
        from PIL import ImageDraw
        cx, cy, r = rnd.uniform(0, W), rnd.uniform(0, H * 0.6), rnd.uniform(60, 160)
        ImageDraw.Draw(glare).ellipse((cx - r, cy - r, cx + r, cy + r), fill=rnd.randint(60, 140))
        glare = glare.filter(ImageFilter.GaussianBlur(40))
        im = Image.composite(Image.new("RGB", (W, H), (255, 255, 255)), im, glare)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=rnd.randint(55, 85))
    return Image.open(io.BytesIO(buf.getvalue()))


PROVA = "--prova" in sys.argv


def main(out, prev=None):
    t0 = time.time()
    old = {}
    if prev and os.path.exists(prev):
        try:
            for cid, h, col in json.load(open(prev))["carte"]:
                old[cid] = (h, col)
        except Exception as ex:
            print("impronte precedenti non leggibili:", ex)
    cards = cards_list()
    todo = [c for c in cards if c[0] not in old] if not PROVA else cards
    print(len(cards), "carte con immagine,", len(old), "impronte già pronte,", len(todo), "da calcolare")
    budget = float(os.environ.get("TEMPO_MAX", "18000"))
    res, samples = dict(old), []
    with ThreadPoolExecutor(12) as ex:
        for i, (cid, h, col, im) in enumerate(ex.map(one, todo)):
            if h:
                res[cid] = (h, col)
                if PROVA and im is not None and len(samples) < 300 and random.random() < 0.05:
                    samples.append((cid, im))
            if i % 1000 == 0:
                print(i, "su", len(todo), round(time.time() - t0), "s")
            if time.time() - t0 > budget:
                print("tempo finito: le altre al prossimo giro")
                break
    keep = {c[0] for c in cards}
    carte = [[cid, h, col] for cid, (h, col) in sorted(res.items()) if cid in keep]
    os.makedirs(out, exist_ok=True)
    json.dump({"versione": 1, "regione": REGION, "creato": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "carte": carte},
              open(f"{out}/impronte.json", "w"), separators=(",", ":"))
    print("ok", len(carte), "impronte in", round(time.time() - t0), "s")
    if PROVA and samples:
        prova(samples, carte)


def prova(samples, carte):
    rnd = random.Random(7)
    ok1 = ok5 = 0
    marg = []
    ints = [(id_, int(H, 16), C) for id_, H, C in carte]
    for cid, im in samples:
        h, col = fingerprint(distort(im, rnd))
        hi = int(h, 16)
        near = sorted(((bin(hi ^ H).count("1"), id_, C) for id_, H, C in ints))[:60]
        sc = sorted(((d + 0.15 * color_dist(col, C), id_) for d, id_, C in near))
        ids = [x[1] for x in sc[:5]]
        ok1 += ids[0] == cid
        ok5 += cid in ids
        if ids[0] == cid:
            marg.append(round(sc[1][0] - sc[0][0], 1))
    n = len(samples)
    print(f"PROVA: {n} foto simulate, carta giusta prima {ok1}/{n} ({100 * ok1 / n:.0f} %), tra le prime 5 {ok5}/{n} ({100 * ok5 / n:.0f} %)")
    marg.sort()
    print("PROVA: distacco dalla seconda (quando giusta), percentili 10/50/90:", marg[len(marg) // 10] if marg else None, marg[len(marg) // 2] if marg else None, marg[9 * len(marg) // 10] if marg else None)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    main(args[0] if args else "out", args[1] if len(args) > 1 else None)
