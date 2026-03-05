```python
#!/usr/bin/env python3
"""
CANIME-CLI v3 — AnimeWorld
"""

import sys
import subprocess
import requests
import os
import re
import json
import threading
from urllib.parse import urljoin, quote
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

try:
    import animeworld as aw
except ImportError:
    print("Dipendenze mancanti: pip install animeworld bs4 requests")
    sys.exit(1)

UA = "Mozilla/5.0 Chrome/124 Safari/537.36"

AW_DOMAINS = [
    "https://www.animeworld.ac",
    "https://www.animeworld.so",
    "https://www.animeworld.tv"
]

CACHE_FILE = os.path.expanduser("~/.canime_cache.json")
STATE_FILE = os.path.expanduser("~/.canime_state.json")

AUTO_NEXT = False
TIMEOUT = 10

session = requests.Session()

retry = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=[429,500,502,503,504]
)

adapter = HTTPAdapter(max_retries=retry)
session.mount("http://", adapter)
session.mount("https://", adapter)

session.headers.update({
    "User-Agent": UA
})

_base_url = None


def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            return json.load(open(CACHE_FILE))
        except:
            pass
    return {}

def save_cache(data):
    try:
        json.dump(data, open(CACHE_FILE,"w"))
    except:
        pass

CACHE = load_cache()


def save_state(anime, ep):
    try:
        json.dump({"anime":anime,"ep":ep}, open(STATE_FILE,"w"))
    except:
        pass


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            return json.load(open(STATE_FILE))
        except:
            pass
    return None


def get_base():
    global _base_url
    if _base_url:
        return _base_url

    for d in AW_DOMAINS:
        try:
            r = session.get(d, timeout=TIMEOUT)
            if r.status_code == 200:
                _base_url = d
                return d
        except:
            pass

    print("AnimeWorld non raggiungibile")
    sys.exit(1)


def search_anime(query):

    if query in CACHE:
        return CACHE[query]

    results = []
    seen = set()

    base = get_base()

    try:
        found = aw.find(query)
        if isinstance(found, dict):
            found = [found]

        for a in found:
            name = a.get("name")
            link = a.get("link")
            if link not in seen:
                seen.add(link)
                results.append({"name":name,"link":link})
    except:
        pass

    try:
        r = session.get(
            f"{base}/api/search?keyword={quote(query)}",
            timeout=TIMEOUT,
            headers={"Accept":"application/json","X-Requested-With":"XMLHttpRequest"}
        )

        data = r.json()

        if isinstance(data, dict) and "html" in data:
            soup = BeautifulSoup(data["html"],"html.parser")

            for a in soup.find_all("a",href=True):
                if "play/" not in a["href"]:
                    continue

                slug = a["href"].split("play/")[-1]
                link = f"{base}/play/{slug}"

                title = slug.replace("-"," ").title()

                if link not in seen:
                    seen.add(link)
                    results.append({"name":title,"link":link})

    except:
        pass

    CACHE[query] = results
    save_cache(CACHE)

    return results


def resolve_stream(url):

    r = session.get(url, timeout=TIMEOUT)

    ct = r.headers.get("Content-Type","")

    if "video" in ct:
        return url

    soup = BeautifulSoup(r.text,"html.parser")

    for tag in soup.find_all(["source","video"]):
        src = tag.get("src")
        if src:
            return urljoin(r.url, src)

    for script in soup.find_all("script"):
        if "m3u8" in script.text:
            m = re.search(r"https?://.*\.m3u8", script.text)
            if m:
                return m.group(0)

    for a in soup.find_all("a",href=True):
        if a["href"].endswith(".mp4"):
            return urljoin(r.url,a["href"])

    return url


def pick_episode(episodes):

    total = len(episodes)

    while True:

        print("\nEpisodi disponibili:", total)

        raw = input("episodio (numero / latest / 0): ").strip()

        if raw == "0":
            return None, -1

        if raw == "latest":
            return episodes[-1], total-1

        try:
            i = int(raw)-1
            if 0 <= i < total:
                return episodes[i], i
        except:
            pass


def play_episode(ep, episodes, idx, anime_name):

    print("recupero stream...")

    try:
        raw = ep.links[0].link
    except:
        print("errore episodio")
        return -1

    url = resolve_stream(raw)

    print("riproduzione:", anime_name, "ep", ep.number)

    try:
        subprocess.run([
            "mpv",
            "--no-ytdl",
            f"--user-agent={UA}",
            url
        ])
    except FileNotFoundError:
        print("mpv non installato")
        sys.exit(1)

    save_state(anime_name, ep.number)

    total = len(episodes)

    if AUTO_NEXT and idx+1 < total:
        return idx+1

    print("\n[n] prossimo")
    print("[p] precedente")
    print("[s] scegli episodio")
    print("[d] download episodio")
    print("[q] esci")

    c = input("> ").lower()

    if c=="n" and idx+1<total:
        return idx+1

    if c=="p" and idx>0:
        return idx-1

    if c=="d":
        subprocess.run(["yt-dlp", url])
        return idx

    if c=="s":
        return -1

    return -2


def select_anime():

    while True:

        q = input("\nAnime: ").strip()

        if not q:
            continue

        results = search_anime(q)

        if not results:
            print("nessun risultato")
            continue

        for i,a in enumerate(results,1):
            print(i, a["name"])

        raw = input("scegli: ")

        try:
            idx = int(raw)-1
            if idx<0:
                continue

            a = results[idx]

            print("carico episodi...")

            anime = aw.Anime(link=a["link"])

            eps = anime.getEpisodes()

            print("episodi:", len(eps))

            return a, eps

        except:
            pass


def main():

    print("CANIME CLI v3")

    base = get_base()

    print("dominio:", base)

    state = load_state()

    if state:
        print("ultimo episodio visto:", state["anime"], "ep", state["ep"])

    while True:

        anime_info, episodes = select_anime()

        anime_name = anime_info["name"]

        ep_idx = None

        while True:

            if ep_idx is None:
                ep, ep_idx = pick_episode(episodes)
                if ep is None:
                    break

            ep = episodes[ep_idx]

            result = play_episode(ep, episodes, ep_idx, anime_name)

            if result >= 0:
                ep_idx = result
            elif result == -1:
                ep_idx = None
            else:
                sys.exit(0)


if __name__ == "__main__":

    try:
        main()
    except KeyboardInterrupt:
        print("\nuscita")
```
