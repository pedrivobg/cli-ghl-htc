#!/usr/bin/env bash
# Roda o Lighthouse (mesmo motor do PageSpeed) num site, sem depender da cota da API.
# A API anônima do PageSpeed Insights estoura a cota diária rápido; este script usa o
# Chromium da máquina e o proxy da sessão.
#
# Uso: tools/lighthouse.sh <url> [mobile|desktop]
set -euo pipefail
URL="${1:?Uso: $0 <url> [mobile|desktop]}"; MODO="${2:-mobile}"
DIR=/tmp/lh13; mkdir -p "$DIR"
[ -x "$DIR/node_modules/.bin/lighthouse" ] || (cd "$DIR" && npm init -y >/dev/null && npm i lighthouse@13 --silent)
EXTRA=""; [ "$MODO" = desktop ] && EXTRA="--preset=desktop"
OUT="$DIR/lh_${MODO}.json"
CHROME_PATH="${CHROME_PATH:-/opt/pw-browsers/chromium}" "$DIR/node_modules/.bin/lighthouse" "$URL" $EXTRA --quiet \
  --output=json --output-path="$OUT" \
  --chrome-flags="--headless=new --no-sandbox --disable-gpu --ignore-certificate-errors ${HTTPS_PROXY:+--proxy-server=$HTTPS_PROXY}"
python3 - "$OUT" <<'PY'
import json, sys
d = json.load(open(sys.argv[1])); a = d["audits"]
print({k: (round(v["score"] * 100) if v["score"] is not None else None) for k, v in d["categories"].items()})
for k in ["first-contentful-paint", "largest-contentful-paint", "total-blocking-time", "cumulative-layout-shift", "speed-index"]:
    print("  %-26s %s" % (k, a[k]["displayValue"]))
for c in d["categories"].values():
    for r in c["auditRefs"]:
        x = a[r["id"]]
        if x.get("score") is not None and x["score"] < 0.9 and x.get("scoreDisplayMode") not in ("manual", "notApplicable", "informative"):
            print("  ✗ %-32s %s" % (r["id"], x.get("displayValue", "")))
PY
