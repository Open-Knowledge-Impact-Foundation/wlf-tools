source .env
CUR_DIR=$(pwd)
HOST="https://tools.wikilovesfolklore.org"
COOKIE="$WLF_COOKIE_NAME=$WLF_COOKIE"

curl -s "$HOST/api/statistics/sendUpdate" -H "Cookie: $COOKIE" -X POST