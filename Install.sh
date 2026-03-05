#!/bin/bash
set -e

CYAN='\033[36m'
GREEN='\033[32m'
RED='\033[31m'
BOLD='\033[1m'
RESET='\033[0m'

echo ""
echo -e "${CYAN}${BOLD}  ▄▀▀ ▄▀▄ █▄  █ █ █▄ ▄█ █▀▀  ▄▀▀ █   █${RESET}"
echo -e "${CYAN}${BOLD}  ▀▄▄ █▀█ █ ▀█ █ █ ▀█▀ █▄▄  █   █▄▄ █${RESET}"
echo -e "  ${BOLD}Installer${RESET}"
echo ""

# Controlla Python 3
if ! command -v python3 &>/dev/null; then
  echo -e "  ${RED}✗${RESET} Python 3 non trovato. Installa Python 3.9+."
  exit 1
fi
echo -e "  ${GREEN}✓${RESET} Python $(python3 --version)"

# Controlla MPV
if ! command -v mpv &>/dev/null; then
  echo -e "  ${RED}✗${RESET} MPV non trovato."
  echo "    macOS:  brew install mpv"
  echo "    Linux:  sudo apt install mpv  /  sudo pacman -S mpv"
  exit 1
fi
echo -e "  ${GREEN}✓${RESET} MPV trovato"

# Crea venv
echo -e "  ${CYAN}›${RESET} Creo ambiente virtuale..."
python3 -m venv venv
source venv/bin/activate

# Installa dipendenze
echo -e "  ${CYAN}›${RESET} Installo dipendenze..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Crea script launcher
cat > canime << 'LAUNCHER'
#!/bin/bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/venv/bin/activate"
python3 "$DIR/canime.py" "$@"
LAUNCHER
chmod +x canime

echo ""
echo -e "  ${GREEN}${BOLD}✓ Installazione completata!${RESET}"
echo ""
echo -e "  Per avviare:"
echo -e "  ${BOLD}  ./canime${RESET}"
echo ""