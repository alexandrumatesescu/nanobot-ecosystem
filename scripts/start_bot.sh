#!/bin/zsh
# NanoBot Local - Avvio Bot
# Avvia l'agente locale e sincronizzazione continua

export PATH="$HOME/bin:$PATH"
ECOSYSTEM_DIR="$HOME/nanobot-ecosystem"
LOG_DIR="$ECOSYSTEM_DIR/logs"

# Carica variabili ambiente
if [ -f "$ECOSYSTEM_DIR/config/.env" ]; then
    source "$ECOSYSTEM_DIR/config/.env"
    export GITHUB_TOKEN GITHUB_OWNER GITHUB_REPO
else
    echo "⚠️  config/.env non trovato. Esegui prima setup_github.sh"
    exit 1
fi

mkdir -p "$LOG_DIR"

echo "=== NanoBot Local Bot Avviato ==="
echo "Timestamp: $(date)"
echo "Workspace: $ECOSYSTEM_DIR"
echo ""

# Funzione sync loop
sync_loop() {
    while true; do
        echo "[$(date '+%H:%M:%S')] Sync con GitHub..."
        python3 "$ECOSYSTEM_DIR/scripts/github_sync.py" tasks 2>&1 | tee -a "$LOG_DIR/sync.log"
        echo "[$(date '+%H:%M:%S')] Prossima sync in 5 minuti..."
        sleep 300
    done
}

# Status iniziale
python3 "$ECOSYSTEM_DIR/scripts/local_agent.py" status

echo ""
echo "Avvio sync loop in background..."
sync_loop &
SYNC_PID=$!
echo "Sync PID: $SYNC_PID"

echo $SYNC_PID > "$LOG_DIR/sync.pid"
echo ""
echo "✅ Bot attivo! Log: $LOG_DIR/sync.log"
echo "Per stoppare: kill $(cat $LOG_DIR/sync.pid)"
