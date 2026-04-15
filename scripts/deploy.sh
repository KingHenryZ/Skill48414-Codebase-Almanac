#!/usr/bin/env bash
# deploy.sh — Deploy a code visualization to Vercel for sharing
#
# Usage:
#   bash scripts/deploy.sh <path-to-visualization-html-or-folder>
#
# Examples:
#   bash scripts/deploy.sh ./my-project-visualization.html
#   bash scripts/deploy.sh ./output/
#
# Deploys to a permanent, shareable URL that works on any device.
set -euo pipefail

# ─── Colors ────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

info()  { echo -e "${CYAN}ℹ${NC} $*"; }
ok()    { echo -e "${GREEN}✓${NC} $*"; }
warn()  { echo -e "${YELLOW}⚠${NC} $*"; }
err()   { echo -e "${RED}✗${NC} $*" >&2; }

# ─── Input validation ─────────────────────────────────────

if [[ $# -lt 1 ]]; then
    err "Usage: bash scripts/deploy.sh <path-to-html-or-folder>"
    err ""
    err "Examples:"
    err "  bash scripts/deploy.sh ./visualization.html"
    err "  bash scripts/deploy.sh ./output/"
    exit 1
fi

INPUT="$1"

if [[ -f "$INPUT" && "$INPUT" == *.html ]]; then
    DEPLOY_DIR=$(mktemp -d)
    cp "$INPUT" "$DEPLOY_DIR/index.html"
    CLEANUP_TEMP=true
    info "Single HTML file detected — preparing for deployment..."
elif [[ -d "$INPUT" ]]; then
    if [[ ! -f "$INPUT/index.html" ]]; then
        err "Folder '$INPUT' does not contain an index.html file."
        exit 1
    fi
    DEPLOY_DIR="$INPUT"
    CLEANUP_TEMP=false
else
    err "'$INPUT' is not a valid HTML file or directory."
    exit 1
fi

# ─── Check for Vercel CLI ─────────────────────────────────

echo ""
echo -e "${BOLD}╔══════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║    Deploy Code Visualization to Vercel    ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════╝${NC}"
echo ""

if ! command -v npx &>/dev/null; then
    err "Node.js is required but not installed."
    err "  macOS:   brew install node"
    err "  or visit https://nodejs.org"
    exit 1
fi

info "Checking Vercel CLI..."

if command -v vercel &>/dev/null; then
    VERCEL_CMD="vercel"
    ok "Vercel CLI found"
elif npx --yes vercel --version &>/dev/null 2>&1; then
    VERCEL_CMD="npx --yes vercel"
    ok "Vercel CLI available via npx"
else
    info "Installing Vercel CLI..."
    npm install -g vercel
    VERCEL_CMD="vercel"
    ok "Vercel CLI installed"
fi

# ─── Check login status ───────────────────────────────────

echo ""
info "Checking Vercel login status..."

if ! $VERCEL_CMD whoami &>/dev/null 2>&1; then
    echo ""
    warn "You're not logged in to Vercel yet."
    echo ""
    echo -e "${BOLD}To log in:${NC}"
    echo "  1. Go to https://vercel.com/signup (free)"
    echo "  2. Run: vercel login"
    echo "  3. Re-run this deploy script"
    echo ""
    echo -e "${YELLOW}Attempting interactive login now...${NC}"
    echo ""
    $VERCEL_CMD login || {
        err "Login failed. Please run 'vercel login' manually and try again."
        [[ "$CLEANUP_TEMP" == "true" ]] && rm -rf "$DEPLOY_DIR"
        exit 1
    }
    echo ""
    ok "Logged in to Vercel!"
fi

VERCEL_USER=$($VERCEL_CMD whoami 2>/dev/null || echo "unknown")
ok "Logged in as: $VERCEL_USER"

# ─── Deploy ───────────────────────────────────────────────

echo ""
info "Deploying visualization..."
echo ""

DECK_NAME=$(basename "$DEPLOY_DIR")
if [[ "$CLEANUP_TEMP" == "true" ]]; then
    DECK_NAME=$(basename "$INPUT" .html)
fi

DECK_NAME=$(echo "$DECK_NAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9._-]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//' | cut -c1-100)

if [[ "$CLEANUP_TEMP" == "true" ]]; then
    RENAMED_DIR="$(dirname "$DEPLOY_DIR")/$DECK_NAME"
    mv "$DEPLOY_DIR" "$RENAMED_DIR"
    DEPLOY_DIR="$RENAMED_DIR"
fi

DEPLOY_OUTPUT=$($VERCEL_CMD deploy "$DEPLOY_DIR" --yes --prod 2>&1) || {
    err "Deployment failed:"
    echo "$DEPLOY_OUTPUT"
    [[ "$CLEANUP_TEMP" == "true" ]] && rm -rf "$DEPLOY_DIR"
    exit 1
}

DEPLOY_URL=$(echo "$DEPLOY_OUTPUT" | grep -o 'https://[^ ]*' | tail -1)

# ─── Success ──────────────────────────────────────────────

echo ""
echo -e "${BOLD}════════════════════════════════════════════${NC}"
ok "Visualization deployed successfully!"
echo ""
echo -e "  ${BOLD}Live URL:${NC}  $DEPLOY_URL"
echo ""
echo "  Works on any device — phones, tablets, laptops."
echo "  Share it via Slack, email, or embed in docs."
echo ""
echo -e "  ${CYAN}Tip:${NC} To take it down, visit https://vercel.com/dashboard"
echo -e "       and delete the project '${DECK_NAME}'."
echo -e "${BOLD}════════════════════════════════════════════${NC}"
echo ""

if [[ "$CLEANUP_TEMP" == "true" ]]; then
    rm -rf "$DEPLOY_DIR"
fi
