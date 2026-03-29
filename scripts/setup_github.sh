#!/bin/zsh
# NanoBot Ecosystem - GitHub Setup Script
# Esegui questo script una sola volta per configurare GitHub

export PATH="$HOME/bin:$PATH"

echo "=== NanoBot Ecosystem - GitHub Setup ==="
echo ""

# 1. Autenticazione GitHub
echo "STEP 1: Login GitHub"
if ! gh auth status &>/dev/null; then
    echo "Avvio autenticazione GitHub..."
    gh auth login --web --hostname github.com --git-protocol https
else
    echo "✅ Già autenticato con GitHub"
fi

echo ""
GH_USER=$(gh api user --jq '.login' 2>/dev/null)
echo "✅ Utente GitHub: $GH_USER"

# 2. Crea repository
echo ""
echo "STEP 2: Creazione repository nanobot-ecosystem"
if gh repo view "$GH_USER/nanobot-ecosystem" &>/dev/null; then
    echo "✅ Repository già esistente"
else
    gh repo create nanobot-ecosystem \
        --public \
        --description "NanoBot VPS + Local Ecosystem Coordination Hub" \
        --add-readme
    echo "✅ Repository creato: github.com/$GH_USER/nanobot-ecosystem"
fi

# 3. Crea labels per task queue
echo ""
echo "STEP 3: Configurazione labels"
for label in "task" "local" "vps" "status" "sync" "automation"; do
    gh label create "$label" --repo "$GH_USER/nanobot-ecosystem" --color "#0075ca" 2>/dev/null || true
done
echo "✅ Labels creati"

# 4. Clone/setup locale
echo ""
echo "STEP 4: Setup directory locale"
ECOSYSTEM_DIR="$HOME/nanobot-ecosystem"
if [ ! -d "$ECOSYSTEM_DIR/.git" ]; then
    cd "$ECOSYSTEM_DIR"
    git init
    git remote add origin "https://github.com/$GH_USER/nanobot-ecosystem.git"
    echo "✅ Git inizializzato in $ECOSYSTEM_DIR"
fi

# 5. Genera token per automazione
echo ""
echo "STEP 5: Genera token automazione"
echo "Vai su: https://github.com/settings/tokens/new"
echo "  - Nome: nanobot-local"
echo "  - Scadenza: 1 year"
echo "  - Permessi: repo (tutto), workflow, read:user"
echo ""
read "GITHUB_TOKEN?Incolla il token generato: "

if [ -n "$GITHUB_TOKEN" ]; then
    # Salva nel file di ambiente
    cat > "$ECOSYSTEM_DIR/config/.env" << EOF
GITHUB_TOKEN=$GITHUB_TOKEN
GITHUB_OWNER=$GH_USER
GITHUB_REPO=nanobot-ecosystem
EOF
    chmod 600 "$ECOSYSTEM_DIR/config/.env"
    echo "✅ Token salvato in config/.env"

    # Test token
    source "$ECOSYSTEM_DIR/config/.env"
    python3 "$ECOSYSTEM_DIR/scripts/github_sync.py" status
fi

echo ""
echo "=== Setup Completato! ==="
echo "Repository: https://github.com/$GH_USER/nanobot-ecosystem"
echo "Directory locale: $ECOSYSTEM_DIR"
echo ""
echo "Prossimo passo: installa Python 3.12"
echo "  sudo installer -pkg /tmp/python312.pkg -target /"
