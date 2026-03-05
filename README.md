# 🎌 CANIME-CLI

> Guarda anime italiani e in giapponese dal terminale. Powered by [AnimeWorld](https://www.animeworld.ac).

```
  ▄▀▀ ▄▀▄ █▄  █ █ █▄ ▄█ █▀▀  ▄▀▀ █   █
  ▀▄▄ █▀█ █ ▀█ █ █ ▀█▀ █▄▄  █   █▄▄ █
  AnimeWorld CLI  —  v2.0
```

## Requisiti

- Python 3.9+
- [MPV](https://mpv.io/installation/)
- macOS / Linux

## Installazione

```bash
git clone https://github.com/tuousername/canime-cli
cd canime-cli
./install.sh
```

## Uso

```bash
./canime
```

## Funzionalità

- 🔍 Ricerca anime per nome
- 🇮🇹 / 🇯🇵 Risultati separati per doppiaggio ITA e JP/SUB
- 📋 Lista episodi paginata (30 per pagina, navigabile)
- ▶️  Riproduzione diretta con MPV
- ⏭  Menu post-episodio: **prossimo** / **precedente** / **scegli** / **esci**
- ↩️  Torna alla ricerca in qualsiasi momento

## Flusso

```
Ricerca → Selezione anime (ITA / JP) → Selezione episodio
  → Riproduzione MPV
    → [n] Prossimo ep
    → [p] Precedente ep
    → [s] Scegli episodio
    → [q] Esci
```