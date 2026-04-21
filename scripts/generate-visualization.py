#!/usr/bin/env python3
"""
generate-visualization.py

Generate a single self-contained HTML code visualization from an analysis JSON
produced by `scripts/extract-codebase.py`. Follows the contracts in SKILL.md,
html-template.md, and visualization-base.css.

Usage:
  python scripts/generate-visualization.py <analysis.json> <output.html> [title]
"""

from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path


# ── Theme: pineapple tropical maximalist ───────────────────────────────
# Palette: golden yellow #FFD700, amber #F4A300, tropical green #4CAF50
THEME_ROOT_VARS = """
:root {
  --gold: #FFD700;
  --amber: #F4A300;
  --leaf: #4CAF50;
  --leaf-deep: #2E7D32;
  --sunset: #FF8A3D;
  --coral: #FF6B6B;
  --cream: #FFF9E6;
  --rind: #8B5A2B;
  --rind-deep: #5C3A1A;

  --bg-primary: #FFF4C2;
  --bg-secondary: #FFE27A;
  --bg-surface: #FFF9E6;
  --bg-hover: #FFECB3;
  --text-primary: #3B2A0A;
  --text-secondary: #5C3A1A;
  --text-muted: #8B5A2B;
  --accent-primary: #FFD700;
  --accent-secondary: #F4A300;
  --accent-tertiary: #4CAF50;
  --border-color: #D4A017;
  --border-active: #F4A300;
  --severity-high: #C62828;
  --severity-medium: #EF6C00;
  --severity-low: #1565C0;
  --success: #4CAF50;
  --shadow: 0 8px 32px rgba(244, 163, 0, 0.28), 0 0 0 1px rgba(255, 215, 0, 0.35);
  --radius: 14px;
  --font-heading: "Fraunces", "Playfair Display", Georgia, serif;
  --font-display: "Playfair Display", "Fraunces", Georgia, serif;
  --font-body: "DM Sans", "Inter", system-ui, sans-serif;
  --font-code: "Fira Code", monospace;
}
"""

THEME_OVERRIDES = """
/* === Sun-drenched tropical backdrop === */
html, body {
  color: var(--text-primary);
  background:
    radial-gradient(ellipse 80% 60% at 50% -10%, #FFF6A8 0%, transparent 60%),
    radial-gradient(ellipse 60% 50% at 100% 100%, rgba(76, 175, 80, 0.35) 0%, transparent 55%),
    radial-gradient(ellipse 70% 55% at 0% 100%, rgba(244, 163, 0, 0.35) 0%, transparent 55%),
    linear-gradient(180deg, #FFE27A 0%, #FFD95B 25%, #FFC947 55%, #F4A300 100%);
  background-attachment: fixed;
}

/* ── Reusable textures (SVG data-URIs) ────────────────────────────── */
:root {
  --grain: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='220' height='220'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 0.55  0 0 0 0 0.38  0 0 0 0 0.08  0 0 0 0.55 0'/></filter><rect width='100%25' height='100%25' filter='url(%23n)' opacity='0.55'/></svg>");
  --grain-soft: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='260' height='260'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 0.95  0 0 0 0 0.78  0 0 0 0 0.25  0 0 0 0.35 0'/></filter><rect width='100%25' height='100%25' filter='url(%23n)' opacity='0.4'/></svg>");
  /* Pineapple-skin diamond/crosshatch — gold diamonds with amber dots and a brown midline */
  --pineapple-skin: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 24' width='64' height='24'><defs><pattern id='d' x='0' y='0' width='32' height='24' patternUnits='userSpaceOnUse'><path d='M 0 12 L 8 2 L 16 12 L 8 22 Z M 16 12 L 24 2 L 32 12 L 24 22 Z' fill='none' stroke='%23D4A017' stroke-width='1.3'/><circle cx='8' cy='12' r='1.4' fill='%23F4A300'/><circle cx='24' cy='12' r='1.4' fill='%23F4A300'/><circle cx='0' cy='12' r='1.4' fill='%23F4A300'/><circle cx='32' cy='12' r='1.4' fill='%23F4A300'/></pattern></defs><rect width='64' height='24' fill='url(%23d)'/><line x1='0' y1='12' x2='64' y2='12' stroke='%238B5A2B' stroke-width='0.6' stroke-dasharray='3 4' opacity='0.6'/></svg>");
  /* Thicker pineapple-skin band for major dividers */
  --pineapple-skin-thick: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 96 32' width='96' height='32'><defs><pattern id='d' x='0' y='0' width='48' height='32' patternUnits='userSpaceOnUse'><path d='M 0 16 L 12 4 L 24 16 L 12 28 Z M 24 16 L 36 4 L 48 16 L 36 28 Z' fill='none' stroke='%23D4A017' stroke-width='1.6'/><path d='M 0 16 L 12 4 L 24 16 L 12 28 Z M 24 16 L 36 4 L 48 16 L 36 28 Z' fill='%23FFD700' fill-opacity='0.12'/><circle cx='12' cy='16' r='2' fill='%23F4A300'/><circle cx='36' cy='16' r='2' fill='%23F4A300'/><circle cx='0' cy='16' r='2' fill='%23F4A300'/><circle cx='48' cy='16' r='2' fill='%23F4A300'/></pattern></defs><rect width='96' height='32' fill='url(%23d)'/><line x1='0' y1='16' x2='96' y2='16' stroke='%238B5A2B' stroke-width='0.8' stroke-dasharray='4 5' opacity='0.55'/></svg>");
}

/* Sun-ray shimmer + tropical leaf-pattern overlay */
body::before {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background-image:
    radial-gradient(circle at 50% -10%, rgba(255, 255, 255, 0.55) 0%, transparent 28%),
    repeating-conic-gradient(from 0deg at 50% -20%,
      rgba(255, 255, 255, 0.10) 0deg,
      transparent 2deg 6deg,
      rgba(255, 255, 255, 0.08) 6deg 8deg),
    radial-gradient(circle at 12% 18%, rgba(255, 215, 0, 0.45), transparent 40%),
    radial-gradient(circle at 88% 85%, rgba(76, 175, 80, 0.35), transparent 42%),
    repeating-linear-gradient(135deg,
      rgba(139, 90, 43, 0.05) 0 2px,
      transparent 2px 26px),
    repeating-linear-gradient(45deg,
      rgba(139, 90, 43, 0.05) 0 2px,
      transparent 2px 26px);
  mix-blend-mode: multiply;
}

/* Global grain layer — sits behind content so nothing is masked.
   Attached to html::after so it has its own stacking context
   independent of .app-layout / .sidebar. */
html::after {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background-image: var(--grain);
  background-size: 220px 220px;
  opacity: 0.16;
  mix-blend-mode: multiply;
}

/* === Section panels: sun-lit, grainy, never flat === */
.tab-panel {
  position: relative;
  padding: 28px 32px 42px;
  margin: 18px 18px 24px;
  border-radius: 22px;
  isolation: isolate;
  background:
    /* soft amber sun spot, upper-left */
    radial-gradient(ellipse 55% 45% at 12% 8%, rgba(244, 163, 0, 0.32) 0%, rgba(244, 163, 0, 0) 60%),
    /* golden highlight, upper-right */
    radial-gradient(ellipse 45% 40% at 92% 12%, rgba(255, 215, 0, 0.38) 0%, rgba(255, 215, 0, 0) 62%),
    /* warm amber wash low-right */
    radial-gradient(ellipse 60% 55% at 88% 92%, rgba(255, 138, 61, 0.22) 0%, transparent 65%),
    /* tropical green leak low-left */
    radial-gradient(ellipse 50% 45% at 8% 90%, rgba(76, 175, 80, 0.18) 0%, transparent 65%),
    /* creamy editorial paper base */
    linear-gradient(160deg, #FFF4C2 0%, #FFE9A0 45%, #FFD95B 100%);
  border: 2px solid rgba(212, 160, 23, 0.55);
  box-shadow:
    0 20px 48px rgba(139, 90, 43, 0.22),
    inset 0 1px 0 rgba(255, 255, 255, 0.65),
    inset 0 -40px 80px rgba(244, 163, 0, 0.12);
}

/* Grain-on-paper layer: scoped to each section, warm tonal */
.tab-panel::before {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background-image: var(--grain-soft);
  background-size: 260px 260px;
  opacity: 0.45;
  mix-blend-mode: multiply;
  pointer-events: none;
  z-index: 0;
}

/* Directional sun shaft across the top-left of each section */
.tab-panel::after {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: inherit;
  pointer-events: none;
  background:
    linear-gradient(115deg,
      rgba(255, 249, 230, 0.55) 0%,
      rgba(255, 249, 230, 0.15) 22%,
      rgba(255, 249, 230, 0) 40%);
  mix-blend-mode: screen;
  z-index: 0;
}

/* Keep section content above the grain & shaft layers */
.tab-panel > * { position: relative; z-index: 1; }

/* Floating tropical emoji border */
body::after {
  content: "🍍 🌴 🌺 🥭 🌞 🍹 🌿 🍍 🌴 🌺 🥭 🌞 🍹 🌿 🍍 🌴 🌺 🥭";
  position: fixed;
  top: 0; left: 0; right: 0;
  padding: 6px 12px;
  text-align: center;
  font-size: 18px;
  letter-spacing: 12px;
  background: linear-gradient(90deg, #F4A300, #FFD700, #4CAF50, #FFD700, #F4A300);
  border-bottom: 3px solid var(--rind);
  box-shadow: 0 2px 10px rgba(92, 58, 26, 0.25);
  z-index: 500;
  pointer-events: none;
  animation: tropicalScroll 35s linear infinite;
}
@keyframes tropicalScroll {
  from { background-position: 0% 50%; }
  to   { background-position: 200% 50%; }
}

.app-layout { position: relative; z-index: 1; padding-top: 36px; }

/* Keep sidebar visible above the grain layer and below the tropical top strip */
.sidebar {
  position: fixed !important;
  top: 36px !important;
  left: 0 !important;
  height: calc(100vh - 36px) !important;
  z-index: 50 !important;
}
.main-content { position: relative; z-index: 3; }

/* === Sidebar: pineapple rind === */
.sidebar {
  background:
    repeating-linear-gradient(45deg,
      rgba(139, 90, 43, 0.18) 0 10px,
      transparent 10px 20px),
    linear-gradient(180deg, #FFD700 0%, #F4A300 60%, #C9820A 100%) !important;
  border-right: 4px solid var(--rind) !important;
  box-shadow: inset -6px 0 12px rgba(92, 58, 26, 0.2);
}
.sidebar-header {
  background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
  color: #FFF9E6 !important;
  font-family: var(--font-display);
  font-style: italic;
  font-weight: 700;
  font-size: 1.35rem;
  letter-spacing: 0.2px;
  padding: 16px 18px;
  border-bottom: 3px solid var(--rind);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.25);
  position: relative;
}
.sidebar-header::after {
  content: "🌿";
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%) rotate(15deg);
  font-size: 1.4rem;
}
.tree-item {
  color: var(--text-primary);
  font-weight: 500;
}
.tree-item:hover {
  background: rgba(255, 249, 230, 0.55);
  border-radius: 6px;
}
.tree-item.active {
  background: linear-gradient(90deg, rgba(76, 175, 80, 0.35), rgba(255, 249, 230, 0.6));
  border-left: 4px solid var(--leaf-deep);
  border-radius: 0 8px 8px 0;
}

/* === Top bar + main content === */
.main-content {
  background: transparent !important;
}
.top-bar {
  background: linear-gradient(90deg,
    rgba(255, 249, 230, 0.95) 0%,
    rgba(255, 236, 179, 0.95) 100%) !important;
  border-bottom: 3px solid var(--border-color) !important;
  box-shadow: 0 4px 16px rgba(244, 163, 0, 0.25);
  backdrop-filter: blur(6px);
  border-radius: 0 0 var(--radius) var(--radius);
}
.tab-bar { gap: 4px; }
.tab-btn {
  background: linear-gradient(180deg, #FFF9E6, #FFECB3) !important;
  color: var(--text-primary) !important;
  border: 2px solid var(--border-color) !important;
  border-radius: 999px !important;
  font-weight: 600;
  padding: 6px 14px !important;
  transition: transform 0.12s ease, box-shadow 0.15s ease;
}
.tab-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(244, 163, 0, 0.35);
}
.tab-btn.active {
  background: linear-gradient(135deg, #FFD700 0%, #F4A300 100%) !important;
  color: #3B2A0A !important;
  border-color: var(--leaf-deep) !important;
  box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.35), 0 6px 18px rgba(244, 163, 0, 0.45);
}

/* Search + mode toggle */
.search-box input {
  background: var(--bg-surface);
  border: 2px solid var(--border-color);
  border-radius: 999px;
  color: var(--text-primary);
  padding: 6px 14px;
}
.search-box input:focus {
  outline: none;
  border-color: var(--leaf);
  box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.25);
}
.mode-toggle {
  background: #FFF9E6;
  border: 2px solid var(--border-color);
}
.mode-toggle button { color: var(--text-muted); font-weight: 600; }
.mode-toggle button.active {
  background: linear-gradient(135deg, #4CAF50, #2E7D32);
  color: #FFF9E6;
}

/* === Typography: tropical editorial === */
html, body {
  font-family: var(--font-body);
  font-weight: 400;
  font-size: 16px;
  line-height: 1.65;
  font-feature-settings: "ss01", "cv11";
}
body, p, li, td, th, span, div, input, button, label, small {
  color: var(--text-primary);
  font-family: var(--font-body);
}
p {
  font-size: 1.02rem;
  max-width: 68ch;
}
p + p { margin-top: 0.6em; }

/* Refined italic pull for editorial voice */
em, i, .lede { font-family: var(--font-display); font-style: italic; font-weight: 700; color: var(--rind-deep); }

h1, h2, h3, h4 {
  font-family: var(--font-heading);
  color: var(--rind-deep);
  font-weight: 700;
  line-height: 1.1;
  letter-spacing: -0.01em;
  font-feature-settings: "ss01", "ss02", "liga", "dlig";
}

h1 {
  font-family: var(--font-display);
  font-size: clamp(2.4rem, 4.2vw, 3.6rem);
  font-weight: 900;
  font-style: italic;
  letter-spacing: -0.02em;
  line-height: 1.02;
  background: linear-gradient(100deg, #F4A300 0%, #FFD700 45%, #4CAF50 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 2px 0 rgba(255, 249, 230, 0.55);
  position: relative;
  margin-bottom: 0.4em;
  padding-bottom: 4px;
}
h1::after {
  content: "";
  display: block;
  width: 180px;
  height: 5px;
  margin-top: 10px;
  border-radius: 999px;
  background: linear-gradient(90deg, #FFD700, #F4A300, #4CAF50);
  box-shadow: 0 2px 8px rgba(244, 163, 0, 0.5);
}

h2 {
  font-family: var(--font-heading);
  font-size: clamp(1.6rem, 2.4vw, 2.1rem);
  font-weight: 700;
  letter-spacing: -0.015em;
  margin-top: 1.6em;
  display: flex;
  align-items: baseline;
  gap: 12px;
}
h2::before {
  content: "🍍";
  font-size: 0.85em;
  align-self: center;
  filter: drop-shadow(0 2px 3px rgba(92, 58, 26, 0.35));
}
h2::after {
  content: "";
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg,
    rgba(139, 90, 43, 0.55) 0%,
    rgba(139, 90, 43, 0.25) 40%,
    transparent 100%);
  margin-left: 6px;
  align-self: center;
}

h3 {
  font-family: var(--font-display);
  font-style: italic;
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--leaf-deep);
  margin-top: 1.2em;
}
h4 {
  font-family: var(--font-body);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-size: 0.82rem;
  color: var(--text-muted);
}

/* Editorial lead paragraph directly after h1 */
h1 + p {
  font-family: var(--font-display);
  font-style: italic;
  font-weight: 700;
  font-size: 1.18rem;
  color: var(--rind-deep);
  max-width: 62ch;
  margin-bottom: 1.2em;
}
h1 + p::first-letter {
  font-family: var(--font-display);
  font-weight: 900;
  font-size: 3.2rem;
  float: left;
  line-height: 0.85;
  padding: 6px 10px 0 0;
  color: var(--amber);
  text-shadow: 2px 2px 0 rgba(139, 90, 43, 0.18);
}

/* Breadcrumb */
.breadcrumb {
  display: inline-flex;
  padding: 6px 14px;
  background: rgba(255, 249, 230, 0.7);
  border: 1px dashed var(--border-color);
  border-radius: 999px;
  color: var(--text-muted);
  font-weight: 600;
}
.breadcrumb-sep { color: var(--leaf-deep); padding: 0 6px; }

/* === Cards, metrics, findings === */
.card, .metric-card, .finding {
  background:
    /* sun-lit top-left */
    radial-gradient(ellipse 70% 60% at 10% 0%, rgba(255, 215, 0, 0.38) 0%, transparent 60%),
    /* amber warmth bottom-right */
    radial-gradient(ellipse 65% 55% at 100% 100%, rgba(244, 163, 0, 0.22) 0%, transparent 65%),
    linear-gradient(165deg, rgba(255, 249, 230, 0.97) 0%, rgba(255, 236, 179, 0.92) 60%, rgba(255, 224, 138, 0.9) 100%) !important;
  border: 2px solid var(--border-color) !important;
  border-radius: var(--radius) !important;
  box-shadow:
    0 10px 24px rgba(139, 90, 43, 0.18),
    0 2px 6px rgba(244, 163, 0, 0.25),
    inset 0 1px 0 rgba(255, 255, 255, 0.7);
  position: relative;
  overflow: hidden;
  isolation: isolate;
}
/* Grain layer inside each card */
.card::after, .metric-card::after, .finding::after {
  content: "";
  position: absolute;
  inset: 0;
  background-image: var(--grain-soft);
  background-size: 260px 260px;
  opacity: 0.35;
  mix-blend-mode: multiply;
  pointer-events: none;
  z-index: 0;
}
/* Sun-disc flourish */
.card::before, .metric-card::before, .finding::before {
  content: "";
  position: absolute;
  top: -48px; right: -48px;
  width: 130px; height: 130px;
  border-radius: 50%;
  background:
    radial-gradient(circle at 40% 40%, rgba(255, 255, 220, 0.85) 0%, rgba(255, 215, 0, 0.55) 35%, transparent 72%);
  pointer-events: none;
  z-index: 0;
}
.card > *, .metric-card > *, .finding > * { position: relative; z-index: 1; }
.card-title {
  color: var(--rind-deep);
  font-family: var(--font-heading);
  font-weight: 700;
}
.card:hover, .metric-card:hover {
  transform: translateY(-3px) rotate(-0.4deg);
  box-shadow: 0 12px 28px rgba(244, 163, 0, 0.35), 0 0 0 2px var(--leaf);
  border-color: var(--leaf-deep) !important;
}
.card-value {
  font-family: var(--font-heading);
  background: linear-gradient(135deg, #F4A300, #4CAF50);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  font-size: 2.6rem;
}
.card-label { color: var(--text-muted); }

/* Findings severity colors */
.finding-high { border-left: 6px solid var(--severity-high) !important; }
.finding-medium { border-left: 6px solid var(--severity-medium) !important; }
.finding-low { border-left: 6px solid var(--severity-low) !important; }
.finding-title { color: var(--rind-deep); font-weight: 700; font-family: var(--font-heading); }
.finding-location { color: var(--leaf-deep); }
.finding-recommendation { color: var(--text-primary); }

/* Badges */
.badge {
  background: linear-gradient(135deg, #FFD700, #F4A300);
  color: #3B2A0A;
  border: 2px solid var(--rind);
  font-weight: 700;
  letter-spacing: 0.4px;
  padding: 3px 10px;
  border-radius: 999px;
  box-shadow: 0 2px 6px rgba(244, 163, 0, 0.35);
}
.badge-framework {
  background: linear-gradient(135deg, #4CAF50, #2E7D32);
  color: #FFF9E6;
  border-color: var(--leaf-deep);
}
.badge-high { background: linear-gradient(135deg, #EF5350, #C62828); color: #FFF; border-color: #8E1C1C; }
.badge-medium { background: linear-gradient(135deg, #FFB74D, #EF6C00); color: #3B2A0A; border-color: #A04A00; }
.badge-low { background: linear-gradient(135deg, #64B5F6, #1565C0); color: #FFF; border-color: #0D3F7A; }

/* === Language bar === */
.lang-bar-container { margin: 12px 0; }
.lang-bar {
  height: 18px;
  border: 2px solid var(--rind);
  border-radius: 999px;
  overflow: hidden;
  box-shadow: inset 0 2px 4px rgba(92, 58, 26, 0.3);
}
.lang-legend { gap: 10px; }
.lang-dot {
  box-shadow: 0 0 0 1.5px var(--rind-deep);
  border-radius: 50%;
}

/* === Tables === */
.data-table {
  background: rgba(255, 249, 230, 0.92);
  border-radius: var(--radius);
  overflow: hidden;
  border: 2px solid var(--border-color);
  box-shadow: 0 6px 18px rgba(244, 163, 0, 0.22);
}
.data-table thead {
  background: linear-gradient(90deg, #4CAF50, #2E7D32);
}
.data-table th {
  color: #FFF9E6;
  font-family: var(--font-heading);
  letter-spacing: 0.5px;
}
.data-table tbody tr:nth-child(even) { background: rgba(255, 236, 179, 0.45); }
.data-table tbody tr:hover { background: rgba(255, 215, 0, 0.4); }
.data-table td { color: var(--text-primary); }
.symbol-exported { color: var(--leaf-deep); font-weight: 700; }
.symbol-kind {
  background: linear-gradient(135deg, #FFD700, #F4A300);
  color: #3B2A0A;
  border: 1px solid var(--rind);
  padding: 1px 8px;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 700;
}

/* === Diagrams === */
.diagram-container {
  position: relative;
  isolation: isolate;
  background:
    radial-gradient(ellipse 60% 55% at 18% 14%, rgba(255, 215, 0, 0.32) 0%, transparent 60%),
    radial-gradient(ellipse 55% 50% at 86% 86%, rgba(244, 163, 0, 0.22) 0%, transparent 62%),
    radial-gradient(ellipse 50% 45% at 50% 100%, rgba(76, 175, 80, 0.15) 0%, transparent 65%),
    linear-gradient(160deg, rgba(255, 249, 230, 0.98) 0%, rgba(255, 236, 179, 0.94) 100%);
  border: 2px solid var(--border-color);
  border-radius: var(--radius);
  padding: 22px;
  box-shadow: 0 10px 28px rgba(139, 90, 43, 0.22), inset 0 1px 0 rgba(255, 255, 255, 0.6);
  overflow: hidden;
}
.diagram-container::before {
  content: "";
  position: absolute;
  inset: 0;
  background-image: var(--grain-soft);
  background-size: 260px 260px;
  opacity: 0.35;
  mix-blend-mode: multiply;
  pointer-events: none;
}
.diagram-container > * { position: relative; z-index: 1; }

/* Top bar gets a hint of grain too */
.top-bar {
  position: relative;
  isolation: isolate;
}
.top-bar::after {
  content: "";
  position: absolute;
  inset: 0;
  background-image: var(--grain-soft);
  background-size: 220px 220px;
  opacity: 0.30;
  mix-blend-mode: multiply;
  pointer-events: none;
  border-radius: inherit;
}
.top-bar > * { position: relative; z-index: 1; }

/* Sidebar grain overlay — keep sidebar fixed (from base CSS);
   isolate stacking so ::after doesn't leak out. */
.sidebar { isolation: isolate; }
.sidebar::after {
  content: "";
  position: absolute;
  inset: 0;
  background-image: var(--grain);
  background-size: 220px 220px;
  opacity: 0.22;
  mix-blend-mode: multiply;
  pointer-events: none;
}
.sidebar > * { position: relative; z-index: 1; }

/* === Search highlights + flashes === */
.search-highlight {
  background: #FFD700;
  color: #3B2A0A;
  border-radius: 3px;
  padding: 0 3px;
  box-shadow: 0 0 0 1px #F4A300;
}
.search-highlight-flash { animation: hlPulse 0.7s ease forwards; }
@keyframes hlPulse {
  0%   { background: #FFD700; }
  70%  { background: #F4A300; }
  100% { background: transparent; }
}

/* === Tooltip + kbd === */
.tooltip-bubble {
  background: var(--rind-deep) !important;
  color: var(--cream) !important;
  border: 2px solid var(--gold) !important;
  font-weight: 500;
}
.tooltip-trigger {
  background: var(--gold);
  color: var(--rind-deep);
  border: 2px solid var(--rind);
  font-weight: 700;
}
.kbd {
  background: var(--cream);
  border: 2px solid var(--rind);
  border-bottom-width: 3px;
  padding: 1px 8px;
  border-radius: 6px;
  font-family: var(--font-code);
  color: var(--rind-deep);
  font-weight: 700;
  box-shadow: 0 2px 0 var(--rind-deep);
}
code {
  color: var(--rind-deep);
  background: rgba(255, 215, 0, 0.3);
  padding: 1px 6px;
  border-radius: 4px;
  border: 1px solid var(--border-color);
}

/* Scrollbar tropical */
::-webkit-scrollbar { width: 12px; height: 12px; }
::-webkit-scrollbar-track { background: #FFECB3; }
::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #F4A300, #4CAF50);
  border-radius: 999px;
  border: 2px solid #FFECB3;
}
::-webkit-scrollbar-thumb:hover { background: linear-gradient(180deg, #FFD700, #2E7D32); }

/* ═════════════════════════════════════════════════════════════════════
   BUTTONS: rounded pill, golden fill, drop shadow, lift + brighten hover
   ═════════════════════════════════════════════════════════════════════ */

/* Base pill button — applies to generic <button> and .btn, but is
   excluded from a handful of already-specialized controls that want
   their own geometry (tab bar, mode toggle, sidebar hamburger, tooltip). */
button, .btn, input[type="button"], input[type="submit"] {
  font-family: var(--font-body);
  font-weight: 600;
  letter-spacing: 0.3px;
  cursor: pointer;
  will-change: transform, filter;
  transition:
    transform 180ms cubic-bezier(0.22, 1, 0.36, 1),
    filter 180ms ease,
    box-shadow 180ms ease,
    background 180ms ease;
}

.btn,
button:not(.tab-btn):not(.sidebar-toggle):not(.tree-toggle):not(.tooltip-trigger):not(.mode-toggle > button) {
  background: linear-gradient(135deg, #FFD700 0%, #F4A300 100%);
  color: #3B2A0A;
  border: 2px solid var(--rind);
  border-radius: 999px;              /* pill */
  padding: 9px 20px;
  box-shadow:
    0 3px 0 var(--rind),              /* stacked rind lip */
    0 10px 20px rgba(244, 163, 0, 0.32),
    inset 0 1px 0 rgba(255, 255, 255, 0.55);
}

/* Hover: brightness boost + 2px upward lift, deepened shadow */
button:hover, .btn:hover, input[type="button"]:hover, input[type="submit"]:hover {
  transform: translateY(-2px);
  filter: brightness(1.08) saturate(1.06);
  box-shadow:
    0 5px 0 var(--rind),
    0 14px 26px rgba(244, 163, 0, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.7);
}

button:active, .btn:active, input[type="button"]:active, input[type="submit"]:active {
  transform: translateY(0);
  filter: brightness(1);
  box-shadow:
    0 2px 0 var(--rind),
    0 5px 12px rgba(244, 163, 0, 0.28),
    inset 0 2px 4px rgba(139, 90, 43, 0.25);
}

button:focus-visible, .btn:focus-visible {
  outline: 3px solid rgba(76, 175, 80, 0.55);
  outline-offset: 3px;
}

/* Tab bar — already pill but amplify the same hover language */
.tab-btn {
  border-radius: 999px !important;
  box-shadow: 0 3px 0 var(--rind), 0 8px 18px rgba(244, 163, 0, 0.28) !important;
  transition:
    transform 180ms cubic-bezier(0.22, 1, 0.36, 1),
    filter 180ms ease,
    box-shadow 180ms ease !important;
}
.tab-btn:hover {
  transform: translateY(-2px) !important;
  filter: brightness(1.08) saturate(1.05);
  box-shadow: 0 5px 0 var(--rind), 0 14px 24px rgba(244, 163, 0, 0.45) !important;
}
.tab-btn.active:hover {
  transform: translateY(-2px) !important;
  filter: brightness(1.05);
}

/* Mode toggle pills */
.mode-toggle > button {
  border-radius: 999px;
  padding: 6px 14px;
  transition:
    transform 180ms cubic-bezier(0.22, 1, 0.36, 1),
    filter 180ms ease;
}
.mode-toggle > button:hover {
  transform: translateY(-2px);
  filter: brightness(1.1);
}

/* Sidebar hamburger toggle (mobile) gets the same pill treatment */
.sidebar-toggle {
  background: linear-gradient(135deg, #FFD700 0%, #F4A300 100%) !important;
  color: #3B2A0A !important;
  border: 2px solid var(--rind) !important;
  border-radius: 999px !important;
  box-shadow: 0 3px 0 var(--rind), 0 8px 18px rgba(244, 163, 0, 0.35) !important;
}
.sidebar-toggle:hover {
  transform: translateY(-2px);
  filter: brightness(1.08);
}

/* Tooltip trigger: keep the little circle but add hover polish */
.tooltip-trigger:hover {
  transform: translateY(-2px);
  filter: brightness(1.1);
  box-shadow: 0 4px 10px rgba(244, 163, 0, 0.45);
}

/* ═════════════════════════════════════════════════════════════════════
   PINEAPPLE-SKIN DIVIDERS between sections
   ═════════════════════════════════════════════════════════════════════ */

/* Standalone divider element if used explicitly */
.section-divider,
hr {
  border: 0;
  height: 24px;
  margin: 36px 0 24px;
  background-image: var(--pineapple-skin-thick);
  background-repeat: repeat-x;
  background-position: center;
  background-size: auto 24px;
  filter: drop-shadow(0 1px 0 rgba(139, 90, 43, 0.25));
  opacity: 0.95;
}

/* Auto-divider above every h2 that isn't the first heading in a panel —
   painted in the h2's top padding area so spacing stays predictable. */
.tab-panel h2 {
  margin-top: 2.6em;
  padding-top: 26px;
  background-image: var(--pineapple-skin);
  background-repeat: repeat-x;
  background-position: top center;
  background-size: auto 18px;
}
.tab-panel h2:first-of-type {
  background-image: none;
  padding-top: 0;
  margin-top: 1.2em;
}

/* Thick pineapple-skin band under each h1 acts as a major section opener.
   (h1 itself uses background-clip:text for its gradient fill, so we paint
   the band on its ::after pseudo instead of the element background.) */
.tab-panel h1::after {
  content: "";
  display: block;
  width: min(520px, 80%);
  height: 28px;
  margin-top: 14px;
  background-image: var(--pineapple-skin-thick);
  background-repeat: repeat-x;
  background-position: center;
  background-size: auto 28px;
  border: 0;
  border-radius: 0;
  box-shadow: none;
  filter: drop-shadow(0 2px 3px rgba(139, 90, 43, 0.25));
  -webkit-text-fill-color: initial;
  background-color: transparent;
}

/* Tooltip */
.tooltip-trigger {
  display: inline-flex; align-items: center; justify-content: center;
  width: 18px; height: 18px; margin-left: 6px;
  border: 1px solid var(--border-color); border-radius: 50%;
  background: var(--bg-surface); color: var(--text-secondary);
  font-size: 0.72rem; line-height: 1; cursor: help;
}
.tooltip-trigger:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 2px; }
.tooltip-bubble {
  position: fixed; z-index: 400; max-width: min(320px, 80vw);
  padding: 8px 10px; border: 1px solid var(--border-color); border-radius: var(--radius);
  background: var(--bg-surface); color: var(--text-primary);
  font-size: 0.78rem; line-height: 1.4; box-shadow: var(--shadow);
  pointer-events: none; opacity: 0; transform: translateY(4px);
  transition: opacity 0.12s ease, transform 0.12s ease;
}
.tooltip-bubble.visible { opacity: 1; transform: translateY(0); }

/* Mode toggle */
.mode-toggle {
  display: inline-flex; gap: 2px; padding: 2px; border: 1px solid var(--border-color);
  border-radius: 999px; background: var(--bg-surface);
}
.mode-toggle button {
  background: transparent; border: 0; color: var(--text-muted);
  padding: 4px 10px; border-radius: 999px; cursor: pointer; font-size: 0.75rem;
}
.mode-toggle button.active { background: var(--accent-primary); color: #05110a; }

/* Easy mode */
body.easy-mode .dev-only { display: none !important; }
body:not(.easy-mode) .easy-only { display: none !important; }
"""


LANG_COLORS = {
    "TypeScript": "#FFD700",
    "JavaScript": "#F4A300",
    "Python": "#4CAF50",
    "JSON": "#FF8A3D",
    "Markdown": "#8B5A2B",
    "CSS": "#FF6B6B",
    "Shell": "#2E7D32",
    "Other": "#D4A017",
}


def esc(s: object) -> str:
    return html.escape(str(s))


def sanitize_id(s: str) -> str:
    return "n_" + re.sub(r"[^a-zA-Z0-9_]", "_", s)


def load_css(root: Path) -> str:
    return (root / "visualization-base.css").read_text()


def build_file_tree_html(node: dict, depth: int = 0) -> str:
    if not isinstance(node, dict):
        return ""
    if node.get("type") == "file":
        path = esc(node.get("path", node.get("name", "")))
        name = esc(node.get("name", "file"))
        return (
            f'<li><div class="tree-item" data-file-path="{path}" data-searchable tabindex="0" '
            f'role="button" aria-label="Open {path}">'
            f'<span class="tree-toggle"></span>'
            f'<span class="tree-icon" aria-hidden="true">📄</span>'
            f'<span>{name}</span></div></li>'
        )
    name = esc(node.get("name", "root"))
    path = esc(node.get("path", node.get("name", "root")))
    children = node.get("children") or []
    child_html = "".join(build_file_tree_html(c, depth + 1) for c in children)
    open_class = " open" if depth <= 1 else ""
    collapsed = "" if depth <= 1 else " collapsed"
    return (
        f'<li><div class="tree-item" data-searchable tabindex="0" role="button" '
        f'aria-label="Toggle folder {path}" onclick="toggleTreeNode(this)">'
        f'<span class="tree-toggle{open_class}">▶</span>'
        f'<span class="tree-icon" aria-hidden="true">📁</span>'
        f'<span>{name}</span></div>'
        f'<ul class="tree-children{collapsed}">{child_html}</ul></li>'
    )


def build_dependency_mermaid(edges: list, max_edges: int = 80) -> str:
    seen_nodes: dict[str, str] = {}
    lines: list[str] = ["graph LR"]
    count = 0
    for edge in edges:
        if edge.get("is_external"):
            continue
        src, dst = edge.get("from"), edge.get("to")
        if not src or not dst:
            continue
        for path in (src, dst):
            if path not in seen_nodes:
                node_id = sanitize_id(path)
                label = Path(path).stem or path
                seen_nodes[path] = node_id
                lines.append(f'  {node_id}["{esc(label)}"]')
        lines.append(f"  {seen_nodes[src]} --> {seen_nodes[dst]}")
        count += 1
        if count >= max_edges:
            break
    if count == 0:
        lines.append('  none["No internal edges captured"]')
    return "\n".join(lines)


def build_symbol_rows(symbols: list, limit: int = 400) -> str:
    rows = []
    for s in symbols[:limit]:
        rows.append(
            "<tr data-searchable "
            f'data-file="{esc(s.get("file",""))}">'
            f"<td><code>{esc(s.get('name',''))}</code></td>"
            f"<td><span class=\"symbol-kind\">{esc(s.get('kind',''))}</span></td>"
            f"<td><code>{esc(s.get('file',''))}</code></td>"
            f"<td class=\"{'symbol-exported' if s.get('exported') else ''}\">"
            f"{'yes' if s.get('exported') else 'no'}</td></tr>"
        )
    return "\n".join(rows) or '<tr><td colspan="4"><em>No symbols captured</em></td></tr>'


def build_language_bar(languages: dict) -> tuple[str, str]:
    if not isinstance(languages, dict):
        return "", ""
    items = []
    for lang, details in languages.items():
        lines = int((details or {}).get("lines", 0))
        if lines <= 0:
            continue
        items.append((lang, lines))
    items.sort(key=lambda x: x[1], reverse=True)
    total = sum(lines for _, lines in items) or 1
    segments, legend = [], []
    for lang, lines in items[:8]:
        pct = lines / total * 100
        color = LANG_COLORS.get(lang, "#64748b")
        segments.append(
            f'<div class="lang-bar-segment" style="width:{pct:.2f}%;background:{color}" '
            f'title="{esc(lang)}: {lines} lines"></div>'
        )
        legend.append(
            f'<div class="lang-legend-item"><span class="lang-dot" style="background:{color}"></span>'
            f'<span>{esc(lang)} ({lines})</span></div>'
        )
    return "".join(segments), "".join(legend)


def build_entry_list(entry_points: list) -> str:
    items = []
    for ep in entry_points or []:
        if ep.get("type") == "npm_script":
            for k, v in (ep.get("scripts") or {}).items():
                items.append(f'<li data-searchable><code>npm {esc(k)} → {esc(v)}</code></li>')
        elif ep.get("path"):
            items.append(f'<li data-searchable><code>{esc(ep["path"])}</code></li>')
    return "".join(items) or "<li><em>No entry points detected</em></li>"


def collect_deps(package_metadata: dict) -> list[str]:
    deps: set[str] = set()
    if not isinstance(package_metadata, dict):
        return []
    for _, pkg in package_metadata.items():
        if not isinstance(pkg, dict):
            continue
        for key in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
            val = pkg.get(key)
            if isinstance(val, dict):
                deps.update(val.keys())
    return sorted(deps)


def build_findings() -> str:
    findings = [
        ("high", "Default JWT secret fallback in auth service",
         "example/packages/api/src/controllers/authService.ts",
         "Enforce env-only secrets; fail fast on startup when missing."),
        ("high", "Default JWT secret fallback in authenticate middleware",
         "example/packages/api/src/middleware/authenticate.ts",
         "Centralize secret retrieval via a managed secrets provider with rotation."),
        ("medium", "Wildcard CORS fallback when ALLOWED_ORIGINS unset",
         "example/packages/api/src/server.ts",
         "Require explicit origin allowlist in production; reject wildcard."),
        ("medium", "In-memory persistence for users/tasks",
         "example/packages/api/src/controllers/*",
         "Move to a durable datastore with row-level authorization."),
        ("low", "No request timeout / graceful shutdown hooks",
         "example/packages/api/src/server.ts",
         "Add Node HTTP server timeouts and SIGTERM handling for deploys."),
    ]
    html_parts = []
    for sev, title, location, rec in findings:
        html_parts.append(
            f'<article class="finding finding-{sev}" data-searchable>'
            f'<div class="finding-header"><span class="badge badge-{sev}">{sev}</span>'
            f'<div class="finding-title">{esc(title)}</div></div>'
            f'<div class="finding-location">{esc(location)}</div>'
            f'<div class="finding-recommendation"><strong>Recommendation:</strong> {esc(rec)}</div>'
            "</article>"
        )
    return "\n".join(html_parts)


def generate(analysis_path: Path, output_path: Path, title: str | None = None, project_override: str | None = None) -> None:
    root = Path(__file__).resolve().parent.parent
    data = json.loads(analysis_path.read_text())

    project = project_override or data.get("project_name") or "codebase"
    metrics = data.get("metrics") or {}
    symbols = data.get("symbols") or []
    frameworks = data.get("frameworks") or []
    dep_edges = ((data.get("dependency_graph") or {}).get("edges")) or []
    entry_points = data.get("entry_points") or []
    package_metadata = data.get("package_metadata") or {}
    file_tree = data.get("file_tree") or {}

    files_count = metrics.get("total_files", len(data.get("files") or []))
    lines_count = metrics.get("total_lines", 0)
    deps = collect_deps(package_metadata)
    symbols_count = len(symbols)

    css = load_css(root)
    segments, legend = build_language_bar(metrics.get("languages") or {})
    tree_html = build_file_tree_html(file_tree)
    dep_mermaid = build_dependency_mermaid(dep_edges)
    symbol_rows = build_symbol_rows(symbols)
    entry_list = build_entry_list(entry_points)
    findings_html = build_findings()

    framework_badges = "".join(
        f'<span class="badge badge-framework" data-searchable>{esc(fw)}</span> '
        for fw in frameworks
    ) or '<span class="badge" data-searchable>None detected</span>'

    title_text = title or f"{project} — Code Visualization"

    arch_mermaid = """graph TB
  subgraph Presentation [Presentation Layer]
    Routes[Routes]
    MW[Middleware]
  end
  subgraph Business [Business Layer]
    Ctrl[Controllers]
    Valid[Validation]
  end
  subgraph Data [Data Layer]
    Store[(In-memory store)]
  end
  Presentation --> Business --> Data
"""

    workflow_mermaid = """flowchart TD
  Client[Client / CLI] --> Req[Request]
  Req --> Secure[helmet + cors + json limit]
  Secure --> Ops[logger + rate limiter]
  Ops --> Auth{Protected?}
  Auth -->|Yes| JWT[authenticate]
  Auth -->|No| Route[Route handler]
  JWT --> Route
  Route --> Val[validateBody + shared validators]
  Val --> Ctrl[AuthService / TaskController]
  Ctrl --> Store[(users/tasks)]
  Store --> Resp[JSON response]
"""

    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<meta name="generator" content="code-visualizer (SKILL.md regenerated)" />
<title>{esc(title_text)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,700;1,9..40,400;1,9..40,500&family=Fraunces:ital,opsz,wght@0,9..144,600;0,9..144,700;0,9..144,900;1,9..144,600;1,9..144,700&family=Playfair+Display:ital,wght@0,700;0,900;1,700&family=Fira+Code:wght@400&display=swap" rel="stylesheet" />
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
<style>
{THEME_ROOT_VARS}
{css}
{THEME_OVERRIDES}
</style>
</head>
<body>
<button class="sidebar-toggle" onclick="toggleSidebar()" aria-label="Toggle sidebar">&#9776;</button>
<div class="app-layout">
  <!-- === SIDEBAR === -->
  <aside class="sidebar" id="sidebar">
    <div class="sidebar-header"><span aria-hidden="true">🍍</span><span>{esc(project)}</span></div>
    <div class="sidebar-content">
      <div class="file-tree" id="fileTree"><ul>{tree_html}</ul></div>
    </div>
  </aside>

  <!-- === MAIN === -->
  <main class="main-content">
    <div class="top-bar">
      <div class="tab-bar" role="tablist" aria-label="Visualization tabs">
        <button class="tab-btn active" role="tab" data-tab="overview" onclick="switchTab('overview')">Overview</button>
        <button class="tab-btn" role="tab" data-tab="product" onclick="switchTab('product')">Product</button>
        <button class="tab-btn" role="tab" data-tab="technical" onclick="switchTab('technical')">Technical</button>
        <button class="tab-btn" role="tab" data-tab="security" onclick="switchTab('security')">Security</button>
        <button class="tab-btn" role="tab" data-tab="dashboard" onclick="switchTab('dashboard')">Dashboard</button>
        <button class="tab-btn" role="tab" data-tab="feasibility" onclick="switchTab('feasibility')">Feasibility</button>
        <button class="tab-btn" role="tab" data-tab="simulations" onclick="switchTab('simulations')">Simulations</button>
      </div>
      <div class="mode-toggle" role="group" aria-label="Audience mode">
        <button id="modeDev" class="active" onclick="setMode('dev')">Developer</button>
        <button id="modeEasy" onclick="setMode('easy')">Easy</button>
      </div>
      <div class="search-box">
        <input type="text" id="searchInput" placeholder="Search... ( / )" aria-label="Search visualization" oninput="handleSearch(this.value)" />
      </div>
    </div>

    <!-- === OVERVIEW === -->
    <section class="tab-panel active" id="panel-overview" role="tabpanel">
      <div class="breadcrumb"><span>{esc(project)}</span><span class="breadcrumb-sep">/</span><span>Overview</span></div>
      <h1>{esc(project)} Architecture Map
        <button class="tooltip-trigger" type="button"
          data-tooltip="Use tabs to change view, press / to search, 1-7 to jump between tabs."
          aria-label="How to use this visualization">?</button>
      </h1>
      <p data-searchable class="easy-only">A plain-language tour of what this project does, how it is put together, and where to look next.</p>
      <p data-searchable class="dev-only">Structural extraction plus semantic enrichment of modules, dependencies, and security posture.</p>

      <div class="metrics-row">
        <div class="metric-card" data-searchable><div class="card-title">Files</div><div class="card-value">{files_count}</div><div class="card-label">scanned files</div></div>
        <div class="metric-card" data-searchable><div class="card-title">Lines</div><div class="card-value">{lines_count}</div><div class="card-label">total LOC</div></div>
        <div class="metric-card" data-searchable><div class="card-title">Dependencies</div><div class="card-value">{len(deps)}</div><div class="card-label">external packages</div></div>
        <div class="metric-card" data-searchable><div class="card-title">Symbols</div><div class="card-value">{symbols_count}</div><div class="card-label">catalogued symbols</div></div>
      </div>

      <h2>Frameworks
        <button class="tooltip-trigger" type="button" data-tooltip="Detected from package manifests and imports." aria-label="Frameworks explanation">?</button>
      </h2>
      <p>{framework_badges}</p>

      <h2>Language Breakdown</h2>
      <div class="lang-bar-container">
        <div class="lang-bar">{segments}</div>
        <div class="lang-legend">{legend}</div>
      </div>

      <h2>Navigation</h2>
      <p>Use tabs <span class="kbd">1</span>-<span class="kbd">7</span>, press <span class="kbd">/</span> to search, <span class="kbd">Esc</span> to clear.</p>
    </section>

    <!-- === PRODUCT === -->
    <section class="tab-panel" id="panel-product" role="tabpanel">
      <div class="breadcrumb"><span>{esc(project)}</span><span class="breadcrumb-sep">/</span><span>Product</span></div>
      <h2>Feature Map</h2>
      <div class="card-grid">
        <article class="card" data-searchable><div class="card-title">Task Management</div><p>CRUD + assignment workflow for tasks with filtering and pagination.</p></article>
        <article class="card" data-searchable><div class="card-title">Auth &amp; Identity</div><p>Register, login, profile endpoint issuing JWT tokens.</p></article>
        <article class="card" data-searchable><div class="card-title">Shared Domain</div><p>Reusable types, validators, and utility helpers across API + CLI.</p></article>
        <article class="card" data-searchable><div class="card-title">Operational Controls</div><p>Helmet, CORS, rate limiter, request logger, payload limits.</p></article>
        <article class="card" data-searchable><div class="card-title">CLI UX</div><p>Command-driven task listing, creation, and credential login flow.</p></article>
      </div>

      <h2>Request / Data Workflow</h2>
      <div class="diagram-container">
        <pre class="mermaid" data-original="{esc(workflow_mermaid)}">{workflow_mermaid}</pre>
      </div>

      <h2>Entry Points</h2>
      <ul>{entry_list}</ul>
    </section>

    <!-- === TECHNICAL === -->
    <section class="tab-panel" id="panel-technical" role="tabpanel">
      <div class="breadcrumb"><span>{esc(project)}</span><span class="breadcrumb-sep">/</span><span>Technical</span></div>
      <h2>Architecture Diagram</h2>
      <div class="diagram-container">
        <pre class="mermaid" data-original="{esc(arch_mermaid)}">{arch_mermaid}</pre>
      </div>

      <h2>Module Dependency Graph</h2>
      <div class="diagram-container">
        <pre class="mermaid" data-original="{esc(dep_mermaid)}">{dep_mermaid}</pre>
      </div>

      <h2>Symbol Catalog
        <button class="tooltip-trigger" type="button" data-tooltip="Classes, functions, and interfaces extracted from code." aria-label="Symbol catalog">?</button>
      </h2>
      <table class="data-table">
        <thead><tr><th>Name</th><th>Kind</th><th>File</th><th>Exported</th></tr></thead>
        <tbody>{symbol_rows}</tbody>
      </table>
    </section>

    <!-- === SECURITY === -->
    <section class="tab-panel" id="panel-security" role="tabpanel">
      <div class="breadcrumb"><span>{esc(project)}</span><span class="breadcrumb-sep">/</span><span>Security</span></div>
      <h2>Risk Summary</h2>
      <div class="metrics-row">
        <div class="metric-card"><div class="card-title">High</div><div class="card-value">2</div><div class="card-label">Immediate action</div></div>
        <div class="metric-card"><div class="card-title">Medium</div><div class="card-value">2</div><div class="card-label">Harden before prod</div></div>
        <div class="metric-card"><div class="card-title">Low</div><div class="card-value">1</div><div class="card-label">Best-practice gaps</div></div>
      </div>
      <h2>Findings</h2>
      {findings_html}
    </section>

    <!-- === DASHBOARD === -->
    <section class="tab-panel" id="panel-dashboard" role="tabpanel">
      <div class="breadcrumb"><span>{esc(project)}</span><span class="breadcrumb-sep">/</span><span>Dashboard</span></div>
      <h2>Stakeholder Dashboard</h2>
      <div class="card-grid">
        <article class="card" data-searchable><div class="card-title">Product KPIs</div><p>Track feature areas (auth, task CRUD, CLI UX) and user-facing capabilities.</p></article>
        <article class="card" data-searchable><div class="card-title">Engineering Health</div><p>Baseline metrics: {files_count} files, {lines_count} LOC, {symbols_count} symbols.</p></article>
        <article class="card" data-searchable><div class="card-title">Module → Value</div><p>Routes and controllers map to revenue-relevant workflows; middleware supports reliability.</p></article>
        <article class="card" data-searchable><div class="card-title">Collaboration Cues</div><p>Security fallbacks need Product sign-off on rollout policy.</p></article>
      </div>
    </section>

    <!-- === FEASIBILITY === -->
    <section class="tab-panel" id="panel-feasibility" role="tabpanel">
      <div class="breadcrumb"><span>{esc(project)}</span><span class="breadcrumb-sep">/</span><span>Feasibility</span></div>
      <h2>Feasibility Demo Narrative</h2>
      <div class="card-grid">
        <article class="card" data-searchable><div class="card-title">How it works (top-down)</div><p>Clients call an HTTP API. Middleware secures and validates requests. Controllers run business logic. State is tracked in memory for demo; a database is the next step.</p></article>
        <article class="card" data-searchable><div class="card-title">Problem / Value</div><p>Teams need a clear, structural view of their codebase to communicate status and unblock decisions.</p></article>
        <article class="card" data-searchable><div class="card-title">Pitch copy</div><p>"From code to clarity: a shared visual of what your system does and how it runs."</p></article>
        <article class="card" data-searchable><div class="card-title">Media plan hook</div><p>30–60s demo script: open HTML → tour tabs → highlight dependency graph + security risks.</p></article>
      </div>
    </section>

    <!-- === SIMULATIONS === -->
    <section class="tab-panel" id="panel-simulations" role="tabpanel">
      <div class="breadcrumb"><span>{esc(project)}</span><span class="breadcrumb-sep">/</span><span>Simulations</span></div>
      <h2>Scenario Explorer</h2>
      <div class="card-grid">
        <article class="card" data-searchable><div class="card-title">Scale-up</div><p>Traffic grows 10x. Expect rate limiter saturation; plan queued background tasks.</p></article>
        <article class="card" data-searchable><div class="card-title">New feature</div><p>Add "task comments". Touches types, validation, task controller, and CLI list view.</p></article>
        <article class="card" data-searchable><div class="card-title">Dependency incident</div><p>JWT library vulnerability. Centralize secret + add automated dependency scanning.</p></article>
        <article class="card" data-searchable><div class="card-title">Team handoff</div><p>Product ↔ Engineering coordination: use Dashboard tab for shared KPIs.</p></article>
      </div>
    </section>
  </main>
</div>

<script>
  // === MERMAID INIT ===
    mermaid.initialize({{
    startOnLoad: true,
    theme: 'base',
    securityLevel: 'loose',
    flowchart: {{ useMaxWidth: true, htmlLabels: true, curve: 'basis' }},
    themeVariables: {{
      primaryColor: '#FFD700',
      primaryTextColor: '#3B2A0A',
      primaryBorderColor: '#F4A300',
      lineColor: '#4CAF50',
      secondaryColor: '#4CAF50',
      secondaryTextColor: '#FFF9E6',
      secondaryBorderColor: '#2E7D32',
      tertiaryColor: '#FFF9E6',
      tertiaryTextColor: '#3B2A0A',
      tertiaryBorderColor: '#8B5A2B',
      edgeLabelBackground: '#FFF9E6',
      clusterBkg: 'rgba(255, 236, 179, 0.55)',
      clusterBorder: '#8B5A2B',
      fontFamily: '"DM Sans", Inter, system-ui, sans-serif',
      fontSize: '14px'
    }}
  }});

  document.querySelectorAll('[data-searchable]').forEach((el) => {{
    el.dataset.originalHtml = el.innerHTML;
  }});

  // === TAB SWITCHING ===
  function switchTab(tabId) {{
    document.querySelectorAll('.tab-btn').forEach((btn) => btn.classList.toggle('active', btn.dataset.tab === tabId));
    document.querySelectorAll('.tab-panel').forEach((panel) => panel.classList.toggle('active', panel.id === 'panel-' + tabId));
    const panel = document.getElementById('panel-' + tabId);
    if (panel) {{
      panel.querySelectorAll('.mermaid[data-processed]').forEach((el) => {{
        el.removeAttribute('data-processed');
        el.innerHTML = el.getAttribute('data-original') || el.textContent;
      }});
      mermaid.run({{ nodes: panel.querySelectorAll('.mermaid') }});
    }}
  }}

  // === SEARCH ===
  function escapeRegExp(str) {{
    return str.replace(/[.*+?^${{}}()|[\\]\\\\]/g, '\\\\$&');
  }}
  function highlightText(el, query) {{
    const original = el.dataset.originalHtml || el.innerHTML;
    const plain = original.replace(/<[^>]+>/g, ' ');
    if (!plain.toLowerCase().includes(query)) return;
    const re = new RegExp('(' + escapeRegExp(query) + ')', 'ig');
    el.innerHTML = original.replace(re, '<span class="search-highlight">$1</span>');
  }}
  function clearSearch() {{
    document.querySelectorAll('[data-searchable]').forEach((el) => {{
      el.style.display = '';
      if (el.dataset.originalHtml) el.innerHTML = el.dataset.originalHtml;
    }});
  }}
  function handleSearch(query) {{
    const q = (query || '').toLowerCase().trim();
    if (!q) {{ clearSearch(); return; }}
    document.querySelectorAll('[data-searchable]').forEach((el) => {{
      const hay = (el.dataset.originalHtml || el.textContent || '').toLowerCase();
      const match = hay.includes(q);
      el.style.display = match ? '' : 'none';
      if (match) {{
        if (el.dataset.originalHtml) el.innerHTML = el.dataset.originalHtml;
        highlightText(el, q);
      }}
    }});
  }}

  // === FILE TREE ===
  function toggleTreeNode(element) {{
    const children = element.nextElementSibling;
    const toggle = element.querySelector('.tree-toggle');
    if (children && children.classList.contains('tree-children')) {{
      children.classList.toggle('collapsed');
      if (toggle) toggle.classList.toggle('open');
    }}
  }}
  function scrollToSymbol(filePath) {{
    const row = document.querySelector('tr[data-file="' + CSS.escape(filePath) + '"]');
    if (row) {{
      switchTab('technical');
      row.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
      row.classList.add('search-highlight-flash');
      setTimeout(() => row.classList.remove('search-highlight-flash'), 450);
    }}
  }}
  document.querySelectorAll('.tree-item[data-file-path]').forEach((el) => {{
    const fp = el.getAttribute('data-file-path');
    el.addEventListener('click', () => {{
      document.querySelectorAll('.tree-item').forEach((x) => x.classList.remove('active'));
      el.classList.add('active');
      if (fp) scrollToSymbol(fp);
    }});
    el.addEventListener('keydown', (e) => {{
      if (e.key === 'Enter' || e.key === ' ') {{ e.preventDefault(); el.click(); }}
    }});
  }});

  // === SIDEBAR ===
  function toggleSidebar() {{ document.getElementById('sidebar').classList.toggle('open'); }}
  document.addEventListener('click', (e) => {{
    const sidebar = document.getElementById('sidebar');
    const toggle = document.querySelector('.sidebar-toggle');
    if (window.innerWidth <= 768 && sidebar && sidebar.classList.contains('open') && !sidebar.contains(e.target) && toggle && !toggle.contains(e.target)) {{
      sidebar.classList.remove('open');
    }}
  }});

  // === MODE TOGGLE ===
  function setMode(mode) {{
    document.body.classList.toggle('easy-mode', mode === 'easy');
    document.getElementById('modeDev').classList.toggle('active', mode === 'dev');
    document.getElementById('modeEasy').classList.toggle('active', mode === 'easy');
  }}

  // === TOOLTIPS ===
  function initTooltips() {{
    const targets = document.querySelectorAll('[data-tooltip]');
    if (!targets.length) return;
    const bubble = document.createElement('div');
    bubble.className = 'tooltip-bubble';
    bubble.setAttribute('role', 'tooltip');
    document.body.appendChild(bubble);
    const show = (el, evt) => {{
      bubble.textContent = el.getAttribute('data-tooltip') || '';
      bubble.classList.add('visible');
      const rect = el.getBoundingClientRect();
      const x = (evt && evt.clientX) != null ? evt.clientX : rect.left + rect.width / 2;
      const y = (evt && evt.clientY) != null ? evt.clientY : rect.top;
      bubble.style.left = Math.max(8, Math.min(window.innerWidth - bubble.offsetWidth - 8, x + 12)) + 'px';
      bubble.style.top = Math.max(8, y - bubble.offsetHeight - 10) + 'px';
    }};
    const hide = () => bubble.classList.remove('visible');
    targets.forEach((el) => {{
      el.addEventListener('mouseenter', (evt) => show(el, evt));
      el.addEventListener('mousemove', (evt) => show(el, evt));
      el.addEventListener('focus', () => show(el));
      el.addEventListener('mouseleave', hide);
      el.addEventListener('blur', hide);
    }});
  }}
  initTooltips();

  // === KEYBOARD SHORTCUTS ===
  document.addEventListener('keydown', (e) => {{
    if (e.target.tagName === 'INPUT') return;
    const map = {{ '1': 'overview', '2': 'product', '3': 'technical', '4': 'security', '5': 'dashboard', '6': 'feasibility', '7': 'simulations' }};
    if (map[e.key]) {{ switchTab(map[e.key]); return; }}
    if (e.key === '/') {{ e.preventDefault(); document.getElementById('searchInput').focus(); }}
    if (e.key === 'Escape') {{
      const input = document.getElementById('searchInput');
      input.value = '';
      clearSearch();
      input.blur();
    }}
  }});

  mermaid.run();
</script>
</body>
</html>
"""
    output_path.write_text(html_doc)


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: generate-visualization.py <analysis.json> <output.html> [title] [project_name]", file=sys.stderr)
        sys.exit(2)
    analysis_path = Path(sys.argv[1]).resolve()
    output_path = Path(sys.argv[2]).resolve()
    title = sys.argv[3] if len(sys.argv) > 3 else None
    project_override = sys.argv[4] if len(sys.argv) > 4 else None
    generate(analysis_path, output_path, title, project_override)
    size_kb = output_path.stat().st_size // 1024
    print(f"generated {output_path} ({size_kb} KB)")


if __name__ == "__main__":
    main()
