source .env
CUR_DIR=$(pwd)
HOST="https://tools.wikilovesfolklore.org"
COOKIE="$WLF_COOKIE_NAME=$WLF_COOKIE"
BACKUP_BASE="$CUR_DIR/backups"
TOOL="WLF"
BACKUP_DIR="$BACKUP_BASE/$TOOL"
OUTPUT_FILE="$BACKUP_DIR/backup-$(date +%Y-%m-%d-%H-%M).zip"
if [ ! -d "$BACKUP_DIR" ]; then
    mkdir -p "$BACKUP_DIR"
fi
echo "cd $BACKUP_DIR"
cd "$BACKUP_DIR"
curl -s "$HOST/api/backup" -H "Cookie: $COOKIE"  > "$OUTPUT_FILE"
