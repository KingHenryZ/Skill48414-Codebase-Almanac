#!/usr/bin/env python3
"""
generate-visualization.py

Generate a single self-contained HTML code visualization from an analysis JSON
produced by `scripts/extract-codebase.py`. Follows the contracts in SKILL.md,
html-template.md, and visualization-base.css.

Usage:
  python scripts/generate-visualization.py <analysis.json> <output.html> [title] [project_name]
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

/* === Section panels === */
.tab-panel {
  position: relative;
  padding: 28px 32px 42px;
  margin: 18px 18px 24px;
  border-radius: 22px;
  isolation: isolate;
  background:
    radial-gradient(ellipse 55% 45% at 12% 8%, rgba(244, 163, 0, 0.32) 0%, rgba(244, 163, 0, 0) 60%),
    radial-gradient(ellipse 45% 40% at 92% 12%, rgba(255, 215, 0, 0.38) 0%, rgba(255, 215, 0, 0) 62%),
    radial-gradient(ellipse 60% 55% at 88% 92%, rgba(255, 138, 61, 0.22) 0%, transparent 65%),
    radial-gradient(ellipse 50% 45% at 8% 90%, rgba(76, 175, 80, 0.18) 0%, transparent 65%),
    linear-gradient(160deg, #FFF4C2 0%, #FFE9A0 45%, #FFD95B 100%);
  border: 2px solid rgba(212, 160, 23, 0.55);
  box-shadow:
    0 20px 48px rgba(139, 90, 43, 0.22),
    inset 0 1px 0 rgba(255, 255, 255, 0.65),
    inset 0 -40px 80px rgba(244, 163, 0, 0.12);
}
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

/* === Top bar + tabs === */
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
.tab-bar { gap: 4px; flex-wrap: wrap; }
.tab-btn {
  background: linear-gradient(180deg, #FFF9E6, #FFECB3) !important;
  color: var(--text-primary) !important;
  border: 2px solid var(--border-color) !important;
  border-radius: 999px !important;
  font-weight: 600;
  padding: 6px 14px !important;
  transition: transform 0.12s ease, box-shadow 0.15s ease;
  font-size: 0.82rem;
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

/* === Typography === */
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
    radial-gradient(ellipse 70% 60% at 10% 0%, rgba(255, 215, 0, 0.38) 0%, transparent 60%),
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

/* Findings severity */
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
  display: inline-block;
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

/* === Search highlights === */
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

/* Scrollbar */
::-webkit-scrollbar { width: 12px; height: 12px; }
::-webkit-scrollbar-track { background: #FFECB3; }
::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #F4A300, #4CAF50);
  border-radius: 999px;
  border: 2px solid #FFECB3;
}
::-webkit-scrollbar-thumb:hover { background: linear-gradient(180deg, #FFD700, #2E7D32); }

/* ═══ HERO ═══ */

.hero {
  position: relative;
  isolation: isolate;
  margin: -8px -32px 28px;
  padding: clamp(40px, 6vw, 80px) clamp(32px, 6vw, 84px) clamp(52px, 7vw, 96px);
  min-height: 460px;
  border-radius: 22px 22px 28px 28px;
  overflow: hidden;
  background:
    radial-gradient(ellipse 50% 70% at 8% 40%, rgba(255, 215, 0, 0.38) 0%, transparent 60%),
    radial-gradient(ellipse 55% 75% at 90% 80%, rgba(244, 163, 0, 0.28) 0%, transparent 65%),
    radial-gradient(ellipse 40% 50% at 100% 0%, rgba(255, 249, 230, 0.7) 0%, transparent 60%),
    linear-gradient(135deg, #FFF4C2 0%, #FFE27A 55%, #FFC947 100%);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.65),
              0 18px 48px rgba(139, 90, 43, 0.25);
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(0, 1fr);
  gap: 0;
  align-items: center;
}
.hero::before {
  content: "";
  position: absolute;
  inset: 0;
  background-image: var(--grain-soft);
  background-size: 260px 260px;
  mix-blend-mode: multiply;
  opacity: 0.45;
  pointer-events: none;
  z-index: 0;
}
.hero::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(120deg,
    rgba(255, 255, 255, 0.55) 0%,
    rgba(255, 255, 255, 0.10) 28%,
    transparent 48%);
  mix-blend-mode: screen;
  pointer-events: none;
  z-index: 0;
}

.hero-content {
  position: relative;
  z-index: 2;
  max-width: 640px;
  padding-right: 20px;
  text-align: left;
}
.hero-eyebrow {
  display: inline-block;
  font-family: var(--font-body);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.28em;
  text-transform: uppercase;
  color: var(--leaf-deep);
  background: rgba(255, 249, 230, 0.85);
  border: 1.5px dashed var(--rind);
  padding: 5px 14px;
  border-radius: 999px;
  margin-bottom: 18px;
  box-shadow: 0 3px 10px rgba(244, 163, 0, 0.2);
}
.hero-content h1 {
  font-size: clamp(2.8rem, 5.4vw, 4.6rem) !important;
  line-height: 0.98;
  margin-bottom: 0.35em;
}
.hero-content h1::after {
  margin-top: 18px;
  margin-left: 0;
  width: min(420px, 70%);
}
.hero-lede {
  font-family: var(--font-display);
  font-style: italic;
  font-weight: 700;
  font-size: clamp(1.05rem, 1.5vw, 1.28rem);
  color: var(--rind-deep);
  max-width: 54ch;
  margin-top: 0.5em;
}
.hero-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 28px;
}
.hero-meta .chip {
  padding: 6px 14px;
  border-radius: 999px;
  background: rgba(255, 249, 230, 0.92);
  border: 1.5px solid var(--border-color);
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 0.88rem;
  box-shadow: 0 2px 8px rgba(244, 163, 0, 0.18);
}
.hero-meta .chip strong {
  color: var(--leaf-deep);
  font-family: var(--font-heading);
  font-weight: 700;
}

.hero-art {
  position: absolute;
  top: -42px;
  right: clamp(-220px, -14vw, -120px);
  width: clamp(520px, 68%, 860px);
  height: auto;
  z-index: 1;
  pointer-events: none;
  transform: rotate(6deg);
  filter: drop-shadow(0 30px 46px rgba(139, 90, 43, 0.35));
  animation: heroFloat 9s ease-in-out infinite;
}
.hero-pineapple { width: 100%; height: auto; display: block; }
@keyframes heroFloat {
  0%, 100% { transform: rotate(6deg) translateY(0); }
  50%      { transform: rotate(5deg) translateY(-14px); }
}

.hero-leaf {
  position: absolute;
  pointer-events: none;
  z-index: 3;
  filter: drop-shadow(0 6px 10px rgba(46, 125, 50, 0.35));
}
.hero-leaf.one   { top: 20px;   left: 44%; width: 90px;  transform: rotate(-18deg); opacity: 0.9; }
.hero-leaf.two   { bottom: 60px; left: 36%; width: 70px; transform: rotate(28deg); opacity: 0.85; }

@media (max-width: 900px) {
  .hero {
    grid-template-columns: 1fr;
    min-height: auto;
    padding: 36px 28px 200px;
  }
  .hero-art {
    top: auto;
    bottom: -120px;
    right: -160px;
    width: 420px;
    transform: rotate(10deg);
  }
  .hero-leaf { display: none; }
}
@media (max-width: 600px) {
  .hero-art { width: 340px; right: -120px; bottom: -90px; }
}

/* ═══ BUTTONS ═══ */

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
  border-radius: 999px;
  padding: 9px 20px;
  box-shadow:
    0 3px 0 var(--rind),
    0 10px 20px rgba(244, 163, 0, 0.32),
    inset 0 1px 0 rgba(255, 255, 255, 0.55);
}

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

.tooltip-trigger:hover {
  transform: translateY(-2px);
  filter: brightness(1.1);
  box-shadow: 0 4px 10px rgba(244, 163, 0, 0.45);
}

/* ═══ PINEAPPLE-SKIN DIVIDERS ═══ */

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

/* Easy mode visibility */
body.easy-mode .dev-only { display: none !important; }
body:not(.easy-mode) .easy-only { display: none !important; }

/* === Summary link cards (Overview lower half) === */
.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
  margin-top: 24px;
}
.summary-link-card {
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
  padding: 22px;
}
.summary-link-card:hover {
  transform: translateY(-4px) rotate(-0.3deg);
}
.summary-link-card .card-icon {
  font-size: 1.8rem;
  margin-bottom: 8px;
}
.summary-link-card .card-title {
  font-size: 1.05rem;
  margin-bottom: 6px;
}
.summary-link-card .card-desc {
  font-size: 0.88rem;
  color: var(--text-muted);
  line-height: 1.45;
}
.summary-link-card .card-link {
  display: inline-block;
  margin-top: 10px;
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--leaf-deep);
}

/* === Traffic light indicators === */
.traffic-light {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 4px 14px;
  border-radius: 999px;
  font-weight: 700;
  font-size: 0.88rem;
}
.traffic-green { background: #d1fae5; color: #065f46; border: 2px solid #10b981; }
.traffic-yellow { background: #fef3c7; color: #92400e; border: 2px solid #f59e0b; }
.traffic-red { background: #fee2e2; color: #991b1b; border: 2px solid #ef4444; }

/* === Checklist === */
.checklist { list-style: none; padding: 0; }
.checklist li {
  padding: 6px 0;
  font-size: 1rem;
}
.checklist li::before {
  content: "✅ ";
}

/* === Priority labels === */
.priority-tag {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 700;
}
.priority-now { background: #fee2e2; color: #991b1b; border: 1px solid #ef4444; }
.priority-soon { background: #fef3c7; color: #92400e; border: 1px solid #f59e0b; }
.priority-later { background: #dbeafe; color: #1e40af; border: 1px solid #3b82f6; }

/* === Pitch copyable block === */
.copyable-block {
  background: rgba(255, 249, 230, 0.95);
  border: 2px dashed var(--border-color);
  border-radius: var(--radius);
  padding: 20px 24px;
  font-family: var(--font-display);
  font-style: italic;
  font-size: 1.1rem;
  line-height: 1.65;
  color: var(--rind-deep);
  position: relative;
}
.copyable-block::after {
  content: "📋 Click to copy";
  position: absolute;
  top: 8px;
  right: 12px;
  font-size: 0.68rem;
  font-style: normal;
  font-family: var(--font-body);
  color: var(--text-muted);
  opacity: 0.7;
}
"""


# ── Hero illustration: hand-drawn-feeling pineapple in SVG ─────────────
HERO_PINEAPPLE_SVG = """\
<svg class="hero-pineapple" viewBox="0 0 640 920" xmlns="http://www.w3.org/2000/svg"
     role="img" aria-hidden="true" preserveAspectRatio="xMidYMid meet">
  <defs>
    <linearGradient id="body-grad" x1="0.15" y1="0" x2="0.9" y2="1">
      <stop offset="0%"  stop-color="#FFF3B0"/>
      <stop offset="35%" stop-color="#FFD700"/>
      <stop offset="75%" stop-color="#F4A300"/>
      <stop offset="100%" stop-color="#9E6A0A"/>
    </linearGradient>
    <radialGradient id="body-sheen" cx="0.28" cy="0.28" r="0.55">
      <stop offset="0%"  stop-color="#FFF8DC" stop-opacity="0.85"/>
      <stop offset="60%" stop-color="#FFF8DC" stop-opacity="0.15"/>
      <stop offset="100%" stop-color="#FFF8DC" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="leaf-front" x1="0.5" y1="0" x2="0.5" y2="1">
      <stop offset="0%"  stop-color="#A5D6A7"/>
      <stop offset="50%" stop-color="#4CAF50"/>
      <stop offset="100%" stop-color="#1B5E20"/>
    </linearGradient>
    <linearGradient id="leaf-mid" x1="0.5" y1="0" x2="0.5" y2="1">
      <stop offset="0%"  stop-color="#81C784"/>
      <stop offset="100%" stop-color="#2E7D32"/>
    </linearGradient>
    <linearGradient id="leaf-back" x1="0.5" y1="0" x2="0.5" y2="1">
      <stop offset="0%"  stop-color="#4CAF50"/>
      <stop offset="100%" stop-color="#0F3B14"/>
    </linearGradient>
    <pattern id="diamond" x="0" y="0" width="74" height="74" patternUnits="userSpaceOnUse" patternTransform="rotate(2)">
      <path d="M 37 0 L 74 37 L 37 74 L 0 37 Z"
            fill="none" stroke="#8B5A2B" stroke-width="2.4" stroke-linejoin="round" opacity="0.75"/>
      <circle cx="37" cy="37" r="3" fill="#F4A300"/>
      <circle cx="0"  cy="37" r="2.2" fill="#C9820A" opacity="0.8"/>
      <circle cx="74" cy="37" r="2.2" fill="#C9820A" opacity="0.8"/>
      <circle cx="37" cy="0"  r="2.2" fill="#C9820A" opacity="0.8"/>
      <circle cx="37" cy="74" r="2.2" fill="#C9820A" opacity="0.8"/>
    </pattern>
    <filter id="soft-shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur in="SourceAlpha" stdDeviation="8"/>
      <feOffset dx="0" dy="14" result="off"/>
      <feColorMatrix in="off" type="matrix"
        values="0 0 0 0 0.54  0 0 0 0 0.35  0 0 0 0 0.10  0 0 0 0.55 0"/>
      <feBlend in="SourceGraphic" in2="off" mode="normal"/>
    </filter>
  </defs>

  <circle cx="320" cy="520" r="340" fill="#FFD700" opacity="0.18"/>
  <circle cx="320" cy="520" r="260" fill="#FFE27A" opacity="0.28"/>

  <g filter="url(#soft-shadow)">
    <path d="M 210 340 Q 150 180 90 80  Q 140 220 170 330 Z"  fill="url(#leaf-back)"/>
    <path d="M 430 340 Q 490 180 550 80 Q 500 220 470 330 Z"  fill="url(#leaf-back)"/>
    <path d="M 260 345 Q 220 140 200 20 Q 250 180 265 335 Z"  fill="url(#leaf-back)"/>
    <path d="M 380 345 Q 420 140 440 20 Q 390 180 375 335 Z"  fill="url(#leaf-back)"/>
  </g>

  <g>
    <path d="M 240 355 Q 210 170 190 40  Q 245 200 258 345 Z" fill="url(#leaf-mid)"/>
    <path d="M 400 355 Q 430 170 450 40  Q 395 200 382 345 Z" fill="url(#leaf-mid)"/>
    <path d="M 285 355 Q 270 130 260 0   Q 295 170 298 345 Z" fill="url(#leaf-mid)"/>
    <path d="M 355 355 Q 370 130 380 0   Q 345 170 342 345 Z" fill="url(#leaf-mid)"/>
  </g>

  <g>
    <path d="M 315 360 Q 308 140 318 15 Q 325 160 325 355 Z" fill="url(#leaf-front)"/>
    <path d="M 325 360 Q 335 140 322 15 Q 317 160 315 355 Z" fill="url(#leaf-front)" opacity="0.85"/>
    <path d="M 320 140 Q 322 80 325 30" stroke="#E8F5E9" stroke-width="2" fill="none" opacity="0.6"/>
    <path d="M 300 200 Q 292 120 280 50" stroke="#C8E6C9" stroke-width="1.5" fill="none" opacity="0.5"/>
    <path d="M 340 200 Q 348 120 360 50" stroke="#C8E6C9" stroke-width="1.5" fill="none" opacity="0.5"/>
  </g>

  <g filter="url(#soft-shadow)">
    <ellipse cx="320" cy="580" rx="240" ry="300" fill="url(#body-grad)"
             stroke="#8B5A2B" stroke-width="5"/>
  </g>
  <ellipse cx="320" cy="580" rx="236" ry="296" fill="url(#diamond)" opacity="0.85"/>
  <ellipse cx="250" cy="470" rx="110" ry="150" fill="url(#body-sheen)"/>
  <path d="M 130 720 Q 320 920 510 720 Q 430 870 320 880 Q 210 870 130 720 Z"
        fill="#8B5A2B" opacity="0.18"/>

  <g opacity="0.8">
    <path d="M 70 440 q 10 -18 30 -8 q -18 10 -30 8 Z"  fill="#4CAF50"/>
    <path d="M 560 400 q -10 -18 -30 -8 q 18 10 30 8 Z" fill="#4CAF50"/>
    <path d="M 40 680 q 14 -10 26 6 q -18 0 -26 -6 Z"    fill="#66BB6A"/>
    <path d="M 585 700 q -14 -10 -26 6 q 18 0 26 -6 Z"   fill="#66BB6A"/>
  </g>
</svg>
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


# ── Utility helpers ─────────────────────────────────────────────────────

def esc(s: object) -> str:
    return html.escape(str(s))


def mermaid_safe_label(s: str) -> str:
    """Escape text for inside [\"...\"] in Mermaid — never use HTML entities here."""
    t = str(s).replace("\r", " ").replace("\n", " ").replace('"', "'").strip()
    if len(t) > 160:
        t = t[:157] + "..."
    return t


def _fix_mermaid_subgraph_titles(text: str) -> str:
    """Mermaid 10+ requires a space before the title bracket: subgraph id [Title].

    Quotes are preserved when the title contains special characters (@, /, :, etc.)
    because Mermaid's parser chokes on unquoted special chars inside brackets.
    """
    _needs_quotes = re.compile(r"[^a-zA-Z0-9 _\-.]")

    def repl(m: re.Match[str]) -> str:
        sid, title = m.group(1), m.group(2)
        if _needs_quotes.search(title):
            return f'subgraph {sid} ["{title}"]'
        return f"subgraph {sid} [{title}]"

    out = re.sub(
        r"subgraph\s+([\w]+)\s*\[\s*\"([^\"]*)\"\s*\]",
        repl,
        text,
        flags=re.MULTILINE,
    )
    out = re.sub(
        r"subgraph\s+([\w]+)\s*\[\s*'([^']*)'\s*\]",
        repl,
        out,
        flags=re.MULTILINE,
    )
    return out


def _fix_er_diagram_text_types(text: str) -> str:
    """Mermaid erDiagram uses types like string/int — SQL 'text' breaks the parser."""
    if not text.lstrip().startswith("erDiagram"):
        return text
    lines = text.split("\n")
    out: list[str] = []
    in_entity = False
    entity_start = re.compile(r"^\s*[\w]+\s*\{\s*$")
    entity_end = re.compile(r"^\s*\}\s*$")
    for line in lines:
        ls = line.strip()
        if entity_start.match(line.rstrip()):
            in_entity = True
            out.append(line)
            continue
        if in_entity and entity_end.match(line.rstrip()):
            in_entity = False
            out.append(line)
            continue
        if in_entity and ls and not re.search(r"\|\|", line):
            parts = ls.split()
            if len(parts) >= 2 and parts[0].lower() == "text":
                idx = line.find(parts[0])
                if idx >= 0:
                    line = line[:idx] + "string" + line[idx + len(parts[0]) :]
        out.append(line)
    return "\n".join(out)


def _fix_flowchart_square_bracket_colons(line: str) -> str:
    """Labels like A[foo: bar] confuse the flowchart parser; require A[\"foo: bar\"]."""
    stripped = line.strip()
    if stripped.startswith(
        ("%%", "classDef", "class ", "direction", "linkStyle", "subgraph", "end", "style ", "erDiagram")
    ):
        return line

    def repl(m: re.Match[str]) -> str:
        nid, lb, inner, rb = m.group(1), m.group(2), m.group(3), m.group(4)
        inner_st = inner.strip()
        if ":" in inner_st and not (inner_st.startswith('"') and inner_st.endswith('"')):
            safe = inner.replace('"', "'")
            return f'{nid}{lb}"{safe}"{rb}'
        return m.group(0)

    return re.sub(r"([\w]+)(\[)([^\]]+)(\])", repl, line)


def prepare_mermaid_source(raw: str | None) -> str:
    """Normalize AI- or extractor-produced Mermaid so Mermaid.js 10/11 can parse it."""
    if raw is None:
        return ""
    s = html.unescape(str(raw)).replace("\r\n", "\n").replace("\r", "\n")
    s = _fix_mermaid_subgraph_titles(s)
    s = _fix_er_diagram_text_types(s)
    s = "\n".join(_fix_flowchart_square_bracket_colons(ln) for ln in s.split("\n"))
    return s


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
                lines.append(f'  {node_id}["{mermaid_safe_label(label)}"]')
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


def build_findings(findings_data: list | None = None) -> str:
    findings = findings_data or [
        ("high", "Default JWT secret fallback in source code",
         "middleware/authenticate.ts",
         "Enforce env-only secrets; fail fast on startup when missing."),
        ("high", "Hardcoded secret strings in authentication layer",
         "auth service files",
         "Centralize secret retrieval via a managed secrets provider with rotation."),
        ("medium", "Wildcard CORS fallback when ALLOWED_ORIGINS unset",
         "server.ts",
         "Require explicit origin allowlist in production; reject wildcard."),
        ("medium", "In-memory or single-file persistence",
         "data layer",
         "Move to a durable datastore with connection pooling."),
        ("low", "No request timeout / graceful shutdown hooks",
         "server.ts",
         "Add HTTP server timeouts and SIGTERM handling."),
    ]
    html_parts = []
    for item in findings:
        if isinstance(item, dict):
            sev = item.get("severity", "low")
            title = item.get("title", "")
            location = item.get("location", "")
            rec = (
                item.get("remediation")
                or item.get("recommendation")
                or item.get("detail")
                or ""
            )
        else:
            sev, title, location, rec = item
        html_parts.append(
            f'<article class="finding finding-{sev}" data-searchable>'
            f'<div class="finding-header"><span class="badge badge-{sev}">{sev}</span>'
            f'<div class="finding-title">{esc(title)}</div></div>'
            f'<div class="finding-location">{esc(location)}</div>'
            f'<div class="finding-recommendation"><strong>Recommendation:</strong> {esc(rec)}</div>'
            "</article>"
        )
    return "\n".join(html_parts)


# ── HTML Generation ─────────────────────────────────────────────────────

def generate(analysis_path: Path, output_path: Path, title: str | None = None, project_override: str | None = None, enrichment_path: Path | None = None) -> None:
    root = Path(__file__).resolve().parent.parent
    data = json.loads(analysis_path.read_text())

    if enrichment_path and enrichment_path.exists():
        enrichment_data = json.loads(enrichment_path.read_text())
        existing = data.get("enrichment") or {}
        def deep_merge(base: dict, overlay: dict) -> dict:
            merged = dict(base)
            for k, v in overlay.items():
                if k in merged and isinstance(merged[k], dict) and isinstance(v, dict):
                    merged[k] = deep_merge(merged[k], v)
                else:
                    merged[k] = v
            return merged
        data["enrichment"] = deep_merge(existing, enrichment_data)

    project = project_override or data.get("project_name") or "codebase"
    metrics = data.get("metrics") or {}
    symbols = data.get("symbols") or []
    frameworks = data.get("frameworks") or []
    dep_edges = ((data.get("dependency_graph") or {}).get("edges")) or []
    entry_points = data.get("entry_points") or []
    package_metadata = data.get("package_metadata") or {}
    file_tree = data.get("file_tree") or {}
    enrichment = data.get("enrichment") or {}
    has_database = data.get("has_database", False)

    files_count = metrics.get("total_files", len(data.get("files") or []))
    lines_count = metrics.get("total_lines", 0)
    deps = collect_deps(package_metadata)
    symbols_count = len(symbols)

    css = load_css(root)
    segments, legend = build_language_bar(metrics.get("languages") or {})
    tree_html = build_file_tree_html(file_tree)
    dep_mermaid = prepare_mermaid_source(build_dependency_mermaid(dep_edges))
    symbol_rows = build_symbol_rows(symbols)
    entry_list = build_entry_list(entry_points)
    findings_html = build_findings(enrichment.get("security", {}).get("findings"))

    framework_badges = "".join(
        f'<span class="badge badge-framework" data-searchable>{esc(fw)}</span> '
        for fw in frameworks
    ) or '<span class="badge" data-searchable>None detected</span>'

    title_text = title or f"{project} — Code Visualization"

    # --- Enrichment data (populated by AI in SKILL.md Phase 3) ----------
    ov = enrichment.get("overview", {})
    project_summary = ov.get("project_summary", f"{project} is a software project analyzed by the code visualizer.")
    tab_summaries = ov.get("tab_summaries", {})

    prod = enrichment.get("product", {})
    tech = enrichment.get("technical", {})
    db = enrichment.get("database", {})
    sec = enrichment.get("security", {})
    sug = enrichment.get("suggestions", {})
    pitch = enrichment.get("pitch", {})
    sim = enrichment.get("simulation", {})

    # --- Mermaid defaults -----------------------------------------------
    arch_mermaid = tech.get("dev", {}).get("architecture_mermaid", """graph TB
  subgraph Presentation ["Presentation Layer"]
    Routes[Routes]
    MW[Middleware]
  end
  subgraph Business ["Business Layer"]
    Ctrl[Controllers]
    Valid[Validation]
  end
  subgraph DataLayer ["Data Layer"]
    Store["Datastore"]
  end
  Presentation --> Business --> DataLayer
""")

    arch_mermaid_easy = tech.get("easy", {}).get("architecture_mermaid", """graph TB
  UI["What users see"] --> Logic["App logic"]
  Logic --> Storage["Where data is saved"]
""")

    workflow_mermaid = prod.get("dev", {}).get("workflow_mermaid", """flowchart TD
  Client[Client] --> Req[Request]
  Req --> Secure[Security middleware]
  Secure --> Auth{Authenticated?}
  Auth -->|Yes| Handler[Route handler]
  Auth -->|No| Reject[401 Rejected]
  Handler --> DB["Database"]
  DB --> Resp[JSON response]
""")

    workflow_mermaid_easy = prod.get("easy", {}).get("workflow_mermaid", """flowchart TD
  A["[AI_FILL: Replace with real user workflow for easy mode]"]
""")

    db_er_mermaid = db.get("dev", {}).get("er_mermaid", "")
    db_er_mermaid_easy = db.get("easy", {}).get("er_mermaid", "")
    db_flow_mermaid = db.get("dev", {}).get("data_flow_mermaid", "")

    arch_mermaid = prepare_mermaid_source(arch_mermaid)
    arch_mermaid_easy = prepare_mermaid_source(arch_mermaid_easy)
    workflow_mermaid = prepare_mermaid_source(workflow_mermaid)
    workflow_mermaid_easy = prepare_mermaid_source(workflow_mermaid_easy)
    db_er_mermaid = prepare_mermaid_source(db_er_mermaid)
    db_er_mermaid_easy = prepare_mermaid_source(db_er_mermaid_easy)
    db_flow_mermaid = prepare_mermaid_source(db_flow_mermaid)

    # --- Helper to render card grids from enrichment --------------------
    def render_cards(items: list, extra_class: str = "") -> str:
        out = []
        for item in items:
            if isinstance(item, str):
                out.append(f'<article class="card {extra_class}" data-searchable><p>{esc(item)}</p></article>')
            elif isinstance(item, dict):
                t = item.get("title", "")
                d = item.get("description", "")
                loc = item.get("location", "")
                effort = item.get("effort", "")
                badges = ""
                if effort:
                    badges = f' <span class="badge">{esc(effort)}</span>'
                if loc:
                    d += f'<br><code>{esc(loc)}</code>'
                out.append(
                    f'<article class="card {extra_class}" data-searchable>'
                    f'<div class="card-title">{esc(t)}{badges}</div><p>{d}</p></article>'
                )
        return "\n".join(out)

    def render_checklist(items: list) -> str:
        li = "".join(f"<li>{esc(i)}</li>" for i in items)
        return f'<ul class="checklist">{li}</ul>'

    def render_priority_items(items: list) -> str:
        out = []
        for item in items:
            if isinstance(item, dict):
                label = item.get("label", "Do later")
                text = item.get("text", "")
                cls = {"Do now": "priority-now", "Do soon": "priority-soon"}.get(label, "priority-later")
                out.append(
                    f'<div style="margin:8px 0" data-searchable>'
                    f'<span class="priority-tag {cls}">{esc(label)}</span> '
                    f'{esc(text)}</div>'
                )
        return "\n".join(out)

    # --- Fallback content for each tab ----------------------------------
    def get_list(obj: dict, key: str) -> list:
        v = obj.get(key)
        return v if isinstance(v, list) else []

    def get_str(obj: dict, key: str, fallback: str = "") -> str:
        v = obj.get(key)
        return v if isinstance(v, str) else fallback

    # Product
    prod_dev = prod.get("dev", {})
    prod_easy = prod.get("easy", {})
    prod_feature_cards = render_cards(get_list(prod_dev, "features"))
    prod_api_rows = ""
    for ep in get_list(prod_dev, "api_surface"):
        prod_api_rows += (
            f'<tr data-searchable><td><span class="badge">{esc(ep.get("method",""))}</span></td>'
            f'<td><code>{esc(ep.get("path",""))}</code></td>'
            f'<td>{"🔒" if ep.get("auth") else "🌐"}</td>'
            f'<td>{esc(ep.get("description",""))}</td></tr>'
        )
    prod_arch_text = get_str(prod_dev, "product_architecture", "[AI_FILL: Product architecture — describe how features are distributed across packages]")
    prod_patterns = render_cards(get_list(prod_dev, "design_patterns"))

    prod_easy_what = get_str(prod_easy, "what_it_does", "[AI_FILL: What does this app do — plain-language feature description]")
    prod_easy_capabilities = render_checklist(get_list(prod_easy, "capabilities"))
    prod_easy_org = get_str(prod_easy, "organization", "[AI_FILL: How is the app organized — name the main parts and their roles]")

    # Technical
    tech_dev = tech.get("dev", {})
    tech_easy = tech.get("easy", {})
    tech_backend = get_str(tech_dev, "backend_analysis", "[AI_FILL: Backend analysis — middleware pipeline, route structure, controller patterns, error handling]")
    tech_frontend = get_str(tech_dev, "frontend_analysis", "[AI_FILL: Frontend analysis — component structure, state management, routing, or state that none exists]")
    tech_quality = render_cards(get_list(tech_dev, "code_quality"))

    tech_easy_how = get_str(tech_easy, "how_built", "[AI_FILL: How is the code built — plain-language analogy explaining the layers]")
    tech_easy_parts = get_str(tech_easy, "main_parts", "[AI_FILL: The main parts — describe the actual packages and what they do]")
    tech_easy_connect = get_str(tech_easy, "connections", "[AI_FILL: How the parts connect — describe actual internal dependencies in plain language]")
    tech_easy_health_items = get_list(tech_easy, "health_check")

    # Database
    db_dev = db.get("dev", {})
    db_easy = db.get("easy", {})
    db_index_text = get_str(db_dev, "index_analysis", "[AI_FILL: Index analysis — existing indexes, query benefits, missing index recommendations]")
    db_query_text = get_str(db_dev, "query_patterns", "[AI_FILL: Query patterns — ORM vs raw SQL, transaction usage, bulk operations]")
    db_integration = get_str(db_dev, "backend_integration", "[AI_FILL: Backend integration — connection management, where DB calls live, error handling]")
    db_easy_what = get_str(db_easy, "what_data", "[AI_FILL: What data does the app store — plain-language description of each data type]")
    db_easy_talk = get_str(db_easy, "how_talks", "[AI_FILL: How does the app talk to the database — simple read/write explanation]")
    db_easy_safe = get_str(db_easy, "data_safety", "[AI_FILL: Is the data safe — plain-language data integrity explanation]")

    # Security
    sec_dev = sec.get("dev", {})
    sec_easy = sec.get("easy", {})
    sec_auth_text = get_str(sec_dev, "auth_analysis", "[AI_FILL: Authentication analysis — JWT/session patterns, secret management, token expiry, role checks]")
    sec_validation = get_str(sec_dev, "input_validation", "[AI_FILL: Input validation audit — what inputs are validated, what are not, injection risk areas]")
    sec_deps = get_str(sec_dev, "dependency_risk", "[AI_FILL: Dependency risk — known CVEs or risky patterns in third-party packages]")
    sec_scale = get_str(sec_dev, "scalability", "[AI_FILL: Scalability analysis — bottlenecks, horizontal vs vertical readiness, connection pooling]")
    high_count = sec_dev.get("high_count", 2)
    med_count = sec_dev.get("medium_count", 2)
    low_count = sec_dev.get("low_count", 1)

    sec_easy_safe = get_str(sec_easy, "is_safe", "[AI_FILL: Is the app safe — traffic-light rating with one-sentence verdict]")
    sec_easy_safe_color = get_str(sec_easy, "safety_color", "yellow")
    sec_easy_attention = get_str(sec_easy, "needs_attention", "[AI_FILL: What needs attention — plain-language risk descriptions]")
    sec_easy_access = get_str(sec_easy, "access_control", "[AI_FILL: Who can access what — simplified auth explanation]")
    sec_easy_growth = get_str(sec_easy, "growth", "[AI_FILL: Can the app handle growth — plain-language scalability assessment]")

    # Suggestions
    sug_dev = sug.get("dev", {})
    sug_easy = sug.get("easy", {})
    sug_product = render_cards(get_list(sug_dev, "product"))
    sug_technical = render_cards(get_list(sug_dev, "technical"))
    sug_security = render_cards(get_list(sug_dev, "security"))
    sug_roadmap = get_list(sug_dev, "scalability_roadmap")
    sug_priority = get_list(sug_dev, "priority_matrix")
    sug_easy_product = get_str(sug_easy, "product", "[AI_FILL: How to make the product better — plain-language improvement ideas]")
    sug_easy_code = get_str(sug_easy, "code", "[AI_FILL: How to make the code stronger — simplified technical suggestions]")
    sug_easy_safer = get_str(sug_easy, "security", "[AI_FILL: How to make it safer — non-jargon security improvements]")
    sug_easy_growth = get_str(sug_easy, "growth", "[AI_FILL: How to handle more users — growth readiness in plain language]")
    sug_easy_first = render_priority_items(get_list(sug_easy, "priorities"))

    # Pitch
    pitch_dev = pitch.get("dev", {})
    pitch_easy = pitch.get("easy", {})
    pitch_elevator = get_str(pitch_dev, "elevator_pitch", "[AI_FILL: Technical elevator pitch — 3-4 sentences about tech stack, architecture, key strengths]")
    pitch_strengths = get_list(pitch_dev, "strengths")
    pitch_stack = get_str(pitch_dev, "tech_stack_justification", "[AI_FILL: Tech stack justification — why these technologies make sense for the use case]")
    pitch_integration = get_str(pitch_dev, "integration_narrative", "[AI_FILL: Integration narrative — how this project fits into or extends a larger ecosystem]")
    pitch_numbers = get_list(pitch_dev, "by_the_numbers")

    pitch_easy_story = get_str(pitch_easy, "story", "[AI_FILL: Tell your story — ready-to-use narrative paragraph about this specific project]")
    pitch_easy_oneliner = get_str(pitch_easy, "one_liner", "[AI_FILL: The one-liner — single sentence value proposition]")
    pitch_easy_audience = get_str(pitch_easy, "audience", "[AI_FILL: Who is this for — target audience in plain terms]")
    pitch_easy_why = get_str(pitch_easy, "why_matters", "[AI_FILL: Why does this matter — impact statement connecting to a real-world problem]")
    pitch_easy_special = get_list(pitch_easy, "differentiators")

    # Simulation
    sim_dev = sim.get("dev", {})
    sim_easy = sim.get("easy", {})
    sim_growth = get_str(sim_dev, "growth_scenario", "[AI_FILL: Growth scenario — what happens at 10x, 100x, 1000x users]")
    sim_expansion = get_str(sim_dev, "feature_expansion", "[AI_FILL: Feature expansion modeling — what adding features would require]")
    sim_failure = get_str(sim_dev, "failure_modes", "[AI_FILL: Failure mode analysis — what breaks first under load]")
    sim_team = get_str(sim_dev, "team_scaling", "[AI_FILL: Team scaling — how codebase supports 2, 5, 10+ developers]")
    sim_evolution = get_str(sim_dev, "architecture_evolution", "[AI_FILL: Architecture evolution path — what to evolve into at each growth stage]")

    sim_easy_takeoff = get_str(sim_easy, "takes_off", "[AI_FILL: What if it takes off — success scenario for thousands of users]")
    sim_easy_next = get_str(sim_easy, "whats_next", "[AI_FILL: What comes next — feature expansion possibilities]")
    sim_easy_pains = get_str(sim_easy, "growing_pains", "[AI_FILL: Growing pains to watch for — plain-language scaling warnings]")
    sim_easy_team_text = get_str(sim_easy, "building_team", "[AI_FILL: Building your team — how the project supports more contributors]")
    sim_easy_big = get_str(sim_easy, "big_picture", "[AI_FILL: The big picture — long-term vision framing]")

    # --- Tab buttons + conditional database -----------------------------
    tab_ids = ["overview", "product", "technical"]
    tab_labels = {"overview": "Overview", "product": "Product", "technical": "Technical"}
    if has_database:
        tab_ids.append("database")
        tab_labels["database"] = "Database"
    tab_ids += ["security", "suggestions", "pitch", "simulation"]
    tab_labels.update({"security": "Security", "suggestions": "Suggestions", "pitch": "Pitch", "simulation": "Simulation"})

    tab_icons = {
        "overview": "📊", "product": "🛍️", "technical": "⚙️", "database": "🗄️",
        "security": "🛡️", "suggestions": "💡", "pitch": "🎤", "simulation": "🔮",
    }

    tab_buttons = ""
    for i, tid in enumerate(tab_ids):
        active = " active" if i == 0 else ""
        tab_buttons += (
            f'<button class="tab-btn{active}" role="tab" data-tab="{tid}" '
            f'onclick="switchTab(\'{tid}\')">{tab_labels[tid]}</button>\n'
        )

    # Keyboard shortcut map
    key_map_js = ", ".join(f"'{i+1}': '{tid}'" for i, tid in enumerate(tab_ids))

    # --- Summary cards for Overview lower half --------------------------
    summary_card_tabs = [t for t in tab_ids if t != "overview"]
    summary_cards_html = ""
    for tid in summary_card_tabs:
        summary_text = tab_summaries.get(tid, f"[AI_FILL: {tab_labels[tid]} tab summary — 1-2 sentence highlight finding]")
        summary_cards_html += (
            f'<article class="card summary-link-card" onclick="switchTab(\'{tid}\')" data-searchable>'
            f'<div class="card-icon">{tab_icons.get(tid, "📋")}</div>'
            f'<div class="card-title">{tab_labels[tid]}</div>'
            f'<div class="card-desc">{esc(summary_text)}</div>'
            f'<span class="card-link">View details →</span>'
            f'</article>\n'
        )

    # --- Roadmap rendering ----------------------------------------------
    roadmap_html = ""
    for i, step in enumerate(sug_roadmap):
        if isinstance(step, str):
            roadmap_html += f'<div data-searchable style="margin:6px 0"><strong>{i+1}.</strong> {esc(step)}</div>'
        elif isinstance(step, dict):
            roadmap_html += f'<div data-searchable style="margin:6px 0"><strong>{i+1}.</strong> {esc(step.get("text",""))}</div>'

    # --- Strengths, numbers, differentiators ----------------------------
    strengths_html = "".join(f"<li data-searchable>{esc(s)}</li>" for s in pitch_strengths)
    numbers_html = "".join(
        f'<div class="metric-card" data-searchable><div class="card-value">{esc(n.get("value",""))}</div>'
        f'<div class="card-label">{esc(n.get("label",""))}</div></div>'
        for n in pitch_numbers if isinstance(n, dict)
    )
    diff_html = "".join(f"<li data-searchable>{esc(d)}</li>" for d in pitch_easy_special)
    health_html = ""
    for h in tech_easy_health_items:
        if isinstance(h, dict):
            color = h.get("color", "yellow")
            label = h.get("label", "")
            desc = h.get("description", "")
            health_html += (
                f'<div style="margin:8px 0" data-searchable>'
                f'<span class="traffic-light traffic-{color}">{esc(label)}</span> '
                f'{esc(desc)}</div>'
            )

    # --- Build the full HTML document -----------------------------------
    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<meta name="generator" content="code-visualizer (SKILL.md)" />
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
        {tab_buttons}
      </div>
      <div class="mode-toggle" role="group" aria-label="Audience mode">
        <button id="modeDev" class="active" onclick="setMode('dev')">Developer</button>
        <button id="modeEasy" onclick="setMode('easy')">Easy</button>
      </div>
      <div class="search-box">
        <input type="text" id="searchInput" placeholder="Search... ( / )" aria-label="Search visualization" oninput="handleSearch(this.value)" />
      </div>
    </div>

    <!-- ============================================================= -->
    <!-- TAB 1: OVERVIEW (no mode split)                                -->
    <!-- ============================================================= -->
    <section class="tab-panel active" id="panel-overview" role="tabpanel">
      <div class="breadcrumb"><span>{esc(project)}</span><span class="breadcrumb-sep">/</span><span>Overview</span></div>

      <div class="hero">
        <div class="hero-content">
          <span class="hero-eyebrow">Tropical Code Cartography</span>
          <h1>{esc(project)} Architecture Map
            <button class="tooltip-trigger" type="button"
              data-tooltip="Use tabs to change view, press / to search, 1-{len(tab_ids)} to jump between tabs."
              aria-label="How to use this visualization">?</button>
          </h1>
          <p data-searchable class="hero-lede">{esc(project_summary)}</p>
          <div class="hero-meta">
            <span class="chip"><strong>{files_count}</strong> files</span>
            <span class="chip"><strong>{lines_count}</strong> LOC</span>
            <span class="chip"><strong>{len(deps)}</strong> deps</span>
            <span class="chip"><strong>{symbols_count}</strong> symbols</span>
          </div>
        </div>
        <div class="hero-art">{HERO_PINEAPPLE_SVG}</div>
        <svg class="hero-leaf one" viewBox="0 0 120 180" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
          <path d="M 60 175 Q 40 100 20 10 Q 70 90 62 170 Z" fill="#4CAF50"/>
          <path d="M 62 170 Q 70 80 65 10 Q 80 100 70 170 Z" fill="#2E7D32" opacity="0.9"/>
        </svg>
        <svg class="hero-leaf two" viewBox="0 0 120 180" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
          <path d="M 60 175 Q 80 90 100 20 Q 55 100 62 170 Z" fill="#66BB6A"/>
          <path d="M 62 170 Q 55 90 55 20 Q 40 100 52 170 Z" fill="#2E7D32" opacity="0.85"/>
        </svg>
      </div>

      <div class="metrics-row">
        <div class="metric-card" data-searchable><div class="card-title">Files</div><div class="card-value">{files_count}</div><div class="card-label">scanned files</div></div>
        <div class="metric-card" data-searchable><div class="card-title">Lines</div><div class="card-value">{lines_count}</div><div class="card-label">total LOC</div></div>
        <div class="metric-card" data-searchable><div class="card-title">Dependencies</div><div class="card-value">{len(deps)}</div><div class="card-label">external packages</div></div>
        <div class="metric-card" data-searchable><div class="card-title">Symbols</div><div class="card-value">{symbols_count}</div><div class="card-label">catalogued symbols</div></div>
      </div>

      <h2>Language Breakdown</h2>
      <div class="lang-bar-container">
        <div class="lang-bar">{segments}</div>
        <div class="lang-legend">{legend}</div>
      </div>

      <h2>Codebase at a Glance</h2>
      <p data-searchable>{esc(project_summary)}</p>
      <div class="summary-grid">
        {summary_cards_html}
      </div>
    </section>

    <!-- ============================================================= -->
    <!-- TAB 2: PRODUCT                                                 -->
    <!-- ============================================================= -->
    <section class="tab-panel" id="panel-product" role="tabpanel">
      <div class="breadcrumb"><span>{esc(project)}</span><span class="breadcrumb-sep">/</span><span>Product</span></div>

      <!-- Developer mode -->
      <div class="dev-only">
        <h2>Feature Map</h2>
        <div class="card-grid">{prod_feature_cards or '<article class="card" data-searchable><p>[AI_FILL: Feature map cards — domain name, modules, endpoints, description for each feature]</p></article>'}</div>

        <h2>User Workflow</h2>
        <div class="diagram-container">
          <pre class="mermaid" data-original="{esc(workflow_mermaid)}">{workflow_mermaid}</pre>
        </div>

        <h2>API Surface</h2>
        <table class="data-table">
          <thead><tr><th>Method</th><th>Path</th><th>Auth</th><th>Description</th></tr></thead>
          <tbody>{prod_api_rows or '<tr><td colspan="4">[AI_FILL: API surface table rows — Method, Path, Auth, Description for each endpoint]</td></tr>'}</tbody>
        </table>

        <h2>Product Architecture</h2>
        <p data-searchable>{esc(prod_arch_text)}</p>

        <h2>Design Patterns</h2>
        <div class="card-grid">{prod_patterns or '<article class="card" data-searchable><p>[AI_FILL: Design patterns — patterns found in the code (RBAC, pagination, rate limiting, etc.)]</p></article>'}</div>
      </div>

      <!-- Easy mode -->
      <div class="easy-only">
        <h2>What does this app do?</h2>
        <p data-searchable>{esc(prod_easy_what)}</p>

        <h2>How do people use it?</h2>
        <div class="diagram-container">
          <pre class="mermaid" data-original="{esc(workflow_mermaid_easy)}">{workflow_mermaid_easy}</pre>
        </div>

        <h2>What can users do?</h2>
        {prod_easy_capabilities or '<p data-searchable>[AI_FILL: Capability checklist — list what users can do]</p>'}

        <h2>How is the app organized?</h2>
        <p data-searchable>{esc(prod_easy_org)}</p>
      </div>

      <h2>Entry Points</h2>
      <ul>{entry_list}</ul>
    </section>

    <!-- ============================================================= -->
    <!-- TAB 3: TECHNICAL                                               -->
    <!-- ============================================================= -->
    <section class="tab-panel" id="panel-technical" role="tabpanel">
      <div class="breadcrumb"><span>{esc(project)}</span><span class="breadcrumb-sep">/</span><span>Technical</span></div>

      <!-- Developer mode -->
      <div class="dev-only">
        <h2>Architecture Diagram</h2>
        <div class="diagram-container">
          <pre class="mermaid" data-original="{esc(arch_mermaid)}">{arch_mermaid}</pre>
        </div>

        <h2>Backend Analysis</h2>
        <p data-searchable>{esc(tech_backend)}</p>

        <h2>Frontend Analysis</h2>
        <p data-searchable>{esc(tech_frontend)}</p>

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

        <h2>Code Quality Signals</h2>
        <div class="card-grid">{tech_quality or '<article class="card" data-searchable><p>[AI_FILL: Code quality signals — file size distribution, largest files, coupling indicators]</p></article>'}</div>
      </div>

      <!-- Easy mode -->
      <div class="easy-only">
        <h2>How is the code built?</h2>
        <p data-searchable>{esc(tech_easy_how)}</p>

        <h2>The main parts</h2>
        <div class="diagram-container">
          <pre class="mermaid" data-original="{esc(arch_mermaid_easy)}">{arch_mermaid_easy}</pre>
        </div>
        <p data-searchable>{esc(tech_easy_parts)}</p>

        <h2>How the parts connect</h2>
        <p data-searchable>{esc(tech_easy_connect)}</p>

        <h2>Code health check</h2>
        {health_html or '<p data-searchable>[AI_FILL: Code health check — traffic-light ratings for organization, complexity, consistency, size]</p>'}
      </div>
    </section>

    <!-- ============================================================= -->
    <!-- TAB 4: DATABASE (conditional)                                  -->
    <!-- ============================================================= -->
    {"" if not has_database else f'''<section class="tab-panel" id="panel-database" role="tabpanel">
      <div class="breadcrumb"><span>{esc(project)}</span><span class="breadcrumb-sep">/</span><span>Database</span></div>

      <!-- Developer mode -->
      <div class="dev-only">
        <h2>Schema Design</h2>
        <div class="diagram-container">
          <pre class="mermaid" data-original="{esc(db_er_mermaid)}">{db_er_mermaid or "erDiagram\\n  SCHEMA ||--|| PENDING : generate"}</pre>
        </div>

        <h2>Index Analysis</h2>
        <p data-searchable>{esc(db_index_text)}</p>

        <h2>Query Patterns</h2>
        <p data-searchable>{esc(db_query_text)}</p>

        <h2>Backend Integration</h2>
        <p data-searchable>{esc(db_integration)}</p>

        {"" if not db_flow_mermaid else f"""<h2>Data Flow</h2>
        <div class="diagram-container">
          <pre class="mermaid" data-original="{esc(db_flow_mermaid)}">{db_flow_mermaid}</pre>
        </div>"""}
      </div>

      <!-- Easy mode -->
      <div class="easy-only">
        <h2>What data does the app store?</h2>
        <p data-searchable>{esc(db_easy_what)}</p>

        <h2>How is data organized?</h2>
        {"" if not db_er_mermaid_easy else f"""<div class="diagram-container">
          <pre class="mermaid" data-original="{esc(db_er_mermaid_easy)}">{db_er_mermaid_easy}</pre>
        </div>"""}

        <h2>How does the app talk to the database?</h2>
        <p data-searchable>{esc(db_easy_talk)}</p>

        <h2>Is the data safe?</h2>
        <p data-searchable>{esc(db_easy_safe)}</p>
      </div>
    </section>'''}

    <!-- ============================================================= -->
    <!-- TAB 5: SECURITY                                                -->
    <!-- ============================================================= -->
    <section class="tab-panel" id="panel-security" role="tabpanel">
      <div class="breadcrumb"><span>{esc(project)}</span><span class="breadcrumb-sep">/</span><span>Security</span></div>

      <!-- Developer mode -->
      <div class="dev-only">
        <h2>Risk Summary</h2>
        <div class="metrics-row">
          <div class="metric-card"><div class="card-title">High</div><div class="card-value">{high_count}</div><div class="card-label">Immediate action</div></div>
          <div class="metric-card"><div class="card-title">Medium</div><div class="card-value">{med_count}</div><div class="card-label">Harden before prod</div></div>
          <div class="metric-card"><div class="card-title">Low</div><div class="card-value">{low_count}</div><div class="card-label">Best-practice gaps</div></div>
        </div>

        <h2>Findings</h2>
        {findings_html}

        <h2>Authentication &amp; Authorization</h2>
        <p data-searchable>{esc(sec_auth_text)}</p>

        <h2>Input Validation Audit</h2>
        <p data-searchable>{esc(sec_validation)}</p>

        <h2>Dependency Risk</h2>
        <p data-searchable>{esc(sec_deps)}</p>

        <h2>Scalability Analysis</h2>
        <p data-searchable>{esc(sec_scale)}</p>
      </div>

      <!-- Easy mode -->
      <div class="easy-only">
        <h2>Is the app safe?</h2>
        <p data-searchable><span class="traffic-light traffic-{sec_easy_safe_color}">{esc(sec_easy_safe)}</span></p>

        <h2>What needs attention?</h2>
        <p data-searchable>{esc(sec_easy_attention)}</p>

        <h2>Who can access what?</h2>
        <p data-searchable>{esc(sec_easy_access)}</p>

        <h2>Can the app handle growth?</h2>
        <p data-searchable>{esc(sec_easy_growth)}</p>
      </div>
    </section>

    <!-- ============================================================= -->
    <!-- TAB 6: SUGGESTIONS                                             -->
    <!-- ============================================================= -->
    <section class="tab-panel" id="panel-suggestions" role="tabpanel">
      <div class="breadcrumb"><span>{esc(project)}</span><span class="breadcrumb-sep">/</span><span>Suggestions</span></div>

      <!-- Developer mode -->
      <div class="dev-only">
        <h2>Product Suggestions</h2>
        <div class="card-grid">{sug_product or '<article class="card" data-searchable><p>[AI_FILL: Product suggestions — feature gaps, missing UX flows, each with title, description, affected files, effort]</p></article>'}</div>

        <h2>Technical Suggestions</h2>
        <div class="card-grid">{sug_technical or '<article class="card" data-searchable><p>[AI_FILL: Technical suggestions — refactoring, architecture improvements, test coverage gaps]</p></article>'}</div>

        <h2>Security Hardening</h2>
        <div class="card-grid">{sug_security or '<article class="card" data-searchable><p>[AI_FILL: Security hardening — specific fixes with file paths and code-level guidance]</p></article>'}</div>

        <h2>Scalability Roadmap</h2>
        {roadmap_html or '<p data-searchable>[AI_FILL: Scalability roadmap — concrete ordered steps]</p>'}

        <h2>Priority Matrix</h2>
        {render_priority_items(sug_priority) or '<p data-searchable>[AI_FILL: Priority matrix — effort-vs-impact ranking]</p>'}
      </div>

      <!-- Easy mode -->
      <div class="easy-only">
        <h2>How to make the product better</h2>
        <p data-searchable>{esc(sug_easy_product)}</p>

        <h2>How to make the code stronger</h2>
        <p data-searchable>{esc(sug_easy_code)}</p>

        <h2>How to make it safer</h2>
        <p data-searchable>{esc(sug_easy_safer)}</p>

        <h2>How to handle more users</h2>
        <p data-searchable>{esc(sug_easy_growth)}</p>

        <h2>What to do first</h2>
        {sug_easy_first or '<p data-searchable>[AI_FILL: What to do first — prioritized action items: Do now / Do soon / Do later]</p>'}
      </div>
    </section>

    <!-- ============================================================= -->
    <!-- TAB 7: PITCH                                                   -->
    <!-- ============================================================= -->
    <section class="tab-panel" id="panel-pitch" role="tabpanel">
      <div class="breadcrumb"><span>{esc(project)}</span><span class="breadcrumb-sep">/</span><span>Pitch</span></div>

      <!-- Developer mode -->
      <div class="dev-only">
        <h2>Technical Elevator Pitch</h2>
        <div class="copyable-block" onclick="navigator.clipboard.writeText(this.innerText)" data-searchable>{esc(pitch_elevator)}</div>

        <h2>Architecture Strengths</h2>
        <ul>{strengths_html or '<li>[AI_FILL: Architecture strengths — bullet list of what the codebase does well]</li>'}</ul>

        <h2>Tech Stack Justification</h2>
        <p data-searchable>{esc(pitch_stack)}</p>

        <h2>Integration Narrative</h2>
        <p data-searchable>{esc(pitch_integration)}</p>

        <h2>By the Numbers</h2>
        <div class="metrics-row">{numbers_html or f'<div class="metric-card" data-searchable><div class="card-value">{files_count}</div><div class="card-label">files</div></div><div class="metric-card" data-searchable><div class="card-value">{lines_count}</div><div class="card-label">LOC</div></div><div class="metric-card" data-searchable><div class="card-value">{symbols_count}</div><div class="card-label">symbols</div></div>'}</div>
      </div>

      <!-- Easy mode -->
      <div class="easy-only">
        <h2>Tell your story</h2>
        <div class="copyable-block" onclick="navigator.clipboard.writeText(this.innerText)" data-searchable>{esc(pitch_easy_story)}</div>

        <h2>The one-liner</h2>
        <div class="copyable-block" onclick="navigator.clipboard.writeText(this.innerText)" data-searchable>{esc(pitch_easy_oneliner)}</div>

        <h2>Who is this for?</h2>
        <p data-searchable>{esc(pitch_easy_audience)}</p>

        <h2>Why does this matter?</h2>
        <p data-searchable>{esc(pitch_easy_why)}</p>

        <h2>What makes it special?</h2>
        <ul>{diff_html or '<li>[AI_FILL: What makes it special — 3-4 differentiators in plain language]</li>'}</ul>
      </div>
    </section>

    <!-- ============================================================= -->
    <!-- TAB 8: SIMULATION                                              -->
    <!-- ============================================================= -->
    <section class="tab-panel" id="panel-simulation" role="tabpanel">
      <div class="breadcrumb"><span>{esc(project)}</span><span class="breadcrumb-sep">/</span><span>Simulation</span></div>

      <!-- Developer mode -->
      <div class="dev-only">
        <h2>Growth Scenario</h2>
        <p data-searchable>{esc(sim_growth)}</p>

        <h2>Feature Expansion Modeling</h2>
        <p data-searchable>{esc(sim_expansion)}</p>

        <h2>Failure Mode Analysis</h2>
        <p data-searchable>{esc(sim_failure)}</p>

        <h2>Team Scaling</h2>
        <p data-searchable>{esc(sim_team)}</p>

        <h2>Architecture Evolution Path</h2>
        <p data-searchable>{esc(sim_evolution)}</p>
      </div>

      <!-- Easy mode -->
      <div class="easy-only">
        <h2>What if it takes off?</h2>
        <p data-searchable>{esc(sim_easy_takeoff)}</p>

        <h2>What comes next?</h2>
        <p data-searchable>{esc(sim_easy_next)}</p>

        <h2>Growing pains to watch for</h2>
        <p data-searchable>{esc(sim_easy_pains)}</p>

        <h2>Building your team</h2>
        <p data-searchable>{esc(sim_easy_team_text)}</p>

        <h2>The big picture</h2>
        <p data-searchable>{esc(sim_easy_big)}</p>
      </div>
    </section>

  </main>
</div>

<script>
  // === MERMAID INIT ===
    mermaid.initialize({{
    startOnLoad: false,
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
  function renderVisibleMermaid(panel) {{
    if (!panel) return;
    const diagrams = Array.from(panel.querySelectorAll('.mermaid')).filter(
      (el) => el.offsetParent !== null
    );
    if (!diagrams.length) return;
    diagrams.forEach((el) => {{
      const src = el.getAttribute('data-original');
      if (src) {{
        el.removeAttribute('data-processed');
        el.textContent = src;
      }}
    }});
    mermaid.run({{ nodes: diagrams }});
  }}
  function switchTab(tabId) {{
    document.querySelectorAll('.tab-btn').forEach((btn) => btn.classList.toggle('active', btn.dataset.tab === tabId));
    document.querySelectorAll('.tab-panel').forEach((panel) => panel.classList.toggle('active', panel.id === 'panel-' + tabId));
    renderVisibleMermaid(document.getElementById('panel-' + tabId));
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
    renderVisibleMermaid(document.querySelector('.tab-panel.active'));
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
    const map = {{ {key_map_js} }};
    if (map[e.key]) {{ switchTab(map[e.key]); return; }}
    if (e.key === '/') {{ e.preventDefault(); document.getElementById('searchInput').focus(); }}
    if (e.key === 'Escape') {{
      const input = document.getElementById('searchInput');
      input.value = '';
      clearSearch();
      input.blur();
    }}
  }});

  renderVisibleMermaid(document.querySelector('.tab-panel.active'));
</script>
</body>
</html>
"""
    output_path.write_text(html_doc)


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Generate HTML code visualization")
    parser.add_argument("analysis", help="Path to codebase-analysis.json")
    parser.add_argument("output", help="Path for the output HTML file")
    parser.add_argument("title", nargs="?", default=None, help="Custom page title")
    parser.add_argument("project_name", nargs="?", default=None, help="Override project name")
    parser.add_argument("--enrichment", default=None, help="Path to enrichment.json from AI Phase 3")
    args = parser.parse_args()

    analysis_path = Path(args.analysis).resolve()
    output_path = Path(args.output).resolve()
    enrichment_path = Path(args.enrichment).resolve() if args.enrichment else None
    generate(analysis_path, output_path, args.title, args.project_name, enrichment_path)
    size_kb = output_path.stat().st_size // 1024
    print(f"generated {output_path} ({size_kb} KB)")


if __name__ == "__main__":
    main()
