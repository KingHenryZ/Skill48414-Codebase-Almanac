#!/usr/bin/env bash
# export-pdf.sh — Export a code visualization HTML to PDF
#
# Usage:
#   bash scripts/export-pdf.sh <path-to-html> [output.pdf] [--compact]
#
# Examples:
#   bash scripts/export-pdf.sh ./visualization.html
#   bash scripts/export-pdf.sh ./visualization.html ./output.pdf
#   bash scripts/export-pdf.sh ./visualization.html --compact
#
# Captures each tab view as a separate PDF page.
# Interactive features (search, tree expand) are not preserved.
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

# ─── Parse flags ──────────────────────────────────────────

VIEWPORT_W=1920
VIEWPORT_H=1200
COMPACT=false

POSITIONAL=()
for arg in "$@"; do
    case $arg in
        --compact)
            COMPACT=true
            VIEWPORT_W=1280
            VIEWPORT_H=800
            ;;
        *)
            POSITIONAL+=("$arg")
            ;;
    esac
done
set -- "${POSITIONAL[@]}"

# ─── Input validation ─────────────────────────────────────

if [[ $# -lt 1 ]]; then
    err "Usage: bash scripts/export-pdf.sh <path-to-html> [output.pdf] [--compact]"
    exit 1
fi

INPUT_HTML="$1"
if [[ ! -f "$INPUT_HTML" ]]; then
    err "File not found: $INPUT_HTML"
    exit 1
fi

INPUT_HTML=$(cd "$(dirname "$INPUT_HTML")" && pwd)/$(basename "$INPUT_HTML")

if [[ $# -ge 2 ]]; then
    OUTPUT_PDF="$2"
else
    OUTPUT_PDF="$(dirname "$INPUT_HTML")/$(basename "$INPUT_HTML" .html).pdf"
fi

OUTPUT_DIR=$(dirname "$OUTPUT_PDF")
mkdir -p "$OUTPUT_DIR"
OUTPUT_PDF="$OUTPUT_DIR/$(basename "$OUTPUT_PDF")"

echo ""
echo -e "${BOLD}╔══════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║    Export Code Visualization to PDF       ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════╝${NC}"
echo ""

# ─── Check dependencies ───────────────────────────────────

if ! command -v npx &>/dev/null; then
    err "Node.js is required but not installed."
    err "  macOS:   brew install node"
    err "  or visit https://nodejs.org"
    exit 1
fi

ok "Node.js found"

# ─── Create export script ─────────────────────────────────

TEMP_DIR=$(mktemp -d)
TEMP_SCRIPT="$TEMP_DIR/export-viz.mjs"
SERVE_DIR=$(dirname "$INPUT_HTML")
HTML_FILENAME=$(basename "$INPUT_HTML")

cat > "$TEMP_SCRIPT" << 'EXPORT_SCRIPT'
import { chromium } from 'playwright';
import { createServer } from 'http';
import { readFileSync, existsSync, mkdirSync, unlinkSync, writeFileSync } from 'fs';
import { join, extname } from 'path';

const SERVE_DIR = process.argv[2];
const HTML_FILE = process.argv[3];
const OUTPUT_PDF = process.argv[4];
const SCREENSHOT_DIR = process.argv[5];
const VP_WIDTH = parseInt(process.argv[6]) || 1920;
const VP_HEIGHT = parseInt(process.argv[7]) || 1200;

const MIME_TYPES = {
  '.html': 'text/html', '.css': 'text/css', '.js': 'application/javascript',
  '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg', '.svg': 'image/svg+xml', '.woff': 'font/woff',
  '.woff2': 'font/woff2', '.ttf': 'font/ttf',
};

const server = createServer((req, res) => {
  const decodedUrl = decodeURIComponent(req.url);
  let filePath = join(SERVE_DIR, decodedUrl === '/' ? HTML_FILE : decodedUrl);
  try {
    const content = readFileSync(filePath);
    const ext = extname(filePath).toLowerCase();
    res.writeHead(200, { 'Content-Type': MIME_TYPES[ext] || 'application/octet-stream' });
    res.end(content);
  } catch {
    res.writeHead(404);
    res.end('Not found');
  }
});

const port = await new Promise((resolve) => {
  server.listen(0, () => resolve(server.address().port));
});
console.log(`  Local server on port ${port}`);

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: VP_WIDTH, height: VP_HEIGHT } });

await page.goto(`http://localhost:${port}/`, { waitUntil: 'networkidle' });
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(2000);

// Discover available tabs
const tabs = await page.evaluate(() => {
  return Array.from(document.querySelectorAll('.tab-btn')).map(btn => ({
    id: btn.dataset.tab,
    label: btn.textContent.trim(),
  }));
});

console.log(`  Found ${tabs.length} tabs: ${tabs.map(t => t.label).join(', ')}`);

// Hide sidebar for cleaner screenshots
await page.evaluate(() => {
  const sidebar = document.querySelector('.sidebar');
  const toggle = document.querySelector('.sidebar-toggle');
  if (sidebar) sidebar.style.display = 'none';
  if (toggle) toggle.style.display = 'none';
  const main = document.querySelector('.main-content');
  if (main) main.style.marginLeft = '0';
});

mkdirSync(SCREENSHOT_DIR, { recursive: true });
const screenshotPaths = [];

for (let i = 0; i < tabs.length; i++) {
  const tab = tabs[i];

  // Switch to this tab
  await page.evaluate((tabId) => {
    if (typeof switchTab === 'function') {
      switchTab(tabId);
    } else {
      document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      const panel = document.getElementById(`panel-${tabId}`);
      const btn = document.querySelector(`[data-tab="${tabId}"]`);
      if (panel) panel.classList.add('active');
      if (btn) btn.classList.add('active');
    }
  }, tab.id);

  await page.waitForTimeout(800);

  // Wait for Mermaid diagrams to render
  await page.evaluate(() => {
    return new Promise(resolve => setTimeout(resolve, 500));
  });

  // Expand all tree nodes for the screenshot
  await page.evaluate(() => {
    document.querySelectorAll('.tree-children.collapsed').forEach(el => {
      el.classList.remove('collapsed');
    });
    document.querySelectorAll('.tree-toggle').forEach(el => {
      el.classList.add('open');
    });
  });

  const screenshotPath = join(SCREENSHOT_DIR, `tab-${String(i + 1).padStart(2, '0')}-${tab.id}.png`);

  // Get full page height for this tab
  const panelHeight = await page.evaluate((tabId) => {
    const panel = document.getElementById(`panel-${tabId}`);
    return panel ? panel.scrollHeight + 120 : 0;
  }, tab.id);

  // Set viewport to capture full content
  await page.setViewportSize({ width: VP_WIDTH, height: Math.max(VP_HEIGHT, panelHeight) });
  await page.waitForTimeout(300);

  await page.screenshot({ path: screenshotPath, fullPage: true });
  screenshotPaths.push(screenshotPath);
  console.log(`  Captured tab ${i + 1}/${tabs.length}: ${tab.label}`);
}

await browser.close();
server.close();

// Combine screenshots into PDF
console.log('  Assembling PDF...');

const browser2 = await chromium.launch();
const pdfPage = await browser2.newPage();

const imagesHtml = screenshotPaths.map((p) => {
  const imgData = readFileSync(p).toString('base64');
  return `<div class="page"><img src="data:image/png;base64,${imgData}" /></div>`;
}).join('\n');

const pdfHtml = `<!DOCTYPE html>
<html>
<head>
<style>
  * { margin: 0; padding: 0; }
  @page { size: ${VP_WIDTH}px auto; margin: 0; }
  .page {
    width: ${VP_WIDTH}px;
    page-break-after: always;
    overflow: hidden;
  }
  .page:last-child { page-break-after: auto; }
  img {
    width: ${VP_WIDTH}px;
    display: block;
  }
</style>
</head>
<body>${imagesHtml}</body>
</html>`;

await pdfPage.setContent(pdfHtml, { waitUntil: 'load' });
await pdfPage.pdf({
  path: OUTPUT_PDF,
  width: `${VP_WIDTH}px`,
  printBackground: true,
  margin: { top: 0, right: 0, bottom: 0, left: 0 },
});

await browser2.close();
screenshotPaths.forEach(p => unlinkSync(p));
console.log(`  PDF saved to: ${OUTPUT_PDF}`);
EXPORT_SCRIPT

# ─── Install Playwright ───────────────────────────────────

info "Setting up Playwright (headless browser for screenshots)..."
info "This may take a moment on first run..."
echo ""

cd "$TEMP_DIR"

cat > "$TEMP_DIR/package.json" << 'PKG'
{ "name": "viz-export", "private": true, "type": "module" }
PKG

npm install playwright &>/dev/null || {
    err "Failed to install Playwright."
    rm -rf "$TEMP_DIR"
    exit 1
}

npx playwright install chromium 2>/dev/null || {
    err "Failed to install Chromium. Try: npx playwright install chromium"
    rm -rf "$TEMP_DIR"
    exit 1
}
ok "Playwright ready"
echo ""

# ─── Run the export ───────────────────────────────────────

SCREENSHOT_DIR="$TEMP_DIR/screenshots"

info "Exporting visualization to PDF..."
echo ""

if [[ "$COMPACT" == "true" ]]; then
    info "Using compact mode (1280x800) for smaller file size"
fi

node "$TEMP_SCRIPT" "$SERVE_DIR" "$HTML_FILENAME" "$OUTPUT_PDF" "$SCREENSHOT_DIR" "$VIEWPORT_W" "$VIEWPORT_H" || {
    err "PDF export failed."
    rm -rf "$TEMP_DIR"
    exit 1
}

# ─── Cleanup and success ──────────────────────────────────

rm -rf "$TEMP_DIR"

echo ""
echo -e "${BOLD}════════════════════════════════════════════${NC}"
ok "PDF exported successfully!"
echo ""
echo -e "  ${BOLD}File:${NC}  $OUTPUT_PDF"
echo ""
FILE_SIZE=$(du -h "$OUTPUT_PDF" | cut -f1 | xargs)
echo "  Size: $FILE_SIZE"
echo ""
echo "  Each tab is captured as a separate page."
echo "  Mermaid diagrams are rendered as images."
echo "  Interactive features (search, tree) are not preserved."
echo -e "${BOLD}════════════════════════════════════════════${NC}"
echo ""

if command -v open &>/dev/null; then
    open "$OUTPUT_PDF"
elif command -v xdg-open &>/dev/null; then
    xdg-open "$OUTPUT_PDF"
fi
