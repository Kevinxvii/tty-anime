# 🎌 CANIME-CLI

> Guarda anime in italiano e giapponese direttamente dal terminale.
> Powered by [AnimeWorld](https://www.animeworld.ac).

```
  ▄▀▀ ▄▀▄ █▄  █ █ █▄ ▄█ █▀▀  ▄▀▀ █   █
  ▀▄▄ █▀█ █ ▀█ █ █ ▀█▀ █▄▄  █   █▄▄ █
  AnimeWorld CLI  —  v2.2
```

---

## Requisiti

- **Python 3.9+**
- **MPV** — [mpv.io/installation](https://mpv.io/installation/)
- macOS o Linux

---

## Installazione

```bash
git clone https://github.com/tuousername/canime-cli
cd canime-cli
./install.sh
```

`install.sh` fa tutto da solo: controlla Python e MPV, crea il virtual environment e installa le dipendenze.

---

## Avvio

```bash
canime
```

Se hai aggiunto la cartella al PATH (consigliato), funziona da qualsiasi directory:

```bash
echo 'export PATH="$PATH:/percorso/canime-cli"' >> ~/.zshrc
source ~/.zshrc
```

---

## Utilizzo

```
🔍 Nome anime: jujutsu kaisen

  [ITA — Doppiaggio]
    1.  Jujutsu Kaisen (ITA)

  [JP — Originale / Sub]
    2.  Jujutsu Kaisen
    3.  Jujutsu Kaisen 2
    4.  Jujutsu Kaisen 3: The Culling Game Part 1

👉 Seleziona anime: 2

  Episodi  (1–30 di 24)
     1.  ✓  Ep 1        ← già visto
     2.  ✓  Ep 2
     3.     Ep 3
     ...

👉 Seleziona episodio: 3

▶  Riproduzione in fullscreen con MPV
```

Al termine di ogni episodio:

```
  [n]  ▶  Prossimo   Ep 4
  [p]  ◀  Precedente Ep 2
  [s]  ☰  Scegli episodio
  [q]  ✕  Esci
```

---

## Funzionalità

| Feature | Descrizione |
|---|---|
| 🔍 Ricerca | Cerca anime per nome, risultati da AnimeWorld |
| 🇮🇹 / 🇯🇵 | Risultati separati per doppiaggio ITA e JP/Sub |
| 📋 Episodi paginati | 30 per pagina, navigabili con `n`/`p` |
| ✅ Episodi visti | Tick verde sugli episodi già guardati, persistono tra sessioni |
| ▶️ Fullscreen | MPV parte direttamente a schermo intero |
| ⏭ Menu post-episodio | Prossimo / Precedente / Scegli / Esci |
| 🔄 Multi-dominio | Prova automaticamente `.ac` → `.so` → `.tv` |

---

## Dipendenze

```
animeworld
requests
beautifulsoup4
```

Installate automaticamente da `install.sh` nel virtual environment.

---

## Storia visti

Gli episodi guardati vengono salvati in `~/.canime_watched.json`.
Il file è leggibile e modificabile manualmente se vuoi resettare o aggiungere episodi.

```json
{
  "Naruto (ITA)": ["1", "2", "3"],
  "Jujutsu Kaisen": ["1"]
}
```

---

## Struttura progetto

```
canime-cli/
├── canime          # launcher bash (eseguibile)
├── canime.py       # sorgente principale
├── install.sh      # script di installazione
├── requirements.txt
└── README.md
```