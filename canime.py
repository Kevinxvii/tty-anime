#!/usr/bin/env python3
"""
╔═══════════════════════════════════════╗
║   CANIME-CLI  —  AnimeWorld Edition   ║
╚═══════════════════════════════════════╝
"""

import sys, subprocess, requests, os, re, json
from urllib.parse import urljoin, quote
from bs4 import BeautifulSoup

try:
    import animeworld as aw
except ImportError:
    print("❌  Dipendenze mancanti. Esegui: pip install -r requirements.txt")
    sys.exit(1)

# ── Colori ANSI ───────────────────────────────────────────────────────────────
R   = "\033[0m"
B   = "\033[1m"
DIM = "\033[2m"
C   = "\033[36m"
Y   = "\033[33m"
G   = "\033[32m"
RD  = "\033[31m"
M   = "\033[35m"

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

# Domini AnimeWorld da provare in ordine
AW_DOMAINS = [
    "https://www.animeworld.ac",
    "https://www.animeworld.so",
    "https://www.animeworld.tv",
]

BANNER = f"""
{C}{B}  ▄▀▀ ▄▀▄ █▄  █ █ █▄ ▄█ █▀▀  ▄▀▀ █   █{R}
{C}{B}  ▀▄▄ █▀█ █ ▀█ █ █ ▀█▀ █▄▄  █   █▄▄ █{R}
{DIM}  AnimeWorld CLI  —  v2.2{R}
"""

_base_url = None  # dominio attivo rilevato

# ── Watch history ─────────────────────────────────────────────────────────────
WATCH_FILE = os.path.expanduser("~/.canime_watched.json")

def _load_watched() -> dict:
    try:
        if os.path.exists(WATCH_FILE):
            return json.load(open(WATCH_FILE))
    except Exception:
        pass
    return {}

def _save_watched(data: dict):
    try:
        json.dump(data, open(WATCH_FILE, "w"), indent=2)
    except Exception:
        pass

def mark_watched(anime_name: str, ep_number: str):
    data = _load_watched()
    key  = anime_name.strip()
    if key not in data:
        data[key] = []
    if ep_number not in data[key]:
        data[key].append(ep_number)
    _save_watched(data)

def get_watched(anime_name: str) -> set:
    data = _load_watched()
    return set(data.get(anime_name.strip(), []))

def banner():
    os.system("clear")
    print(BANNER)

def info(msg):  print(f"  {C}›{R} {msg}")
def ok(msg):    print(f"  {G}✓{R} {msg}")
def err(msg):   print(f"  {RD}✗{R} {msg}"); sys.exit(1)
def sep():      print(f"  {DIM}{'─'*46}{R}")

def prompt(msg, default=None):
    suffix = f" {DIM}[{default}]{R}" if default else ""
    try:
        val = input(f"\n  {Y}›{R} {B}{msg}{R}{suffix} ").strip()
        return val if val else default
    except (EOFError, KeyboardInterrupt):
        print(); sys.exit(0)

# ── Rileva dominio attivo ─────────────────────────────────────────────────────
def get_base() -> str:
    global _base_url
    if _base_url:
        return _base_url
    for domain in AW_DOMAINS:
        try:
            r = requests.get(domain + "/", timeout=8,
                             headers={"User-Agent": UA, "Accept": "text/html"})
            if r.status_code == 200:
                _base_url = domain
                return domain
        except Exception:
            continue
    err("Nessun dominio AnimeWorld raggiungibile.")

# ── Ricerca anime ─────────────────────────────────────────────────────────────
def search_anime(query: str) -> list[dict]:
    """
    Metodo 1: aw.find() ufficiale.
    Metodo 2: API /api/search con scraping HTML della risposta {"html":"..."}.
    I risultati vengono filtrati per rilevanza (il titolo deve contenere
    almeno una parola della query).
    """
    results = []
    seen    = set()
    words   = [w.lower() for w in query.split() if len(w) > 2]

    def is_relevant(title: str) -> bool:
        t = title.lower()
        return any(w in t for w in words)

    def add(title, link):
        if link in seen: return
        if not is_relevant(title): return
        seen.add(link)
        results.append({"name": title, "link": link})

    # Metodo 1: libreria ufficiale
    try:
        found = aw.find(query)
        if found:
            if isinstance(found, dict): found = [found]
            for a in found:
                title = a.get("name") or a.get("title","")
                link  = a.get("link","")
                add(title, link)
    except Exception:
        pass

    # Metodo 2: API /api/search → {"html":"..."}
    try:
        base = get_base()
        r = requests.get(
            f"{base}/api/search?keyword={quote(query)}",
            timeout=15,
            headers={
                "User-Agent": UA,
                "Accept": "application/json",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": base + "/",
            },
        )
        data = r.json()

        # Caso A: array diretto
        items = []
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            items = data.get("animes") or data.get("data") or data.get("results") or []

        for item in items:
            title = item.get("title") or item.get("name","")
            link  = item.get("link")  or item.get("slug","")
            if link and "/play/" not in link:
                link = f"{base}/play/{link}"
            if title and link: add(title, link)

        # Caso B: {"html":"..."} — scraping
        if not items and isinstance(data, dict) and "html" in data:
            soup = BeautifulSoup(data["html"], "html.parser")
            # AnimeWorld mette href="play/slug" nei tag <a>
            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"]
                if "play/" not in href: continue
                slug = href.split("play/")[-1].rstrip("/")
                link = f"{base}/play/{slug}"
                # Il titolo sta nel tag con class "name" vicino all'<a>
                parent  = a_tag.find_parent()
                nm_tag  = (parent.find(class_=re.compile(r"\bname\b", re.I)) if parent else None)
                title   = nm_tag.get_text(strip=True) if nm_tag else ""
                if not title:
                    title = slug.rsplit(".", 1)[0].replace("-", " ").title()
                add(title, link)

    except Exception:
        pass

    return results

# ── Risoluzione URL SweetPixel ────────────────────────────────────────────────
def resolve_stream_url(raw_url: str) -> str:
    r = requests.get(raw_url, timeout=15, headers={
        "User-Agent": UA,
        "Referer": get_base() + "/",
    })
    ct = r.headers.get("Content-Type", "")
    if "video" in ct or "octet-stream" in ct:
        return raw_url
    soup = BeautifulSoup(r.text, "html.parser")
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if any(href.endswith(ext) for ext in (".mp4", ".mkv", ".avi", ".m3u8")):
            return urljoin(r.url, href)
    for tag in soup.find_all(["source", "video"]):
        src = tag.get("src", "")
        if src:
            return urljoin(r.url, src)
    return raw_url

# ── Picker episodi paginato ───────────────────────────────────────────────────
def pick_episode(episodes: list, anime_name: str = "") -> tuple:
    total   = len(episodes)
    page_sz = 30
    page    = 0

    while True:
        lo    = page * page_sz
        hi    = min(lo + page_sz, total)
        chunk = episodes[lo:hi]

        print()
        sep()
        print(f"  {B}Episodi{R}  {DIM}({lo+1}–{hi} di {total}){R}")
        sep()

        for i, ep in enumerate(chunk):
            gi = lo + i + 1
            watched = get_watched(anime_name)
            tick = f"  {G}✓{R}" if ep.number in watched else "   "
            print(f"  {DIM}{gi:>4}.{R}{tick}  Ep {B}{ep.number}{R}")

        nav = []
        if lo > 0:   nav.append(f"{DIM}p{R}=prec.pagina")
        if hi < total: nav.append(f"{DIM}n{R}=prox.pagina")
        nav.append(f"{DIM}0{R}=indietro")
        print(f"\n  {DIM}{' │ '.join(nav)}{R}")

        raw = prompt(f"Seleziona episodio [1-{total}]:").lower()

        if raw == "0":   return None, -1
        if raw == "p" and lo > 0:   page -= 1; continue
        if raw == "n" and hi < total: page += 1; continue
        try:
            gi = int(raw) - 1
            if 0 <= gi < total:
                return episodes[gi], gi
        except ValueError:
            pass
        print(f"  {RD}  Valore non valido.{R}")

# ── Riproduzione + menu post-episodio ─────────────────────────────────────────
def play_episode(ep, episodes: list, ep_idx: int, anime_name: str) -> int:
    info(f"Recupero URL stream per Ep {ep.number}...")
    try:
        raw_url = str(ep.links[0].link)
    except Exception as e:
        print(f"  {RD}✗{R} {e}"); return -1

    info("Risolvo URL...")
    final_url = resolve_stream_url(raw_url)
    ok(f"Stream pronto")

    print()
    info(f"{G}{B}Riproduzione:{R} {anime_name} — Ep {ep.number}")
    print()

    try:
        subprocess.run([
            "mpv", "--no-ytdl",
            "--fs",
            "--geometry=100%x100%",
            f"--user-agent={UA}",
            f"--referrer={get_base()}/",
            f"--title=CANIME │ {anime_name} │ Ep {ep.number}",
            "--really-quiet",
            final_url,
        ])
        mark_watched(anime_name, ep.number)
    except FileNotFoundError:
        err("MPV non trovato. Installa: https://mpv.io/installation/")

    # Menu post-episodio
    total    = len(episodes)
    has_next = ep_idx + 1 < total
    has_prev = ep_idx > 0

    os.system("clear")
    print(BANNER)
    sep()
    print(f"  {G}✓{R}  {B}{anime_name}{R} — Ep {ep.number} terminato")
    sep()
    print()

    options = []
    if has_next:
        options.append(("n", f"▶   Prossimo   {DIM}Ep {episodes[ep_idx+1].number}{R}"))
    if has_prev:
        options.append(("p", f"◀   Precedente  {DIM}Ep {episodes[ep_idx-1].number}{R}"))
    options.append(("s", "☰   Scegli episodio"))
    options.append(("q", "✕   Esci"))

    for key, label in options:
        print(f"  {Y}{B}[{key}]{R}  {label}")

    choice = prompt("Cosa vuoi fare?").lower()

    if choice == "n" and has_next: return ep_idx + 1
    if choice == "p" and has_prev: return ep_idx - 1
    if choice == "s": return -1
    return -2

# ── Selezione anime ───────────────────────────────────────────────────────────
def select_anime():
    while True:
        banner()
        query = prompt("Nome anime:").strip()
        if not query:
            continue

        info("Ricerca in corso...")
        results = search_anime(query)

        if not results:
            print(f"  {RD}✗{R} Nessun risultato per '{query}'.")
            prompt("Premi invio per riprovare...")
            continue

        # Separa ITA e JP/SUB
        ita = [a for a in results if "(ITA)" in (a.get("name") or a.get("title",""))]
        jap = [a for a in results if "(ITA)" not in (a.get("name") or a.get("title",""))]
        all_results = ita + jap

        print()
        sep()
        print(f"  {B}Risultati{R}  {DIM}({len(all_results)} trovati){R}")
        sep()

        if ita:
            print(f"\n  {M}{B}[ITA — Doppiaggio]{R}")
            for i, a in enumerate(ita, 1):
                print(f"  {DIM}{i:>3}.{R}  {B}{a.get('name') or a.get('title','?')}{R}")

        if jap:
            off = len(ita)
            print(f"\n  {C}{B}[JP — Originale / Sub]{R}")
            for i, a in enumerate(jap, 1):
                print(f"  {DIM}{i+off:>3}.{R}  {B}{a.get('name') or a.get('title','?')}{R}")

        print(f"\n  {DIM}0.  ← Nuova ricerca{R}")

        while True:
            raw = prompt(f"Seleziona anime [0-{len(all_results)}]:")
            try:
                idx = int(raw) - 1
                if idx == -1:
                    break
                if 0 <= idx < len(all_results):
                    anime_info = all_results[idx]
                    name = anime_info.get("name") or anime_info.get("title","")
                    ok(name)
                    info("Carico episodi...")
                    try:
                        anime    = aw.Anime(link=anime_info.get("link",""))
                        episodes = anime.getEpisodes()
                    except Exception as e:
                        print(f"  {RD}✗{R} {e}")
                        prompt("Premi invio per riprovare...")
                        break
                    if not episodes:
                        print(f"  {RD}✗{R} Nessun episodio trovato.")
                        prompt("Premi invio per riprovare...")
                        break
                    ok(f"{len(episodes)} episodi disponibili")
                    return anime_info, episodes
            except (ValueError, TypeError):
                pass
            print(f"  {RD}  Valore non valido.{R}")

# ── Main loop ─────────────────────────────────────────────────────────────────
def main():
    # Rileva dominio all'avvio
    info("Connessione ad AnimeWorld...")
    base = get_base()
    ok(f"Connesso a {base}")

    while True:
        anime_info, episodes = select_anime()
        anime_name = anime_info.get("name") or anime_info.get("title","")
        ep_idx = None

        while True:
            if ep_idx is None:
                ep, ep_idx = pick_episode(episodes, anime_name)
                if ep is None:
                    break

            ep     = episodes[ep_idx]
            result = play_episode(ep, episodes, ep_idx, anime_name)

            if result >= 0:   ep_idx = result
            elif result == -1: ep_idx = None
            else:
                os.system("clear")
                print(BANNER)
                print(f"  {DIM}Ciao!{R}\n")
                sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n  {DIM}Uscita.{R}\n")
        sys.exit(0)