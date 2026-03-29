#!/bin/zsh
# Installa OpenClaw/NanoBot con Python 3.12
# Esegui DOPO aver installato Python 3.12

echo "=== Install OpenClaw with Python 3.12 ==="

# Verifica Python 3.12
if ! python3.12 --version &>/dev/null; then
    echo "❌ Python 3.12 non trovato!"
    echo "Prima installa: sudo installer -pkg /tmp/python312.pkg -target /"
    exit 1
fi

echo "✅ $(python3.12 --version)"

# Crea venv Python 3.12
VENV_DIR="$HOME/nanobot-py312"
python3.12 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

echo "Aggiorno pip..."
pip install --upgrade pip

echo "Installo OpenClaw..."
pip install openclaw

echo ""
openclaw --version 2>/dev/null || python3.12 -c "import openclaw; print('OpenClaw:', openclaw.__version__)"

echo ""
echo "✅ OpenClaw installato!"
echo ""
echo "Per usarlo:"
echo "  source $VENV_DIR/bin/activate"
echo "  openclaw --help"
