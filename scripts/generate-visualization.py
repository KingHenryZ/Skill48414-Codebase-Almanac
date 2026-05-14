#!/usr/bin/env python3
"""
generate-visualization.py

Generate a single self-contained HTML code visualization from an analysis JSON
produced by `scripts/extract-codebase.py`. Follows the contracts in SKILL.md
and visualization-base.css.

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
  /* Batch 6: fancier word treatment for the project name in the
     sidebar. Fraunces display font (matches `.codebase-card-name`),
     non-italic, with a richer green gradient backdrop, a soft inner
     glow, and a thin gold accent bar underneath. The flanking 🍍 / 🌿
     decorations stay removed (batch 5). */
  background:
    radial-gradient(120% 140% at 0% 0%, rgba(255, 215, 0, 0.18) 0%, transparent 65%),
    linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
  color: #FFF9E6 !important;
  font-family: var(--font-heading);
  font-style: normal;
  font-weight: 800;
  font-size: 1.6rem;
  letter-spacing: -0.012em;
  line-height: 1.05;
  padding: 22px 22px 18px;
  border-bottom: 3px solid var(--rind);
  text-shadow:
    0 1px 0 rgba(255, 255, 255, 0.18),
    0 2px 8px rgba(0, 0, 0, 0.28);
  position: relative;
  overflow: hidden;
  text-align: left;
  display: flex;
  align-items: flex-end;
  min-height: 78px;
}
.sidebar-header > span {
  position: relative;
  z-index: 1;
  /* Subtle two-stop gold-cream gradient on the letterforms themselves
     so the word reads brand-y, not just bold. Falls back to the cream
     text colour above when background-clip isn't supported. */
  background: linear-gradient(180deg, #FFFCEC 0%, #FFE9A0 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  filter: drop-shadow(0 2px 6px rgba(0, 0, 0, 0.35));
}
.sidebar-header::before {
  /* Decorative gold accent bar that anchors the word visually. */
  content: "";
  position: absolute;
  left: 22px;
  bottom: 10px;
  width: 38px;
  height: 4px;
  border-radius: 999px;
  background: linear-gradient(90deg, #FFD700 0%, #F4A300 100%);
  box-shadow: 0 1px 0 rgba(0, 0, 0, 0.25);
  z-index: 0;
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
  /* Batch 6: PERFECTLY symmetric vertical padding above + below the tab
     pills. The previous `min-height` rule produced unequal breathing
     room because flex items center inside that min-height while padding
     stayed fixed at 14px (so the bottom always picked up extra slack).
     Removing `min-height` lets the bar size to padding + content only
     so 16px top + 16px bottom renders truly symmetric. */
  padding-top: 16px !important;
  padding-bottom: 16px !important;
  height: auto !important;
  min-height: 0 !important;
  align-items: center !important;
}
.tab-bar { gap: 4px; flex-wrap: wrap; align-items: center; }
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

/* Mode toggle */
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
/* The global h2 decoration adds a pineapple emoji + connector line.
   It is suppressed for h2 elements that already have their own visual
   treatment (the codebase intro card, the seasoning legends, etc.) so
   the decoration doesn't leak in. */
h2:not(.codebase-card-name):not(.no-h2-deco)::before {
  content: "🍍";
  font-size: 0.85em;
  align-self: center;
  filter: drop-shadow(0 2px 3px rgba(92, 58, 26, 0.35));
}
h2:not(.codebase-card-name):not(.no-h2-deco)::after {
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
h2.codebase-card-name { display: block; }

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
/* Batch 4: recommendation block is now a highlighted callout, with the
   body text noticeably larger than the rest of the finding so the
   actionable remediation is the most visible part of each card. */
.finding-recommendation {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 6px 12px;
  align-items: start;
  margin-top: 14px;
  padding: 14px 16px;
  background: linear-gradient(135deg,
    rgba(255, 215, 0, 0.18) 0%,
    rgba(76, 175, 80, 0.10) 100%);
  border: 1.5px solid var(--rind);
  border-left: 5px solid var(--leaf-deep);
  border-radius: 14px;
  color: var(--text-primary);
  box-shadow: 0 4px 12px rgba(244, 163, 0, 0.12);
}
.finding-rec-label {
  font-family: var(--font-heading);
  font-weight: 800;
  font-size: 0.92rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--leaf-deep);
  white-space: nowrap;
  padding-top: 4px;
}
.finding-rec-body {
  /* Batch 5: match the rest of the findings card (`.finding-detail` etc.)
     so the recommendation body doesn't visually dominate the row. The
     callout chrome (label + gradient bg + border) still draws attention. */
  font-family: var(--font-body);
  font-size: 0.95rem;
  line-height: 1.55;
  font-weight: 500;
  color: var(--text-primary);
}
.finding-rec-body .kw {
  background: linear-gradient(180deg, transparent 60%, rgba(255, 215, 0, 0.55) 60%);
}
@media (max-width: 600px) {
  .finding-recommendation { grid-template-columns: 1fr; }
  .finding-rec-label { padding-top: 0; }
}

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

/* === Highlight flash (used when scrolling to a symbol row) === */
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
  /* Batch 6: pineapple owns the WHOLE right side of the hero (~2/3 of
     the hero width), like the original "pineapple-as-hero" iteration,
     while still rendering the entire fruit (crown + body) thanks to
     `object-fit: contain` on the SVG. We slot the container against the
     right edge with very small safe gutters and let the SVG's natural
     aspect ratio keep the crown vertical. */
  position: absolute;
  top: clamp(8px, 1.5%, 24px);
  right: clamp(-12px, 0vw, 16px);
  bottom: clamp(8px, 1.5%, 24px);
  width: clamp(420px, 56%, 760px);
  max-height: calc(100% - clamp(16px, 3%, 48px));
  z-index: 1;
  pointer-events: none;
  transform: rotate(2deg);
  filter: drop-shadow(0 28px 42px rgba(139, 90, 43, 0.34));
  animation: heroFloat 9s ease-in-out infinite;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}
.hero-pineapple {
  width: 100%;
  height: 100%;
  max-height: 100%;
  display: block;
  /* `contain` keeps the entire SVG visible regardless of how big the
     hero-art frame grows — no clipping at any viewport. */
  object-fit: contain;
  object-position: right center;
}
@keyframes heroFloat {
  0%, 100% { transform: rotate(2deg) translateY(0); }
  50%      { transform: rotate(1deg) translateY(-12px); }
}

/* The legacy .hero-leaf decorations are removed in batch 3; rules retained
   below as `display: none` in case any downstream theme still emits them. */
.hero-leaf { display: none !important; }

/* === Evergreen hero block (left of pineapple) ======================
   Batch 4: no boxes. The evergreen title + tagline sit directly on the
   hero background. The legacy `.hero-tbd-block`, `.hero-tbd-tag`, and
   `.hero-tbd-subtitle` classes are kept as a no-op so any downstream
   theme that still emits them does not crash visually. */
.hero-evergreen {
  position: relative;
  background: transparent;
  border: 0;
  padding: 0;
  margin: 0;
}
.hero-evergreen-title {
  font-size: clamp(2rem, 4vw, 3.2rem) !important;
  line-height: 1.04;
  margin: 0 0 14px !important;
  color: var(--leaf-deep);
  text-shadow: 0 2px 0 rgba(255, 255, 255, 0.45);
}
.hero-evergreen-body {
  font-family: var(--font-body);
  font-size: 1rem;
  line-height: 1.55;
  color: var(--text-secondary);
  margin: 0;
  max-width: 56ch;
}
/* Legacy class fallbacks (kept so old rules don't suddenly mismatch). */
.hero-tbd-block { all: unset; display: block; }
.hero-tbd-tag,
.hero-tbd-subtitle { display: none !important; }
.hero-tbd-title {
  font-size: clamp(2rem, 4vw, 3.2rem) !important;
  line-height: 1.02;
  margin: 0 0 10px;
}
.hero-tbd-body {
  font-family: var(--font-body);
  font-size: 1rem;
  line-height: 1.55;
  color: var(--text-secondary);
  margin: 0;
}

/* === Codebase intro card (below hero, codebase-specific name + summary) === */
.codebase-card {
  position: relative;
  margin: 28px auto 32px;
  padding: 4px;
  border-radius: 28px;
  background: linear-gradient(135deg,
    #FFD700 0%,
    #F4A300 35%,
    #4CAF50 75%,
    #2E7D32 100%);
  box-shadow:
    0 18px 38px rgba(244, 163, 0, 0.32),
    0 4px 0 var(--rind);
  isolation: isolate;
}
.codebase-card::before {
  content: "";
  position: absolute;
  inset: -10px;
  border-radius: 36px;
  background: radial-gradient(60% 60% at 50% 50%, rgba(255, 215, 0, 0.45), transparent 70%);
  filter: blur(20px);
  z-index: -1;
  opacity: 0.85;
  pointer-events: none;
}
.codebase-card-inner {
  position: relative;
  padding: 28px 32px;
  border-radius: 24px;
  background:
    radial-gradient(140% 120% at 0% 0%, rgba(255, 249, 230, 0.95), rgba(255, 236, 179, 0.92) 60%, rgba(255, 215, 0, 0.10) 100%);
  overflow: hidden;
}
.codebase-card-inner::after {
  content: "";
  position: absolute;
  inset: 0;
  background-image:
    repeating-linear-gradient(45deg, rgba(139, 90, 43, 0.05) 0 1px, transparent 1px 14px),
    repeating-linear-gradient(-45deg, rgba(139, 90, 43, 0.05) 0 1px, transparent 1px 14px);
  pointer-events: none;
  opacity: 0.5;
}
.codebase-card-eyebrow {
  display: inline-block;
  font-family: var(--font-body);
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.32em;
  text-transform: uppercase;
  color: var(--leaf-deep);
  background: rgba(255, 249, 230, 0.95);
  border: 1.5px solid var(--rind);
  padding: 4px 14px;
  border-radius: 999px;
  margin-bottom: 14px;
  box-shadow: 0 2px 0 var(--rind), 0 4px 12px rgba(244, 163, 0, 0.22);
  position: relative;
}
.codebase-card-name {
  font-family: var(--font-heading);
  font-size: clamp(2.6rem, 5.4vw, 4.2rem) !important;
  line-height: 1.0;
  margin: 0 0 14px !important;
  /* Solid high-contrast tropical color so the title is readable on
     the cream-gradient card background. The previous gradient-text
     trick rendered nearly white because the card background already
     has a gold/cream gradient underneath. */
  color: var(--leaf-deep) !important;
  background: none !important;
  -webkit-text-fill-color: currentColor;
  text-shadow: 0 2px 0 rgba(255, 255, 255, 0.55);
  position: relative;
}
.codebase-card-name::after {
  /* Decorative underline rendered as a sibling block instead of a
     pseudo-element on the heading itself; using ::after on a `display:
     block` heading keeps it inline with the title's flow. */
  content: "";
  display: block;
  margin-top: 12px;
  height: 6px;
  width: min(280px, 38%);
  border-radius: 999px;
  background: linear-gradient(90deg, #FFD700, #F4A300, transparent);
  box-shadow: 0 2px 0 var(--rind);
}
.codebase-card-summary {
  /* Match the h2 / "Explore by Tab" heading font (Fraunces display)
     but at body-paragraph weight + size so the description still reads
     as prose. No italic. */
  font-family: var(--font-heading);
  font-style: normal;
  font-weight: 500;
  font-size: clamp(1.05rem, 1.45vw, 1.22rem);
  line-height: 1.55;
  color: var(--text-primary);
  max-width: 78ch;
  margin: 0;
  position: relative;
}
.summary-grid-lede {
  margin: 0 0 14px;
  color: var(--text-secondary);
  font-size: 0.98rem;
}
@media (max-width: 720px) {
  .codebase-card { margin: 22px 0 26px; }
  .codebase-card-inner { padding: 22px 20px; }
}

@media (max-width: 900px) {
  .hero {
    grid-template-columns: 1fr;
    min-height: auto;
    padding: 36px 28px clamp(280px, 60vw, 360px);
  }
  .hero-art {
    /* Below the text, fully visible, slightly larger so it carries the
       layout when there's nothing to the right. */
    top: auto;
    bottom: 16px;
    right: 50%;
    transform: translateX(50%) rotate(2deg);
    width: clamp(240px, 70vw, 360px);
    max-height: clamp(240px, 60vw, 340px);
  }
  .hero-leaf { display: none; }
}
@media (max-width: 600px) {
  .hero-art {
    width: clamp(200px, 80vw, 300px);
    max-height: clamp(220px, 70vw, 300px);
  }
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
.summary-link-card:focus-visible {
  outline: 3px solid var(--leaf-deep);
  outline-offset: 3px;
}
/* Batch 4: header row puts the icon on the LEFT and the tab name on
   the RIGHT, both vertically centered on the same line. The title uses
   the same display font as the codebase intro card so the Overview
   grid feels like a curated index, not a list of metrics. */
.summary-link-card .summary-link-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 12px;
  padding-bottom: 10px;
  border-bottom: 1.5px dashed rgba(139, 90, 43, 0.32);
}
.summary-link-card .card-icon {
  font-size: 2rem;
  margin: 0;
  flex: none;
  filter: drop-shadow(0 2px 4px rgba(244, 163, 0, 0.35));
}
.summary-link-card .card-title {
  font-family: var(--font-heading) !important;
  font-weight: 700;
  font-size: clamp(1.35rem, 1.8vw, 1.7rem) !important;
  letter-spacing: -0.01em;
  line-height: 1.0;
  margin: 0;
  color: var(--leaf-deep);
  text-align: right;
  text-shadow: 0 1px 0 rgba(255, 255, 255, 0.5);
}
.summary-link-card .card-desc {
  font-size: 0.92rem;
  color: var(--text-secondary);
  line-height: 1.5;
}
.summary-link-card .card-link {
  display: inline-block;
  margin-top: 10px;
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--leaf-deep);
}

/* === Health-status indicators (4-tier scale, batch 3 rename) ========
   Replaces the legacy traffic-light Good/Yellow/Red trio with a four-tier
   Health / Sick / Severe Sick / Death scale that uses the warm pineapple
   palette (leaf / gold / rind / chili-black). Legacy class names
   (.traffic-green / .traffic-yellow / .traffic-red) are aliased so
   existing enrichment payloads (e.g. the Security tab's `safety_color`)
   keep working without churn. */
.traffic-light {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 4px 14px;
  border-radius: 999px;
  font-weight: 700;
  font-size: 0.88rem;
  letter-spacing: 0.02em;
}
.traffic-light::before {
  content: "";
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: currentColor;
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.7);
  flex: none;
}
/* === New 4-tier scale ============================================== */
.traffic-health  { background: #E6F4EA; color: #1B5E20; border: 2px solid #4CAF50; }
.traffic-sick    { background: #FFF8DC; color: #7A4F01; border: 2px solid #F4A300; }
.traffic-severe  { background: #FCE7D2; color: #8B3A0E; border: 2px solid #D9531E; }
.traffic-death   { background: #2B1410; color: #FFE2D6; border: 2px solid #5C1A0F; }
.traffic-death::before { box-shadow: 0 0 0 2px rgba(255, 226, 214, 0.28); }
/* === Legacy aliases (kept for backward-compat) ====================== */
.traffic-green   { background: #E6F4EA; color: #1B5E20; border: 2px solid #4CAF50; }
.traffic-yellow  { background: #FFF8DC; color: #7A4F01; border: 2px solid #F4A300; }
.traffic-red     { background: #FCE7D2; color: #8B3A0E; border: 2px solid #D9531E; }
/* === Health Check legend strip ====================================== */
.health-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 14px;
  padding: 12px 16px;
  margin: 8px 0 18px;
  background: rgba(255, 249, 230, 0.7);
  border: 1.5px dashed var(--rind);
  border-radius: 14px;
  font-size: 0.84rem;
  color: var(--text-secondary);
  align-items: center;
}
.health-legend .health-legend-label {
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 0.72rem;
  color: var(--rind-deep);
  margin-right: 6px;
}
.health-legend .traffic-light { font-size: 0.78rem; padding: 3px 10px; }
.health-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  font-family: var(--font-body);
}
.health-row-desc {
  font-size: 0.98rem;
  line-height: 1.5;
  color: var(--text-primary);
}
/* Safety verdict (Security/General "Is the app safe?") gets a slightly
   bigger pill and verdict text than the Code Health Check rows. */
.safety-verdict {
  margin: 8px 0 18px;
  font-size: 1.08rem;
}
.safety-verdict .traffic-light {
  font-size: 0.96rem;
  padding: 6px 16px;
}
.safety-verdict .health-row-desc {
  font-size: 1.05rem;
  font-weight: 500;
}

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
  /* Batch 5: non-italic body font so the one-liner / story sit visually
     beside the rest of the prose in the tab. The previous italic display
     font made the most-shareable lines feel like pull-quotes, not pitch
     copy. The Pitch panel still bumps up the size + adds its own gold
     spotlight (see `.pitch-oneliner` / `.pitch-story`). */
  font-family: var(--font-body);
  font-style: normal;
  font-size: 1.05rem;
  line-height: 1.65;
  color: var(--text-primary);
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

/* === Boss View pill (Pitch + Simulation, batch 6) ===================
   The Boss View indicator uses the SAME `.panel-header > .mode-toggle`
   pill chrome as the Developer / General toggle on every other tab.
   The only difference is the label inside the active button. There is
   no real toggle — the single button is decorative (disabled at the
   DOM level, but visually identical to the active mode-toggle pill on
   other tabs). The legacy `.boss-view-badge` gold pill from batch 5 is
   removed. */
.mode-toggle.boss-view-toggle > button[disabled] {
  /* Strip the browser's "disabled" greyout so the Boss View pill reads
     like an active mode chip on the other tabs. */
  cursor: default;
  opacity: 1;
  pointer-events: none;
}

/* === Pitch tab (batch 6: page background reverted to default) ====== */
.pitch-panel .pitch-section-title,
.simulation-panel .sim-section-title {
  font-family: var(--font-heading);
  font-size: clamp(1.4rem, 2vw, 1.75rem);
  font-weight: 700;
  margin-top: 1.6em;
  margin-bottom: 0.6em;
  color: var(--leaf-deep);
  letter-spacing: -0.01em;
  display: block;
}
.pitch-panel .pitch-section-title:first-of-type,
.simulation-panel .sim-section-title:first-of-type { margin-top: 8px; }
.pitch-panel .pitch-oneliner-title { color: var(--rind-deep); }

.pitch-panel .pitch-oneliner {
  /* Batch 7: the one-liner becomes the deck's flashy hero line. The
     CARD chrome (gold halo, gold-rind border, leaf-deep shadow) frames
     the sentence; the SENTENCE itself is rendered through
     `.pitch-oneliner-text` with a display-font gradient fill so the
     whole line reads as a marketing headline \u2014 no per-word `**bold**`
     highlights, no `.num` chips. Spans full content width. */
  background:
    radial-gradient(120% 200% at 0% 0%, rgba(255, 215, 0, 0.34), transparent 60%),
    rgba(255, 255, 255, 0.92);
  border: 2.5px solid var(--rind);
  border-left: 6px solid #F4A300;
  box-shadow:
    0 14px 32px rgba(244, 163, 0, 0.32),
    inset 0 1px 0 rgba(255, 255, 255, 0.75);
  color: var(--rind-deep);
  width: 100%;
  box-sizing: border-box;
  padding: 26px 28px;
}
.pitch-panel .pitch-oneliner .pitch-oneliner-line {
  margin: 0;
  width: 100%;
}
.pitch-panel .pitch-oneliner-text {
  /* Flashy display headline treatment for the entire sentence. */
  display: inline;
  font-family: var(--font-heading);
  font-weight: 800;
  font-style: normal;
  font-size: clamp(1.55rem, 2.6vw, 2.35rem);
  line-height: 1.18;
  letter-spacing: -0.012em;
  background:
    linear-gradient(135deg,
      #F4A300 0%,
      #FFD700 35%,
      #F4A300 60%,
      #B26A00 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  filter: drop-shadow(0 2px 0 rgba(255, 255, 255, 0.6))
          drop-shadow(0 6px 18px rgba(244, 163, 0, 0.28));
  /* Cream halo behind the gradient text in case background-clip falls
     back (e.g. very old browsers) so the sentence stays readable. */
  text-shadow: 0 1px 0 rgba(255, 255, 255, 0.35);
}
.pitch-panel .pitch-story {
  background: rgba(255, 255, 255, 0.78);
  border-style: solid;
  border-left: 5px solid var(--leaf-deep);
  width: 100%;
  box-sizing: border-box;
}
/* Batch 7: the one-liner + story render WITHOUT keyword highlights or
   number chips. If any leaked through, neutralize them so the headline
   styling stays the focal point. */
.pitch-panel .pitch-oneliner .kw,
.pitch-panel .pitch-oneliner .num,
.pitch-panel .pitch-story .kw,
.pitch-panel .pitch-story .num {
  font-weight: inherit !important;
  background: none !important;
  color: inherit !important;
  padding: 0 !important;
  border-radius: 0 !important;
  box-shadow: none !important;
  -webkit-text-fill-color: inherit !important;
  font-family: inherit !important;
  letter-spacing: inherit !important;
}

/* Batch 6: Pitch + Simulation prose blocks span the FULL content
   width. Previously the Pitch panel wrapped `prose-bullets` in a
   leaf-tinted card with extra side padding which read like a narrow
   inset \u2014 plus the panel itself had 40px page padding of its own,
   compounding the inset. We strip the inset card chrome and force
   block-level fields to fill the column. */
.pitch-panel ul.prose-bullets,
.pitch-panel p,
.simulation-panel ul.prose-bullets,
.simulation-panel p {
  width: 100%;
  box-sizing: border-box;
  max-width: none;
}

/* === Simulation tab (batch 6) ======================================== */
.sim-takeoff-card {
  /* Batch 6: the rocket is now a BIG faded watermark sitting behind the
     content, not a tiny corner glyph. Padding starts from the LEFT so
     the bullets/paragraphs span the full content width from the left
     edge. */
  position: relative;
  background:
    radial-gradient(120% 120% at 0% 0%, rgba(255, 215, 0, 0.22), transparent 60%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.85), rgba(255, 249, 230, 0.78));
  border: 2px solid var(--rind);
  border-left: 6px solid #F4A300;
  border-radius: 22px;
  padding: 26px 28px;
  box-shadow:
    0 10px 24px rgba(244, 163, 0, 0.18),
    inset 0 1px 0 rgba(255, 255, 255, 0.7);
  margin-bottom: 18px;
  overflow: hidden;
  isolation: isolate;
}
.sim-takeoff-card::before {
  /* Giant rocket watermark behind the content, low opacity so the
     prose stays readable. Aligned to the left edge so the rocket fills
     the empty space without pushing the text right. */
  content: "\U0001f680";
  position: absolute;
  top: 50%;
  left: clamp(-30px, -2vw, 8px);
  transform: translateY(-50%) rotate(-12deg);
  font-size: clamp(220px, 28vw, 360px);
  line-height: 1;
  opacity: 0.08;
  pointer-events: none;
  z-index: 0;
  filter: drop-shadow(0 14px 28px rgba(244, 163, 0, 0.25));
}
.sim-takeoff-card > * {
  position: relative;
  z-index: 1;
}
.sim-takeoff-card ul.prose-bullets {
  margin: 0;
  padding-left: 22px;
  width: 100%;
  box-sizing: border-box;
}
.sim-takeoff-card p { margin: 0; }

.sim-next-grid {
  margin-top: 4px;
  margin-bottom: 22px;
}
.sim-next-grid .card .card-title {
  font-family: var(--font-heading);
  font-weight: 700;
  font-size: clamp(1.12rem, 1.5vw, 1.32rem);
  color: var(--leaf-deep);
  margin-bottom: 10px;
}
.simulation-panel .big-picture-stepper {
  /* Lightly tinted backdrop so the stepper stands apart from the rest
     of the tab without introducing a full-page background tint. */
  background: rgba(255, 255, 255, 0.4);
  padding: 18px 8px 22px;
  border-radius: 18px;
  border: 1.5px dashed rgba(76, 175, 80, 0.3);
}
.simulation-panel .big-picture-stepper .roadmap-medallion {
  background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
  color: #FFF9E6;
  border-color: #1B5E20;
}
.simulation-panel .big-picture-stepper .roadmap-when {
  background: rgba(244, 163, 0, 0.15);
  color: var(--rind-deep);
  border-color: var(--rind);
}
/* Batch 6: inside "The big picture" stepper ONLY, render `**bold**`
   keyword highlights as plain underlined text \u2014 no bold weight, no
   yellow highlight bar. Keeps the stepper visually quieter. */
.simulation-panel .big-picture-stepper .kw {
  font-weight: 400 !important;
  background: none !important;
  color: inherit !important;
  text-decoration: underline;
  text-decoration-color: rgba(46, 125, 50, 0.45);
  text-decoration-thickness: 1.5px;
  text-underline-offset: 3px;
  padding: 0 !important;
}

/* === Panel header (in-panel mode toggle, replaces breadcrumb) ====== */
.panel-header {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 12px;
  margin: -4px 0 18px;
}
.panel-header .mode-toggle {
  display: inline-flex;
  gap: 4px;
  padding: 4px;
  border-radius: 999px;
  background: rgba(255, 249, 230, 0.92);
  border: 1.5px dashed var(--rind);
  box-shadow: 0 3px 10px rgba(244, 163, 0, 0.2);
}
.panel-header .mode-toggle button {
  border: 0;
  background: transparent;
  font-family: var(--font-body);
  font-weight: 700;
  font-size: 0.86rem;
  letter-spacing: 0.04em;
  color: var(--text-muted);
  padding: 6px 16px;
  border-radius: 999px;
  cursor: pointer;
  transition: background 160ms ease, color 160ms ease, transform 160ms ease;
}
.panel-header .mode-toggle button.active {
  background: linear-gradient(135deg, #FFD700 0%, #F4A300 100%);
  color: #3B2A0A;
  box-shadow: 0 2px 0 var(--rind), 0 6px 14px rgba(244, 163, 0, 0.32);
}
.panel-header .mode-toggle button:hover { transform: translateY(-1px); }
.panel-header .mode-toggle button:focus-visible {
  outline: 3px solid rgba(76, 175, 80, 0.5);
  outline-offset: 2px;
}
@media (max-width: 480px) {
  .panel-header .mode-toggle button { padding: 5px 12px; font-size: 0.78rem; }
}

/* === Inline emphasis used by emphasize() ============================ */
/* Important words/phrases marked **like this** in the JSON. */
.kw {
  color: var(--rind-deep);
  font-weight: 700;
  background: linear-gradient(180deg,
              rgba(255, 255, 255, 0) 55%,
              rgba(255, 215, 0, 0.55) 55%,
              rgba(255, 215, 0, 0.55) 92%,
              rgba(255, 255, 255, 0) 92%);
  padding: 0 3px;
  border-radius: 3px;
  box-decoration-break: clone;
  -webkit-box-decoration-break: clone;
}
/* Auto-emphasized numeric tokens. */
.num {
  font-family: var(--font-heading);
  font-weight: 700;
  color: var(--leaf-deep);
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.5px;
}

/* === Pineapple Seasoning Score (effort chips) ====================== */
.seasoning-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px 4px 10px;
  border-radius: 999px;
  border: 1.5px solid var(--rind);
  background: rgba(255, 249, 230, 0.92);
  font-family: var(--font-body);
  font-weight: 700;
  font-size: 0.78rem;
  letter-spacing: 0.04em;
  color: var(--text-primary);
  box-shadow: 0 2px 6px rgba(244, 163, 0, 0.22);
  white-space: nowrap;
  vertical-align: middle;
}
.seasoning-chip .seasoning-glyph {
  font-size: 0.95rem;
  filter: drop-shadow(0 1px 2px rgba(244, 163, 0, 0.35));
  letter-spacing: -1px;
}
/* Batch 5: glyph-only chips (used everywhere except the legend) shrink
   the padding and bump the emoji size since the descriptive label is
   gone. Hovering the chip reveals the title attribute. */
.seasoning-chip.seasoning-glyph-only {
  padding: 3px 8px;
  gap: 0;
}
.seasoning-chip.seasoning-glyph-only .seasoning-glyph {
  font-size: 1.05rem;
}
.seasoning-chip.seasoning-1 {
  background: linear-gradient(135deg, #FFF8DC 0%, #FFECB3 100%);
  border-color: #F4A300;
}
.seasoning-chip.seasoning-2 {
  background: linear-gradient(135deg, #FFE082 0%, #FFCA28 100%);
  border-color: #B26A00;
  color: #4A2C00;
}
.seasoning-chip.seasoning-3 {
  background: linear-gradient(135deg, #FFB300 0%, #D9531E 100%);
  border-color: #8B1A0E;
  color: #FFF8DC;
  text-shadow: 0 1px 0 rgba(0, 0, 0, 0.35);
}

.seasoning-legend {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px 14px;
  padding: 12px 16px;
  margin: 8px 0 18px;
  background: rgba(255, 249, 230, 0.7);
  border: 1.5px dashed var(--rind);
  border-radius: 14px;
  font-size: 0.84rem;
  color: var(--text-secondary);
}
.seasoning-legend .seasoning-legend-label {
  font-family: var(--font-heading);
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 0.74rem;
  color: var(--rind-deep);
  margin-right: 4px;
}

/* === Suggestion / Priority cards: bigger title, seasoning treatment === */
.suggestions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 18px;
  margin: 8px 0 24px;
}
.suggestions-grid .card .card-title {
  font-family: var(--font-heading);
  font-weight: 700;
  font-size: clamp(1.18rem, 1.6vw, 1.42rem);
  line-height: 1.15;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 10px;
  color: var(--leaf-deep);
}

/* === Priority Matrix (batch 5: plain bullet list) ==================== */
.priority-matrix {
  list-style: none;
  display: grid;
  gap: 10px;
  margin: 8px 0 18px;
  padding: 0;
}
.priority-matrix .priority-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 16px 12px 18px;
  background: rgba(255, 249, 230, 0.55);
  border: 1.5px solid rgba(139, 90, 43, 0.18);
  border-left: 5px solid var(--rind);
  border-radius: 12px;
}
.priority-matrix .priority-row::before {
  content: "\U0001f34d";
  font-size: 0.95rem;
  line-height: 1.55;
  flex: none;
  filter: drop-shadow(0 1px 2px rgba(244, 163, 0, 0.3));
}
.priority-matrix .priority-row .priority-text {
  font-size: 1rem;
  line-height: 1.55;
  color: var(--text-primary);
  flex: 1 1 auto;
}

/* === Scalability Roadmap (horizontal connected stepper) ============== */
.scalability-roadmap {
  list-style: none;
  margin: 8px 0 28px;
  /* Batch 5: bumped vertical padding so the parent's overflow context
     never clips overhanging children (the medallion is now fully INSIDE
     each node so this is just a safety belt). */
  padding: 14px 4px 18px;
  display: flex;
  flex-wrap: nowrap;
  gap: 0;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scroll-snap-type: x proximity;
  counter-reset: roadmap-counter;
}
.scalability-roadmap .roadmap-node {
  position: relative;
  flex: 1 0 220px;
  min-width: 220px;
  max-width: 280px;
  /* Batch 5: medallion now sits FULLY INSIDE the node (top: 14px), so
     the node padding-top is sized to give it room without negative
     overflow getting clipped by the parent's `overflow-x: auto`. */
  padding: 70px 18px 18px;
  margin: 0 32px 0 0;
  background: rgba(255, 249, 230, 0.92);
  border: 2px solid var(--rind);
  border-radius: 18px;
  box-shadow:
    0 8px 18px rgba(139, 90, 43, 0.22),
    inset 0 1px 0 rgba(255, 255, 255, 0.7);
  scroll-snap-align: start;
  display: flex;
  flex-direction: column;
  gap: 6px;
  isolation: isolate;
}
.scalability-roadmap .roadmap-node:last-child { margin-right: 0; }
.scalability-roadmap .roadmap-node::after {
  /* Arrow connector to the NEXT node (skipped on the last one). */
  content: "";
  position: absolute;
  top: 50%;
  right: -28px;
  width: 28px;
  height: 4px;
  background: linear-gradient(90deg, var(--rind), #F4A300);
  border-radius: 2px;
  transform: translateY(-50%);
}
.scalability-roadmap .roadmap-node:last-child::after { display: none; }
.scalability-roadmap .roadmap-node::before {
  content: "";
  position: absolute;
  top: 50%;
  right: -34px;
  width: 0; height: 0;
  border-top: 8px solid transparent;
  border-bottom: 8px solid transparent;
  border-left: 12px solid #F4A300;
  transform: translateY(-50%);
}
.scalability-roadmap .roadmap-node:last-child::before { display: none; }
.scalability-roadmap .roadmap-medallion {
  /* Batch 5: medallion now sits fully INSIDE the node so the top of the
     numbered circle is never clipped by the parent's overflow context. */
  position: absolute;
  top: 14px;
  left: 18px;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: linear-gradient(135deg, #FFD700 0%, #F4A300 100%);
  border: 2.5px solid var(--rind);
  color: #3B2A0A;
  font-family: var(--font-heading);
  font-weight: 900;
  font-size: 1.4rem;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6px 14px rgba(244, 163, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.6);
}
.scalability-roadmap .roadmap-when {
  display: inline-block;
  align-self: flex-start;
  padding: 3px 10px;
  border-radius: 999px;
  font-family: var(--font-body);
  font-weight: 800;
  font-size: 0.72rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  background: rgba(76, 175, 80, 0.15);
  color: var(--leaf-deep);
  border: 1px dashed var(--leaf-deep);
}
.scalability-roadmap .roadmap-title {
  font-family: var(--font-heading);
  font-weight: 700;
  font-size: 1.05rem;
  line-height: 1.3;
  color: var(--leaf-deep);
}
.scalability-roadmap .roadmap-text {
  font-size: 0.92rem;
  line-height: 1.45;
  color: var(--text-secondary);
}
.scalability-roadmap .roadmap-effort {
  margin-top: auto;
  align-self: flex-start;
}
.scalability-roadmap .roadmap-now    { background: linear-gradient(180deg, #FFF9E6, #FFECB3); }
.scalability-roadmap .roadmap-next   { background: linear-gradient(180deg, #FFF9E6, #FCE7D2); }
.scalability-roadmap .roadmap-later  { background: linear-gradient(180deg, #FFF9E6, #E6F4EA); }
.scalability-roadmap .roadmap-future { background: linear-gradient(180deg, #FFF9E6, #E0E7FF); }
@media (max-width: 600px) {
  .scalability-roadmap { flex-wrap: wrap; }
  .scalability-roadmap .roadmap-node {
    flex-basis: 100%;
    max-width: 100%;
    margin: 0 0 36px 0;
  }
  .scalability-roadmap .roadmap-node::after,
  .scalability-roadmap .roadmap-node::before { display: none; }
}

/* === Bullet-style cards (e.g. Feature Map) ========================= */
.card-bullets {
  list-style: none;
  padding: 0;
  margin: 8px 0 0;
  display: grid;
  gap: 6px;
}
.card-bullets li {
  position: relative;
  padding: 4px 4px 4px 22px;
  font-size: 0.95rem;
  line-height: 1.45;
  color: var(--text-primary);
  border-radius: 6px;
}
.card-bullets li::before {
  content: "";
  position: absolute;
  left: 4px;
  top: 14px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: linear-gradient(135deg, #FFD700 0%, #F4A300 100%);
  border: 1.5px solid var(--rind);
  box-shadow: 0 1px 0 rgba(139, 90, 43, 0.25);
}
.card-bullets li:hover {
  background: rgba(255, 236, 179, 0.55);
}
.card-desc { margin: 4px 0 0; }
.card-loc {
  margin-top: 8px;
  font-size: 0.82rem;
  color: var(--text-muted);
}
.card-loc code { word-break: break-all; }

/* Bullet list outside cards (e.g. Product Architecture). */
.prose-bullets {
  list-style: none;
  padding: 0;
  margin: 12px 0 4px;
  display: grid;
  gap: 8px;
  max-width: 78ch;
}
.prose-bullets li {
  position: relative;
  padding: 6px 6px 6px 26px;
  font-size: 1rem;
  line-height: 1.55;
  border-left: 3px solid transparent;
}
.prose-bullets li::before {
  content: "";
  position: absolute;
  left: 6px;
  top: 13px;
  width: 10px;
  height: 10px;
  border-radius: 2px;
  background: linear-gradient(135deg, #FFD700 0%, #F4A300 100%);
  border: 1.5px solid var(--rind);
  transform: rotate(45deg);
}

/* === Security Risk Summary cards =================================== */
.risk-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 18px;
  margin: 8px 0 28px;
}
.risk-card {
  position: relative;
  padding: 22px 22px 20px;
  border-radius: 22px;
  background: rgba(255, 249, 230, 0.92);
  border: 2.5px solid var(--rind);
  box-shadow:
    0 12px 28px rgba(139, 90, 43, 0.22),
    inset 0 1px 0 rgba(255, 255, 255, 0.7);
  isolation: isolate;
  overflow: hidden;
  text-align: left;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.risk-card::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: -1;
  background:
    radial-gradient(140% 90% at 100% 0%, var(--risk-tint, transparent), transparent 70%),
    repeating-linear-gradient(45deg, rgba(139, 90, 43, 0.05) 0 1px, transparent 1px 14px);
  opacity: 0.95;
}
.risk-card::after {
  content: "";
  position: absolute;
  left: 0; right: 0; top: 0;
  height: 5px;
  border-radius: 22px 22px 0 0;
  background: var(--risk-bar, linear-gradient(90deg, #FFD700, #F4A300));
  box-shadow: 0 1px 0 var(--rind);
}
.risk-card-glyph {
  font-size: 1.6rem;
  filter: drop-shadow(0 2px 4px rgba(244, 163, 0, 0.3));
}
.risk-card-tier {
  font-family: var(--font-body);
  font-weight: 800;
  font-size: 0.78rem;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--risk-text, var(--leaf-deep));
  margin-top: 4px;
}
.risk-card-count {
  font-family: var(--font-heading);
  font-weight: 900;
  font-size: clamp(2.6rem, 4.8vw, 3.8rem);
  line-height: 1;
  margin-top: 2px;
  color: var(--risk-text, var(--leaf-deep));
  text-shadow: 0 2px 0 rgba(255, 255, 255, 0.55);
  font-variant-numeric: tabular-nums;
}
.risk-card-label {
  font-family: var(--font-body);
  font-size: 0.92rem;
  color: var(--text-secondary);
  margin-top: 6px;
}
.risk-card.risk-high   {
  --risk-bar: linear-gradient(90deg, #B71C1C, #D9531E);
  --risk-text: #8B1A0E;
  --risk-tint: rgba(217, 83, 30, 0.25);
  border-color: #B71C1C;
}
.risk-card.risk-medium {
  --risk-bar: linear-gradient(90deg, #F4A300, #FFD700);
  --risk-text: #7A4F01;
  --risk-tint: rgba(244, 163, 0, 0.22);
  border-color: var(--rind);
}
.risk-card.risk-low    {
  --risk-bar: linear-gradient(90deg, #4CAF50, #81C784);
  --risk-text: #1B5E20;
  --risk-tint: rgba(76, 175, 80, 0.22);
  border-color: var(--leaf-deep);
}

/* === Findings card responsiveness =================================== */
.finding {
  padding: 18px 20px;
  margin: 12px 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.finding-header {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.finding-title { word-break: break-word; }
.finding-location {
  font-family: var(--font-code);
  font-size: 0.86rem;
  word-break: break-all;
  overflow-wrap: anywhere;
}
.finding-detail { color: var(--text-secondary); font-size: 0.95rem; }
.finding-recommendation { word-break: break-word; overflow-wrap: anywhere; }
.finding-empty { color: var(--text-muted); font-style: italic; }

/* === Diagram container: responsive Mermaid ========================== */
.diagram-container {
  max-width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  text-align: center;
}
.diagram-container .mermaid {
  display: block;
  min-width: 0;
  margin: 0 auto;
}
/* Mermaid is configured with useMaxWidth:false (see mermaid.initialize),
   so every SVG renders at its NATURAL pixel size. We cap it to the
   container width to keep things responsive; small diagrams DO NOT get
   stretched up, which keeps their internal fontSize consistent across
   the whole document (architecture, dep graph, ER, easy-mode "main parts"
   all read at the same baseline). */
.diagram-container .mermaid svg {
  max-width: 100% !important;
  height: auto !important;
  display: inline-block;
  margin: 0 auto;
}
/* Belt-and-suspenders: clamp Mermaid text nodes to the same baseline
   so flowchart / er / sequence diagrams all read consistently. */
.diagram-container .mermaid svg text,
.diagram-container .mermaid svg .nodeLabel,
.diagram-container .mermaid svg .edgeLabel,
.diagram-container .mermaid svg .label,
.diagram-container .mermaid svg foreignObject div {
  font-size: 14px !important;
  font-family: "DM Sans", Inter, system-ui, sans-serif !important;
}
.diagram-container .mermaid svg .entityBox text,
.diagram-container .mermaid svg .er .entityLabel,
.diagram-container .mermaid svg .er .relationshipLabel,
.diagram-container .mermaid svg .er .attributeBoxOdd text,
.diagram-container .mermaid svg .er .attributeBoxEven text {
  font-size: 13px !important;
}

/* === Summary grid responsive =======================================  */
@media (max-width: 768px) {
  .summary-grid { grid-template-columns: 1fr; }
  .summary-link-card { padding: 16px; }
  .finding { padding: 14px 16px; }
  .diagram-container { padding: 12px; }
}
@media (max-width: 480px) {
  .finding-header { flex-direction: column; align-items: flex-start; }
}

/* === Persistent credits (bottom-left, always visible) =============== */
.credits {
  position: fixed;
  left: 14px;
  bottom: 14px;
  z-index: 600;
  /* Batch 3: darker glassy background so the page behind shows through.
     Uses a deep rind/leaf-tinted layer at low opacity instead of the old
     near-opaque cream. Border tinted to match. */
  background: rgba(33, 22, 8, 0.42);
  border: 1.5px solid rgba(255, 215, 0, 0.55);
  border-radius: 14px;
  padding: 10px 14px;
  font-family: var(--font-body);
  font-size: 0.78rem;
  line-height: 1.5;
  color: rgba(255, 249, 230, 0.95);
  box-shadow:
    0 8px 22px rgba(0, 0, 0, 0.32),
    inset 0 1px 0 rgba(255, 255, 255, 0.18);
  backdrop-filter: blur(8px) saturate(1.1);
  -webkit-backdrop-filter: blur(8px) saturate(1.1);
  pointer-events: auto;
  max-width: min(280px, 64vw);
}
.credits .credits-line {
  display: flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
}
.credits .credits-team { color: rgba(255, 249, 230, 0.92); font-weight: 600; }
.credits .credits-team strong {
  color: #FFD700;
  font-family: var(--font-heading);
  text-shadow: 0 1px 0 rgba(0, 0, 0, 0.4);
}
.credits .credits-handle {
  font-family: var(--font-code);
  color: #FFECB3;
  font-weight: 600;
}
.credits .credits-year {
  color: rgba(255, 249, 230, 0.6);
  font-variant-numeric: tabular-nums;
  letter-spacing: 1px;
}
.credits .credits-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border-radius: 4px;
  background: rgba(10, 102, 194, 0.95); /* LinkedIn brand-ish, slightly muted */
  color: #FFFFFF;
  text-decoration: none;
  transition: transform 160ms ease, background 160ms ease, box-shadow 160ms ease;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.35);
}
.credits .credits-link:hover {
  transform: translateY(-1px) scale(1.06);
  background: #0A66C2;
  box-shadow: 0 3px 10px rgba(10, 102, 194, 0.6);
}
.credits .credits-link:focus-visible {
  outline: 2px solid #FFD700;
  outline-offset: 2px;
}
.credits .credits-link svg {
  width: 12px;
  height: 12px;
  fill: currentColor;
}
@media (max-width: 768px) {
  .credits {
    left: 8px;
    bottom: 8px;
    padding: 6px 10px;
    font-size: 0.72rem;
    border-radius: 12px;
    max-width: min(240px, 72vw);
  }
}
@media (max-width: 420px) {
  .credits {
    font-size: 0.68rem;
    padding: 5px 8px;
    border-width: 1.5px;
  }
}
@media print {
  .credits {
    position: static;
    box-shadow: none;
    background: rgba(0, 0, 0, 0.04);
    color: var(--text-secondary);
    border-color: var(--border-color);
  }
  .credits .credits-link { display: none; }
}
"""


# ── Hero illustration: 3D pineapple in SVG ─────────────────────────────
# All crown leaves attach to a single point at (320, 360) on the body's
# upper rim. There are no decorative leaves floating outside the fruit.
HERO_PINEAPPLE_SVG = """\
<svg class="hero-pineapple" viewBox="0 0 640 920" xmlns="http://www.w3.org/2000/svg"
     role="img" aria-hidden="true" preserveAspectRatio="xMidYMid meet">
  <defs>
    <!-- 3D body: warm sunlit top → deep amber underbelly -->
    <radialGradient id="body3d" cx="38%" cy="32%" r="78%">
      <stop offset="0%"   stop-color="#FFF6B8"/>
      <stop offset="22%"  stop-color="#FFE066"/>
      <stop offset="55%"  stop-color="#F4A300"/>
      <stop offset="85%"  stop-color="#B07415"/>
      <stop offset="100%" stop-color="#6B4408"/>
    </radialGradient>
    <linearGradient id="body-rim" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%"   stop-color="#FFF3B0" stop-opacity="0.95"/>
      <stop offset="100%" stop-color="#FFF3B0" stop-opacity="0"/>
    </linearGradient>
    <radialGradient id="body-spec" cx="28%" cy="22%" r="34%">
      <stop offset="0%"   stop-color="#FFFFFF" stop-opacity="0.95"/>
      <stop offset="55%"  stop-color="#FFFFFF" stop-opacity="0.25"/>
      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="body-shadow" cx="72%" cy="78%" r="70%">
      <stop offset="0%"   stop-color="#3B2A0A" stop-opacity="0"/>
      <stop offset="60%"  stop-color="#3B2A0A" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="#3B2A0A" stop-opacity="0.55"/>
    </radialGradient>

    <!-- Diamond-lattice skin scales with subtle bevel -->
    <pattern id="skin" x="0" y="0" width="78" height="78" patternUnits="userSpaceOnUse" patternTransform="rotate(2)">
      <path d="M 39 1 L 77 39 L 39 77 L 1 39 Z"
            fill="none" stroke="#7A4F1A" stroke-width="2.6" stroke-linejoin="round" opacity="0.85"/>
      <path d="M 39 1 L 77 39 L 39 77 L 1 39 Z"
            fill="none" stroke="#FFE9A0" stroke-width="0.9" stroke-linejoin="round" opacity="0.65"
            transform="translate(0 -1.2)"/>
      <circle cx="39" cy="39" r="3.4" fill="#C9820A"/>
      <circle cx="39" cy="39" r="1.4" fill="#FFE066"/>
      <circle cx="0"  cy="39" r="2.4" fill="#9C6510" opacity="0.85"/>
      <circle cx="78" cy="39" r="2.4" fill="#9C6510" opacity="0.85"/>
      <circle cx="39" cy="0"  r="2.4" fill="#9C6510" opacity="0.85"/>
      <circle cx="39" cy="78" r="2.4" fill="#9C6510" opacity="0.85"/>
    </pattern>

    <!-- Crown leaf gradients: back (deep) → mid → front (lit) -->
    <linearGradient id="leaf-back" x1="0.5" y1="0" x2="0.5" y2="1">
      <stop offset="0%"   stop-color="#1B5E20"/>
      <stop offset="55%"  stop-color="#0F3B14"/>
      <stop offset="100%" stop-color="#062309"/>
    </linearGradient>
    <linearGradient id="leaf-mid" x1="0.5" y1="0" x2="0.5" y2="1">
      <stop offset="0%"   stop-color="#66BB6A"/>
      <stop offset="55%"  stop-color="#2E7D32"/>
      <stop offset="100%" stop-color="#143E18"/>
    </linearGradient>
    <linearGradient id="leaf-front" x1="0.4" y1="0" x2="0.6" y2="1">
      <stop offset="0%"   stop-color="#D7F3D8"/>
      <stop offset="35%"  stop-color="#7FCB82"/>
      <stop offset="70%"  stop-color="#3E9243"/>
      <stop offset="100%" stop-color="#1B5E20"/>
    </linearGradient>
    <linearGradient id="leaf-spec" x1="0.5" y1="0" x2="0.5" y2="1">
      <stop offset="0%"   stop-color="#FFFFFF" stop-opacity="0.7"/>
      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0"/>
    </linearGradient>

    <filter id="drop" x="-15%" y="-10%" width="130%" height="130%">
      <feGaussianBlur in="SourceAlpha" stdDeviation="9"/>
      <feOffset dx="0" dy="16" result="o"/>
      <feColorMatrix in="o" type="matrix"
        values="0 0 0 0 0.42  0 0 0 0 0.27  0 0 0 0 0.06  0 0 0 0.55 0"/>
      <feBlend in="SourceGraphic" in2="o" mode="normal"/>
    </filter>
  </defs>

  <!-- Soft halo glow behind the fruit -->
  <ellipse cx="320" cy="560" rx="320" ry="330" fill="#FFD700" opacity="0.16"/>
  <ellipse cx="320" cy="560" rx="240" ry="260" fill="#FFE27A" opacity="0.26"/>

  <!-- ===== Crown leaves — every leaf anchors at (320, 360) ===== -->
  <!-- Back row -->
  <g filter="url(#drop)">
    <path d="M 320 360 Q 188 200 122 70 Q 218 232 286 358 Z" fill="url(#leaf-back)"/>
    <path d="M 320 360 Q 452 200 518 70 Q 422 232 354 358 Z" fill="url(#leaf-back)"/>
    <path d="M 320 360 Q 232 168 196 28 Q 264 198 300 358 Z" fill="url(#leaf-back)"/>
    <path d="M 320 360 Q 408 168 444 28 Q 376 198 340 358 Z" fill="url(#leaf-back)"/>
  </g>
  <!-- Mid row -->
  <g>
    <path d="M 320 360 Q 248 168 232 18 Q 288 198 308 358 Z" fill="url(#leaf-mid)"/>
    <path d="M 320 360 Q 392 168 408 18 Q 352 198 332 358 Z" fill="url(#leaf-mid)"/>
    <path d="M 320 360 Q 282 144 280 0   Q 304 184 312 358 Z" fill="url(#leaf-mid)"/>
    <path d="M 320 360 Q 358 144 360 0   Q 336 184 328 358 Z" fill="url(#leaf-mid)"/>
  </g>
  <!-- Front row + central blade with highlight -->
  <g>
    <path d="M 320 360 Q 308 152 314 8  Q 322 168 318 358 Z" fill="url(#leaf-front)"/>
    <path d="M 320 360 Q 332 152 326 8  Q 318 168 322 358 Z" fill="url(#leaf-front)" opacity="0.92"/>
    <!-- specular highlight along central blade -->
    <path d="M 320 350 Q 319 220 321 60" stroke="url(#leaf-spec)" stroke-width="3.4" fill="none" opacity="0.85"/>
    <!-- subtle vein striations -->
    <path d="M 320 320 Q 322 200 326 70"  stroke="#E8F5E9" stroke-width="1.8" fill="none" opacity="0.55"/>
    <path d="M 304 330 Q 296 220 286 90"  stroke="#C8E6C9" stroke-width="1.4" fill="none" opacity="0.45"/>
    <path d="M 336 330 Q 344 220 354 90"  stroke="#C8E6C9" stroke-width="1.4" fill="none" opacity="0.45"/>
  </g>

  <!-- ===== Pineapple body — shaded for 3D depth ===== -->
  <g filter="url(#drop)">
    <ellipse cx="320" cy="585" rx="240" ry="300" fill="url(#body3d)"
             stroke="#5C3A1A" stroke-width="5"/>
  </g>
  <!-- diamond-skin lattice clipped to fruit shape -->
  <ellipse cx="320" cy="585" rx="234" ry="294" fill="url(#skin)" opacity="0.92"/>
  <!-- ambient occlusion on the lower-right side -->
  <ellipse cx="320" cy="585" rx="234" ry="294" fill="url(#body-shadow)"/>
  <!-- broad specular highlight, top-left -->
  <ellipse cx="232" cy="450" rx="120" ry="170" fill="url(#body-spec)"/>
  <!-- thin warm rim at the top -->
  <path d="M 124 470 A 240 300 0 0 1 516 470" fill="none" stroke="url(#body-rim)" stroke-width="14" opacity="0.85"/>
  <!-- under-shadow on the ground plane -->
  <ellipse cx="320" cy="880" rx="200" ry="22" fill="#3B2A0A" opacity="0.22"/>
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


# ── Display name normalization ─────────────────────────────────────────
# Marketing-style codebase name: strips repo-suffix noise (`-monorepo`,
# `-mono`, `-app`, `-repo`, `-service`, `_app`, `.git`, `_v2`...), drops
# version trailers like `-v2` / `-2.0`, and PascalCases what remains so
# `spendwise-monorepo` → `SpendWise`, `my_cool_app` → `MyCool`,
# `auth-service` → `Auth`, `acme-platform` → `AcmePlatform`.
_NAME_TRAILING_NOISE_RE = re.compile(
    r"("
    r"[-_.]?monorepo"
    r"|[-_.]?mono"
    r"|[-_.]?repo"
    r"|[-_.]?app"
    r"|[-_.]?application"
    r"|[-_.]?platform"
    r"|[-_.]?service"
    r"|[-_.]?services"
    r"|[-_.]?server"
    r"|[-_.]?backend"
    r"|[-_.]?api"
    r"|[-_.]?web"
    r"|[-_.]?ui"
    r"|[-_.]?frontend"
    r"|[-_.]?client"
    r"|[-_.]?example"
    r"|[-_.]?demo"
    r"|[-_.]?sample"
    r"|[-_.]?starter"
    r"|[-_.]?template"
    r"|[-_.]?v\d+(?:\.\d+)*"
    r"|[-_.]?\d+(?:\.\d+)+"
    r"|\.git"
    r")$",
    re.IGNORECASE,
)
_NAME_SPLIT_RE = re.compile(r"[\s\-_.]+")


def display_name(raw: object) -> str:
    """Auto-derive a marketing-style display name from a project slug.

    Examples:
        spendwise-monorepo  → SpendWise
        my_cool_app         → MyCool
        auth-service        → Auth
        acme-platform-v2    → Acme
        FooBar              → FooBar (already CamelCase, returned as-is)
        @scope/pkg-name     → PkgName

    Always returns a non-empty string. Falls back to the original if the
    cleanup would yield an empty token.
    """
    s = str(raw or "").strip()
    if not s:
        return "Codebase"
    # Drop npm scope prefix like "@spendwise/api" → "api".
    if s.startswith("@") and "/" in s:
        s = s.split("/", 1)[1]
    # Strip a sequence of trailing noise tokens (e.g. `-app-v2`).
    prev = None
    while prev != s:
        prev = s
        s = _NAME_TRAILING_NOISE_RE.sub("", s).strip("-_. ")
    if not s:
        # Everything was a noise word; fall back to the original raw input
        # (still escape later via esc()). Better than rendering nothing.
        return str(raw or "Codebase").strip() or "Codebase"
    # If the cleaned name is already CamelCase (no separators, has at
    # least one lowercase + one uppercase), keep it as-is so we don't
    # mangle hand-crafted brands like "SpendWise" or "OpenAI".
    has_sep = bool(_NAME_SPLIT_RE.search(s))
    if not has_sep and any(c.isupper() for c in s) and any(c.islower() for c in s):
        return s
    parts = [p for p in _NAME_SPLIT_RE.split(s) if p]
    if not parts:
        return str(raw or "Codebase").strip() or "Codebase"
    return "".join(p[:1].upper() + p[1:] for p in parts)


# ── Inline emphasis for summary prose ──────────────────────────────────
# Authors mark important words with **double asterisks** in the JSON.
# Numbers (123, 12.5, 12k, 7-day, 100×) are auto-emphasized.
_EM_BOLD_RE = re.compile(r"\*\*([^*\n][^*\n]*?)\*\*")
_EM_NUM_RE = re.compile(
    r"(?<![\w<>])("
    r"\d+(?:[.,]\d+)?[kKmMbB×x]?(?:-[a-zA-Z]+)?"  # 24, 12.5, 12k, 7-day, 100×
    r"|~\d+(?:[.,]\d+)?[kKmMbB×x]?"  # ~24
    r")(?![\w])"
)


def emphasize(text: object) -> str:
    """HTML-escape text and apply summary emphasis.

    - Wraps ``**word**`` as ``<strong class="kw">word</strong>``.
    - Wraps standalone numeric tokens as ``<span class="num">…</span>``.

    Output is safe to drop into HTML; falls back to plain escaped text
    when no markers are present, so existing callers stay safe.
    """
    if text is None:
        return ""
    raw = str(text)
    if not raw:
        return ""
    # 1. Tokenize ** runs first so the inner text never gets re-emphasized.
    parts: list[tuple[str, str]] = []  # (kind, payload)
    pos = 0
    for m in _EM_BOLD_RE.finditer(raw):
        if m.start() > pos:
            parts.append(("text", raw[pos : m.start()]))
        parts.append(("kw", m.group(1)))
        pos = m.end()
    if pos < len(raw):
        parts.append(("text", raw[pos:]))

    out: list[str] = []
    for kind, payload in parts:
        if kind == "kw":
            out.append(f'<strong class="kw">{esc(payload)}</strong>')
            continue
        # Number emphasis on plain text segments only.
        last = 0
        for nm in _EM_NUM_RE.finditer(payload):
            if nm.start() > last:
                out.append(esc(payload[last : nm.start()]))
            out.append(f'<span class="num">{esc(nm.group(1))}</span>')
            last = nm.end()
        if last < len(payload):
            out.append(esc(payload[last:]))
    return "".join(out)


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
        detail_text = ""
        if isinstance(item, dict):
            sev = item.get("severity", "low")
            title = item.get("title", "")
            location = item.get("location", "")
            rec = (
                item.get("remediation")
                or item.get("recommendation")
                or ""
            )
            detail_text = item.get("detail", "") or ""
            if not rec and detail_text:
                rec = detail_text
                detail_text = ""
        else:
            sev, title, location, rec = item

        rec_html = (
            emphasize(rec)
            if rec
            else '<em class="finding-empty">No remediation provided — populate the <code>remediation</code> field.</em>'
        )
        detail_block = (
            f'<div class="finding-detail">{emphasize(detail_text)}</div>' if detail_text else ""
        )
        html_parts.append(
            f'<article class="finding finding-{sev}" data-searchable>'
            f'<div class="finding-header"><span class="badge badge-{sev}">{sev}</span>'
            f'<div class="finding-title">{esc(title)}</div></div>'
            f'<div class="finding-location">{esc(location)}</div>'
            f'{detail_block}'
            f'<div class="finding-recommendation">'
            f'<span class="finding-rec-label">\U0001f4a1 Recommendation</span>'
            f'<span class="finding-rec-body">{rec_html}</span>'
            f'</div>'
            "</article>"
        )
    return "\n".join(html_parts)


# ── HTML Generation ─────────────────────────────────────────────────────

def generate(analysis_path: Path, output_path: Path, title: str | None = None, project_override: str | None = None, enrichment_path: Path | None = None) -> None:
    root = Path(__file__).resolve().parent.parent
    data = json.loads(analysis_path.read_text())

    # Auto-discover enrichment.json sitting next to the analysis JSON when
    # the caller didn't pass --enrichment explicitly. This is the canonical
    # SKILL.md layout (`.code-visualizer/codebase-analysis.json` +
    # `.code-visualizer/enrichment.json`) — without auto-discovery the
    # generator silently falls back to `[AI_FILL]` placeholders even when
    # a perfectly valid enrichment file exists, which is the worst kind of
    # silent failure for a visualization tool.
    if enrichment_path is None:
        sibling = analysis_path.parent / "enrichment.json"
        if sibling.exists():
            enrichment_path = sibling

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

    # Raw slug from analysis JSON (e.g. "spendwise-monorepo") is kept for
    # internal references like the page <title>; the display name we render
    # in the .codebase-card and sidebar is the auto-derived marketing
    # version (e.g. "SpendWise"). See display_name() for the rules.
    raw_project = project_override or data.get("project_name") or "codebase"
    project = display_name(raw_project)
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

    title_text = title or f"{project} \u2014 Code Visualization"

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
    # === Pineapple Seasoning Score (effort \u2192 seasoning) ==========
    # Replaces the legacy Small/Medium/Large effort badge with a 1-3
    # pineapple-emoji rating. Authors may pass any of the legacy tokens
    # (small/medium/large), the new tokens (mild/medium/spicy or
    # quick-win/medium-effort/big-bake), or just numeric `effort: 1|2|3`.
    SEASONING_TIERS = {
        # 1 pineapple \u2014 Quick Win
        "small": (1, "Quick Win"),
        "s": (1, "Quick Win"),
        "1": (1, "Quick Win"),
        "mild": (1, "Quick Win"),
        "quick": (1, "Quick Win"),
        "quick-win": (1, "Quick Win"),
        "quick_win": (1, "Quick Win"),
        # 2 pineapples \u2014 Medium Effort
        "medium": (2, "Medium Effort"),
        "m": (2, "Medium Effort"),
        "2": (2, "Medium Effort"),
        "medium-effort": (2, "Medium Effort"),
        "medium_effort": (2, "Medium Effort"),
        # 3 pineapples \u2014 Big Bake
        "large": (3, "Big Bake"),
        "l": (3, "Big Bake"),
        "3": (3, "Big Bake"),
        "spicy": (3, "Big Bake"),
        "big": (3, "Big Bake"),
        "big-bake": (3, "Big Bake"),
        "big_bake": (3, "Big Bake"),
        "huge": (3, "Big Bake"),
    }

    def seasoning_chip(effort_value) -> str:
        """Render a Pineapple Seasoning Score chip from any effort token.

        Batch 5: chips on cards / roadmap / priority matrix render the
        pineapple emoji ONLY (no "Quick Win" text), so the chip stays a
        compact glyph indicator. The descriptive label only appears in
        the SEASONING_LEGEND_HTML legend at the top of the tab.
        """
        if effort_value in (None, ""):
            return ""
        if isinstance(effort_value, (int, float)):
            key = str(int(effort_value))
        else:
            key = str(effort_value).strip().lower()
        level, label = SEASONING_TIERS.get(key, (2, str(effort_value).strip().title() or "Medium Effort"))
        pineapples = "\U0001f34d" * level
        return (
            f'<span class="seasoning-chip seasoning-{level} seasoning-glyph-only" '
            f'aria-label="Effort: {esc(label)} ({level} pineapples)" '
            f'title="{esc(label)}">'
            f'<span class="seasoning-glyph" aria-hidden="true">{pineapples}</span>'
            "</span>"
        )

    # Batch 5: only ONE legend, emitted once at the top of the tab. The
    # legend keeps the descriptive labels so the reader can decode the
    # chips that follow.
    SEASONING_LEGEND_HTML = (
        '<div class="seasoning-legend" role="note" aria-label="Pineapple Seasoning Score legend">'
        '<span class="seasoning-legend-label">Pineapple Seasoning Score</span>'
        '<span class="seasoning-chip seasoning-1"><span class="seasoning-glyph">\U0001f34d</span>'
        '<span class="seasoning-label">Quick Win</span></span>'
        '<span class="seasoning-chip seasoning-2"><span class="seasoning-glyph">\U0001f34d\U0001f34d</span>'
        '<span class="seasoning-label">Medium Effort</span></span>'
        '<span class="seasoning-chip seasoning-3"><span class="seasoning-glyph">\U0001f34d\U0001f34d\U0001f34d</span>'
        '<span class="seasoning-label">Big Bake</span></span>'
        '</div>'
    )

    def render_cards(items: list, extra_class: str = "", suppress_effort: bool = False) -> str:
        """Render a list of feature/suggestion/etc. cards.

        Each item may be either a plain string or a dict with these
        optional fields:

        - ``title`` / ``description``: paragraph-style content (legacy).
        - ``bullets``: ``list[str]`` rendered as a ``<ul class="card-bullets">``.
          When present, bullets render IN ADDITION TO any description
          (``description`` becomes the lead-in line above the bullets).
        - ``location``: file path rendered as ``<code>`` under the body.
        - ``effort``: rendered as a Pineapple Seasoning Score chip
          (``\U0001f34d`` Quick Win / ``\U0001f34d\U0001f34d`` Medium Effort /
          ``\U0001f34d\U0001f34d\U0001f34d`` Big Bake).

        ``suppress_effort=True`` (batch 7) silently drops the effort chip
        even when the item carries one \u2014 used by the Simulation tab's
        "What comes next?" feature cards, where the seasoning chip is
        out of place (effort chips belong to Suggestions only).
        """
        out = []
        for item in items:
            if isinstance(item, str):
                out.append(
                    f'<article class="card {extra_class}" data-searchable><p>{emphasize(item)}</p></article>'
                )
                continue
            if not isinstance(item, dict):
                continue

            t = item.get("title", "")
            d_raw = item.get("description", "")
            bullets = item.get("bullets")
            loc = item.get("location", "")
            effort = item.get("effort", "")

            badges = ""
            if effort not in (None, "") and not suppress_effort:
                badges = f" {seasoning_chip(effort)}"

            body_parts: list[str] = []
            if isinstance(d_raw, str) and d_raw.strip():
                body_parts.append(f'<p class="card-desc">{emphasize(d_raw)}</p>')
            if isinstance(bullets, list) and bullets:
                lis = "".join(
                    f"<li>{emphasize(b)}</li>"
                    for b in bullets
                    if isinstance(b, str) and b.strip()
                )
                if lis:
                    body_parts.append(f'<ul class="card-bullets">{lis}</ul>')
            if loc:
                body_parts.append(f'<div class="card-loc"><code>{esc(loc)}</code></div>')
            body_html = "".join(body_parts) or '<p class="card-desc"></p>'

            out.append(
                f'<article class="card {extra_class}" data-searchable>'
                f'<div class="card-title">{esc(t)}{badges}</div>'
                f"{body_html}"
                "</article>"
            )
        return "\n".join(out)

    def prose_or_bullets(value, fallback: str) -> str:
        """Render ``value`` as a paragraph (str) or a bullet list (list[str])."""
        if isinstance(value, list) and value:
            lis = "".join(
                f"<li>{emphasize(b)}</li>"
                for b in value
                if isinstance(b, str) and b.strip()
            )
            if lis:
                return f'<ul class="prose-bullets" data-searchable>{lis}</ul>'
        if isinstance(value, str) and value.strip():
            return f'<p data-searchable>{emphasize(value)}</p>'
        return f'<p data-searchable>{esc(fallback)}</p>'

    def render_checklist(items: list) -> str:
        li = "".join(f"<li>{esc(i)}</li>" for i in items)
        return f'<ul class="checklist">{li}</ul>'

    def render_priority_items(items: list) -> str:
        """Priority Matrix as plain bullet rows (batch 5).

        The legacy "Do now / Do soon / Do later" chips and the per-row
        seasoning effort chips have been REMOVED at the user's request \u2014
        each row is now just the recommendation text (with `**bold**`
        highlights) inside a styled card. The original `label` field is
        ignored visually, but accepted for backward compat.
        """
        if not items:
            return ""
        rows = []
        for item in items:
            if isinstance(item, dict):
                text = item.get("text", "")
            elif isinstance(item, str):
                text = item
            else:
                continue
            if not text or not str(text).strip():
                continue
            rows.append(
                f'<li class="priority-row" data-searchable>'
                f'<span class="priority-text">{emphasize(text)}</span>'
                f'</li>'
            )
        if not rows:
            return ""
        return f'<ul class="priority-matrix">{"".join(rows)}</ul>'

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
    prod_arch_value = prod_dev.get("product_architecture")
    prod_arch_html = prose_or_bullets(
        prod_arch_value,
        "[AI_FILL: Product architecture — bullets describing how features are distributed across packages]",
    )
    prod_patterns = render_cards(get_list(prod_dev, "design_patterns"))

    prod_easy_what = get_str(prod_easy, "what_it_does", "[AI_FILL: What does this app do — plain-language feature description]")
    prod_easy_capabilities = render_checklist(get_list(prod_easy, "capabilities"))
    prod_easy_org = get_str(prod_easy, "organization", "[AI_FILL: How is the app organized — name the main parts and their roles]")

    # Technical
    tech_dev = tech.get("dev", {})
    tech_easy = tech.get("easy", {})
    tech_backend_html = prose_or_bullets(
        tech_dev.get("backend_analysis"),
        "[AI_FILL: Backend analysis — middleware pipeline, route structure, controller patterns, error handling]",
    )
    tech_frontend_html = prose_or_bullets(
        tech_dev.get("frontend_analysis"),
        "[AI_FILL: Frontend analysis — component structure, state management, routing, or state that none exists]",
    )
    tech_quality = render_cards(get_list(tech_dev, "code_quality"))

    tech_easy_how = get_str(tech_easy, "how_built", "[AI_FILL: How is the code built — plain-language analogy explaining the layers]")
    tech_easy_parts = get_str(tech_easy, "main_parts", "[AI_FILL: The main parts — describe the actual packages and what they do]")
    tech_easy_connect = get_str(tech_easy, "connections", "[AI_FILL: How the parts connect — describe actual internal dependencies in plain language]")
    tech_easy_health_items = get_list(tech_easy, "health_check")

    # Database
    db_dev = db.get("dev", {})
    db_easy = db.get("easy", {})
    db_index_html = prose_or_bullets(
        db_dev.get("index_analysis"),
        "[AI_FILL: Index analysis — existing indexes, query benefits, missing index recommendations]",
    )
    db_query_html = prose_or_bullets(
        db_dev.get("query_patterns"),
        "[AI_FILL: Query patterns — ORM vs raw SQL, transaction usage, bulk operations]",
    )
    db_integration_html = prose_or_bullets(
        db_dev.get("backend_integration"),
        "[AI_FILL: Backend integration — connection management, where DB calls live, error handling]",
    )
    db_easy_what = get_str(db_easy, "what_data", "[AI_FILL: What data does the app store — plain-language description of each data type]")
    db_easy_talk = get_str(db_easy, "how_talks", "[AI_FILL: How does the app talk to the database — simple read/write explanation]")
    db_easy_safe = get_str(db_easy, "data_safety", "[AI_FILL: Is the data safe — plain-language data integrity explanation]")

    # Security
    sec_dev = sec.get("dev", {})
    sec_easy = sec.get("easy", {})
    sec_auth_html = prose_or_bullets(
        sec_dev.get("auth_analysis"),
        "[AI_FILL: Authentication analysis \u2014 JWT/session patterns, secret management, token expiry, role checks]",
    )
    sec_validation_html = prose_or_bullets(
        sec_dev.get("input_validation"),
        "[AI_FILL: Input validation audit \u2014 what inputs are validated, what are not, injection risk areas]",
    )
    sec_deps_html = prose_or_bullets(
        sec_dev.get("dependency_risk"),
        "[AI_FILL: Dependency risk \u2014 known CVEs or risky patterns in third-party packages]",
    )
    sec_scale_html = prose_or_bullets(
        sec_dev.get("scalability"),
        "[AI_FILL: Scalability analysis \u2014 bottlenecks, horizontal vs vertical readiness, connection pooling]",
    )
    high_count = sec_dev.get("high_count", 2)
    med_count = sec_dev.get("medium_count", 2)
    low_count = sec_dev.get("low_count", 1)

    sec_easy_safe = get_str(sec_easy, "is_safe", "[AI_FILL: Is the app safe \u2014 4-tier rating with one-sentence verdict]")
    sec_easy_safe_color = get_str(sec_easy, "safety_color", "sick")
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
    # Suggestions/General view: each section accepts a string OR a
    # bullet array, both with **bold** highlight markers (batch 4).
    sug_easy_product_html = prose_or_bullets(
        sug_easy.get("product"),
        "[AI_FILL: How to make the product better \u2014 plain-language improvement ideas with **bold** highlights]",
    )
    sug_easy_code_html = prose_or_bullets(
        sug_easy.get("code"),
        "[AI_FILL: How to make the code stronger \u2014 simplified technical suggestions with **bold** highlights]",
    )
    sug_easy_safer_html = prose_or_bullets(
        sug_easy.get("security"),
        "[AI_FILL: How to make it safer \u2014 non-jargon security improvements with **bold** highlights]",
    )
    sug_easy_growth_html = prose_or_bullets(
        sug_easy.get("growth"),
        "[AI_FILL: How to handle more users \u2014 growth readiness in plain language with **bold** highlights]",
    )
    sug_easy_first = render_priority_items(get_list(sug_easy, "priorities"))

    # === Pitch (batch 5: single "Boss View" \u2014 dev/general split removed) ===
    # Source data: prefer the new top-level `pitch.boss.*` keys; fall back
    # to the legacy `pitch.dev.*` / `pitch.easy.*` so older enrichment
    # files keep rendering. Each section accepts a STRING (paragraph) or
    # a LIST OF STRINGS (bullet array) where applicable.
    pitch_dev = pitch.get("dev", {})
    pitch_easy = pitch.get("easy", {})
    pitch_boss = pitch.get("boss", {})

    def _pitch_get(*keys, default=None):
        """Return the first non-empty value found in boss \u2192 easy \u2192 dev."""
        for source in (pitch_boss, pitch_easy, pitch_dev):
            for k in keys:
                v = source.get(k) if isinstance(source, dict) else None
                if v not in (None, "", []):
                    return v
        return default

    pitch_oneliner = _pitch_get("one_liner", "oneliner", "elevator_pitch",
                                default="[AI_FILL: The one-liner \u2014 a self-promotional, marketing-tone single sentence with **bold** highlights and aha factor]")
    pitch_story = _pitch_get("story", "tell_your_story",
                             default="[AI_FILL: Tell your story \u2014 a narrative paragraph in product language with **bold** highlights]")
    pitch_audience = _pitch_get("audience", "who_for",
                                default=["[AI_FILL: Who is this for \u2014 target persona bullet with **bold** highlights]"])
    pitch_why = _pitch_get("why_matters", "why",
                           default=["[AI_FILL: Why does this matter \u2014 impact bullet with **bold** highlights]"])
    pitch_special = _pitch_get("what_special", "differentiators",
                               default=["[AI_FILL: What makes it special \u2014 differentiator bullet with **bold** highlights]"])
    pitch_strengths = _pitch_get("architecture_strengths", "strengths",
                                 default=["[AI_FILL: Architecture strengths \u2014 bullet with **bold** highlights]"])
    pitch_stack = _pitch_get("tech_stack_justification", "tech_stack",
                             default=["[AI_FILL: Tech stack justification \u2014 bullet with **bold** highlights]"])
    pitch_integration = _pitch_get("integration_narrative", "integration",
                                   default=["[AI_FILL: Integration narrative \u2014 bullet with **bold** highlights]"])
    pitch_numbers = get_list(pitch_dev, "by_the_numbers")

    # Pitch Boss View \u2014 the one-liner and "Tell your story" are rendered
    # WITHOUT `**bold**` keyword highlights or auto-number chips (batch 7):
    # the user wants the one-liner sentence to read as ONE flashy headline,
    # and the story to read as plain narrative prose. Both still accept
    # either a string or a single-item list (treated as a paragraph).
    def _plain_paragraph(value: object, fallback: str) -> str:
        if isinstance(value, list) and value:
            value = " ".join(b for b in value if isinstance(b, str) and b.strip())
        if not isinstance(value, str) or not value.strip():
            return f'<p data-searchable>{esc(fallback)}</p>'
        # Strip `**...**` markers so the wrapped text renders verbatim, no
        # `.kw` / `.num` chips. We keep punctuation and spacing intact.
        stripped = _EM_BOLD_RE.sub(lambda m: m.group(1), value)
        return esc(stripped)

    pitch_oneliner_text = _plain_paragraph(
        pitch_oneliner,
        "[AI_FILL: The one-liner \u2014 self-promotional sales-pitch sentence]",
    )
    # Wrap the one-liner sentence so .pitch-oneliner-text can style the
    # whole sentence as a flashy gradient-fill headline (batch 7).
    pitch_oneliner_html = (
        f'<p data-searchable class="pitch-oneliner-line">'
        f'<span class="pitch-oneliner-text">{pitch_oneliner_text}</span>'
        f'</p>'
    )
    pitch_story_text = _plain_paragraph(
        pitch_story,
        "[AI_FILL: Tell your story \u2014 narrative paragraph in product language]",
    )
    pitch_story_html = f'<p data-searchable>{pitch_story_text}</p>'
    pitch_audience_html = prose_or_bullets(pitch_audience, "[AI_FILL: Who is this for \u2014 bullets]")
    pitch_why_html = prose_or_bullets(pitch_why, "[AI_FILL: Why does this matter \u2014 bullets]")
    pitch_special_html = prose_or_bullets(pitch_special, "[AI_FILL: What's special \u2014 bullets]")
    pitch_strengths_html = prose_or_bullets(pitch_strengths, "[AI_FILL: Architecture strengths \u2014 bullets]")
    pitch_stack_html = prose_or_bullets(pitch_stack, "[AI_FILL: Tech stack justification \u2014 bullets]")
    pitch_integration_html = prose_or_bullets(pitch_integration, "[AI_FILL: Integration narrative \u2014 bullets]")

    # === Simulation (batch 5: single "Boss View") =======================
    # Source data: prefer `simulation.boss.*` then merge content from the
    # legacy easy + dev splits so existing enrichment doesn't disappear.
    sim_dev = sim.get("dev", {})
    sim_easy = sim.get("easy", {})
    sim_boss = sim.get("boss", {})

    def _sim_get(*keys, default=None):
        for source in (sim_boss, sim_easy, sim_dev):
            for k in keys:
                v = source.get(k) if isinstance(source, dict) else None
                if v not in (None, "", []):
                    return v
        return default

    # "What if it takes off" merges product-view + dev growth scenario.
    sim_takeoff_value = _sim_get("takes_off", "takeoff",
                                 default=None)
    if sim_takeoff_value is None:
        # Auto-merge legacy easy.takes_off + dev.growth_scenario into a bullet array.
        legacy_takeoff = sim_easy.get("takes_off")
        legacy_growth = sim_dev.get("growth_scenario")
        merged = []
        if isinstance(legacy_takeoff, list):
            merged.extend([b for b in legacy_takeoff if isinstance(b, str)])
        elif isinstance(legacy_takeoff, str) and legacy_takeoff.strip():
            merged.append(legacy_takeoff)
        if isinstance(legacy_growth, list):
            merged.extend([b for b in legacy_growth if isinstance(b, str)])
        elif isinstance(legacy_growth, str) and legacy_growth.strip():
            merged.append(legacy_growth)
        sim_takeoff_value = merged or "[AI_FILL: What if it takes off \u2014 success-scenario bullets in product language with **bold** highlights]"
    sim_takeoff_html = prose_or_bullets(
        sim_takeoff_value,
        "[AI_FILL: What if it takes off \u2014 success-scenario bullets with **bold** highlights]",
    )

    # "What comes next" \u2014 list of feature cards (title + bullets/desc).
    sim_next_cards = _sim_get("whats_next_cards", "next_cards",
                              default=None)
    if not sim_next_cards:
        # Auto-derive cards from legacy free-text fields.
        sim_next_cards = []
        for src_key, src in (("easy.whats_next", sim_easy.get("whats_next")),
                              ("dev.feature_expansion", sim_dev.get("feature_expansion"))):
            if isinstance(src, list):
                for item in src:
                    if isinstance(item, dict):
                        sim_next_cards.append(item)
                    elif isinstance(item, str) and item.strip():
                        sim_next_cards.append({"title": "What comes next", "bullets": [item]})
            elif isinstance(src, str) and src.strip():
                sim_next_cards.append({"title": "What comes next", "bullets": [src]})
    # Batch 7: Simulation "What comes next?" cards must NOT show the
    # pineapple seasoning chip \u2014 effort chips belong to Suggestions.
    sim_next_html = render_cards(sim_next_cards, suppress_effort=True) if sim_next_cards else ""

    sim_pains_value = _sim_get("growing_pains", "pains",
                               default=sim_easy.get("growing_pains") or sim_dev.get("failure_modes"))
    sim_pains_html = prose_or_bullets(
        sim_pains_value,
        "[AI_FILL: Growing pains \u2014 plain-language scaling warning bullets with **bold** highlights]",
    )

    # "The big picture" \u2014 step-by-step phases (roadmap-style stepper). Pull
    # from new big_picture_steps OR collect leftover dev/easy fields.
    sim_big_steps = _sim_get("big_picture_steps", "big_picture",
                             default=None)
    if sim_big_steps is None or isinstance(sim_big_steps, str):
        # Stitch a default phased journey from the leftover fields so
        # existing enrichment files still produce a stepper.
        leftovers = []
        for raw in (
            sim_dev.get("architecture_evolution"),
            sim_easy.get("big_picture"),
            sim_dev.get("team_scaling"),
            sim_easy.get("building_team"),
        ):
            if isinstance(raw, str) and raw.strip():
                leftovers.append(raw)
            elif isinstance(raw, list):
                leftovers.extend([b for b in raw if isinstance(b, str) and b.strip()])
        if leftovers:
            phase_titles = ["Today", "Soon", "Next year", "Long term", "Vision"]
            sim_big_steps = [
                {"title": phase_titles[min(i, len(phase_titles) - 1)], "text": text}
                for i, text in enumerate(leftovers[:5])
            ]
        else:
            sim_big_steps = []

    if isinstance(sim_big_steps, list) and sim_big_steps:
        node_htmls = []
        default_when = ["Today", "Soon", "Next year", "Long term", "Vision"]
        for i, step in enumerate(sim_big_steps):
            if isinstance(step, str):
                step = {"title": default_when[min(i, len(default_when) - 1)], "text": step}
            elif not isinstance(step, dict):
                continue
            title = step.get("title") or default_when[min(i, len(default_when) - 1)]
            when = step.get("when") or default_when[min(i, len(default_when) - 1)]
            text = step.get("text", "")
            tier = "now" if i == 0 else ("next" if i == 1 else ("later" if i == 2 else "future"))
            node_htmls.append(
                f'<li class="roadmap-node roadmap-{tier}" data-searchable>'
                f'<span class="roadmap-medallion" aria-hidden="true">{i+1}</span>'
                f'<span class="roadmap-when">{esc(when)}</span>'
                f'<span class="roadmap-title">{emphasize(title)}</span>'
                + (f'<span class="roadmap-text">{emphasize(text)}</span>' if text else "")
                + "</li>"
            )
        sim_big_html = (
            f'<ol class="scalability-roadmap big-picture-stepper" aria-label="The big picture phased journey">'
            f'{"".join(node_htmls)}'
            f"</ol>"
        )
    else:
        sim_big_html = '<p data-searchable>[AI_FILL: The big picture \u2014 step-by-step phased journey in product language]</p>'

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

    # Mode toggle that lives inline at the top of every non-Overview tab,
    # replacing the per-tab breadcrumb. Buttons are labelled "Developer View"
    # and "General View" (per SKILL Phase 5 / batch-2 rename).
    panel_mode_toggle = (
        '<div class="panel-header">'
        '<div class="mode-toggle" role="group" aria-label="Audience view">'
        '<button data-mode="dev" class="active" onclick="setMode(\'dev\')">Developer View</button>'
        '<button data-mode="easy" onclick="setMode(\'easy\')">General View</button>'
        '</div></div>'
    )
    # Batch 6: Pitch + Simulation use a SINGLE non-toggleable pill that
    # matches the same .panel-header > .mode-toggle chrome as the rest
    # of the tabs. The label inside is "Boss View" and is decorative
    # (no click handler, role="group" with a single active button).
    boss_view_panel_header = (
        '<div class="panel-header">'
        '<div class="mode-toggle boss-view-toggle" role="group" aria-label="Audience view">'
        '<button class="active" type="button" aria-pressed="true" disabled>Boss View</button>'
        '</div></div>'
    )

    # --- Summary cards for Overview lower half --------------------------
    summary_card_tabs = [t for t in tab_ids if t != "overview"]
    summary_cards_html = ""
    for tid in summary_card_tabs:
        summary_text = tab_summaries.get(tid, f"[AI_FILL: {tab_labels[tid]} tab summary \u2014 1-2 sentence highlight finding]")
        summary_cards_html += (
            f'<article class="card summary-link-card" '
            f'onclick="goToTab(\'{tid}\')" data-searchable tabindex="0" '
            f'role="link" aria-label="Open {esc(tab_labels[tid])} tab">'
            f'<div class="summary-link-head">'
            f'<div class="card-icon" aria-hidden="true">{tab_icons.get(tid, "\U0001f4cb")}</div>'
            f'<div class="card-title">{tab_labels[tid]}</div>'
            f"</div>"
            f'<div class="card-desc">{emphasize(summary_text)}</div>'
            f'<span class="card-link">View details →</span>'
            f'</article>\n'
        )

    # --- Roadmap rendering (batch 4: horizontal stepper) ----------------
    # Each step renders as a connected node with a numbered medallion,
    # title, and optional "when" lane (Now / Next / Later / Future). The
    # row scrolls horizontally on narrow viewports.
    roadmap_steps = []
    for i, step in enumerate(sug_roadmap):
        if isinstance(step, str):
            roadmap_steps.append({"text": step})
        elif isinstance(step, dict):
            roadmap_steps.append(step)

    roadmap_html = ""
    if roadmap_steps:
        node_htmls = []
        total = len(roadmap_steps)
        # Default "when" labels if author doesn't supply one.
        default_when = ["Now", "Next", "Later", "Future", "Future"]
        for i, step in enumerate(roadmap_steps):
            title = step.get("title") or step.get("text", "")
            text = step.get("text", "") if step.get("title") else ""
            when = step.get("when") or default_when[min(i, len(default_when) - 1)]
            tier = "now" if i == 0 else ("next" if i == 1 else ("later" if i == 2 else "future"))
            # Batch 5: per-node effort/seasoning chip removed.
            node_htmls.append(
                f'<li class="roadmap-node roadmap-{tier}" data-searchable>'
                f'<span class="roadmap-medallion" aria-hidden="true">{i+1}</span>'
                f'<span class="roadmap-when">{esc(when)}</span>'
                f'<span class="roadmap-title">{emphasize(title)}</span>'
                + (f'<span class="roadmap-text">{emphasize(text)}</span>' if text else "")
                + "</li>"
            )
        roadmap_html = (
            f'<ol class="scalability-roadmap" aria-label="Scalability roadmap stepper">'
            f'{"".join(node_htmls)}'
            f"</ol>"
        )

    # --- Strengths, numbers, differentiators ----------------------------
    # Batch 5: strengths/special are now rendered through prose_or_bullets
    # via *_html variables above. Only `numbers_html` is still used.
    numbers_html = "".join(
        f'<div class="metric-card" data-searchable><div class="card-value">{esc(n.get("value",""))}</div>'
        f'<div class="card-label">{esc(n.get("label",""))}</div></div>'
        for n in pitch_numbers if isinstance(n, dict)
    )

    # === Code Health Check: 4-tier scale (Health / Sick / Severe Sick / Death) ===
    # Enrichment may use either the new 4-tier color tokens (`health`, `sick`,
    # `severe`, `death`) or the legacy 3-tier (`green`, `yellow`, `red`). We
    # map both to the same .traffic-* CSS classes; if the author also omits a
    # `label`, we fall back to a sensible default per tier.
    HEALTH_TIER_MAP = {
        "health": ("health", "Health"),
        "sick": ("sick", "Sick"),
        "severe": ("severe", "Severe Sick"),
        "severe-sick": ("severe", "Severe Sick"),
        "severe_sick": ("severe", "Severe Sick"),
        "death": ("death", "Death"),
        # Legacy
        "green": ("health", "Health"),
        "yellow": ("sick", "Sick"),
        "orange": ("severe", "Severe Sick"),
        "red": ("severe", "Severe Sick"),
        "black": ("death", "Death"),
    }
    health_html = ""
    for h in tech_easy_health_items:
        if not isinstance(h, dict):
            continue
        raw_color = str(h.get("color", "sick")).strip().lower()
        tier_key, tier_label = HEALTH_TIER_MAP.get(raw_color, ("sick", "Sick"))
        author_label = h.get("label", "")
        # If the author label still uses the old "Foo: Good/Yellow/Red" form
        # (e.g. "Organization: Good"), keep it; otherwise prefix with tier.
        label = str(author_label).strip() or tier_label
        desc = h.get("description", "")
        health_html += (
            f'<div class="health-row" data-searchable style="margin:8px 0">'
            f'<span class="traffic-light traffic-{tier_key}">{esc(label)}</span> '
            f'<span class="health-row-desc">{emphasize(desc)}</span>'
            f'</div>'
        )

    health_legend_html = (
        '<div class="health-legend" role="note" aria-label="Health check legend">'
        '<span class="health-legend-label">Scale</span>'
        '<span class="traffic-light traffic-health">Health</span>'
        '<span class="traffic-light traffic-sick">Sick</span>'
        '<span class="traffic-light traffic-severe">Severe Sick</span>'
        '<span class="traffic-light traffic-death">Death</span>'
        '</div>'
    )

    # === Security "Is the app safe?" verdict (4-tier, batch 4) ===
    # Reuses the same 4-tier scale as the Code Health Check so the
    # cross-tab vocabulary is consistent. The author can pass any of the
    # new tokens (`health`, `sick`, `severe`, `death`) or legacy 3-tier
    # tokens; both flow through HEALTH_TIER_MAP.
    sec_safe_tier_key, sec_safe_tier_label = HEALTH_TIER_MAP.get(
        str(sec_easy_safe_color).strip().lower(), ("sick", "Sick")
    )
    sec_easy_safe_html = (
        f'{health_legend_html}'
        f'<div class="health-row safety-verdict" data-searchable>'
        f'<span class="traffic-light traffic-{sec_safe_tier_key}">{esc(sec_safe_tier_label)}</span> '
        f'<span class="health-row-desc">{emphasize(sec_easy_safe)}</span>'
        f'</div>'
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
    <div class="sidebar-header"><span>{esc(project)}</span></div>
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
    </div>

    <!-- ============================================================= -->
    <!-- TAB 1: OVERVIEW (no mode split)                                -->
    <!-- ============================================================= -->
    <section class="tab-panel active" id="panel-overview" role="tabpanel">
      <!-- NOTE: Overview no longer renders a project breadcrumb. The page
           title role is taken over by the .codebase-card below the hero,
           which is the only place the codebase name appears at the top
           of the page. -->

      <div class="hero">
        <!-- Left of the pineapple: EVERGREEN content that stays the same
             on every visualization this skill produces. Batch 4 stripped
             the dashed-box framing so the title + tagline sit directly
             on the hero background, and removed the second block entirely. -->
        <div class="hero-content">
          <div class="hero-evergreen" data-tbd="1">
            <h1 class="hero-evergreen-title">Pineapple Code Cartography
              <button class="tooltip-trigger" type="button"
                data-tooltip="Use the tab bar to change view, or press 1-{len(tab_ids)} to jump between tabs."
                aria-label="How to use this visualization">?</button>
            </h1>
            <p class="hero-evergreen-body">[TBD &mdash; evergreen tagline / mission statement that stays the same across every codebase rendered with this skill.]</p>
          </div>
        </div>
        <div class="hero-art">{HERO_PINEAPPLE_SVG}</div>
        <!-- The two stray crown leaves (.hero-leaf.one / .hero-leaf.two)
             and the four hero-meta chips (files / LOC / deps / symbols)
             were removed in batch 3 because they duplicated the metric
             cards below and floated detached from the pineapple body. -->
      </div>

      <!-- ============================================================= -->
      <!-- CODEBASE INTRO CARD                                            -->
      <!-- Codebase-specific content lives here (name + AI summary). It   -->
      <!-- sits between the evergreen hero and the metrics row so the    -->
      <!-- reader sees "what is this project?" before any numbers.        -->
      <!-- ============================================================= -->
      <section class="codebase-card" aria-labelledby="codebase-card-heading">
        <div class="codebase-card-inner">
          <span class="codebase-card-eyebrow">This codebase</span>
          <h2 id="codebase-card-heading" class="codebase-card-name">{esc(project)}</h2>
          <p class="codebase-card-summary" data-searchable>{emphasize(project_summary)}</p>
        </div>
      </section>

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

      <h2>Explore by Tab</h2>
      <p class="summary-grid-lede" data-searchable>Each card below jumps to its dedicated tab. Click any card to dive into that view of the codebase.</p>
      <div class="summary-grid">
        {summary_cards_html}
      </div>
    </section>

    <!-- ============================================================= -->
    <!-- TAB 2: PRODUCT                                                 -->
    <!-- ============================================================= -->
    <section class="tab-panel" id="panel-product" role="tabpanel">
      {panel_mode_toggle}

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
        {prod_arch_html}

        <h2>Design Patterns</h2>
        <div class="card-grid">{prod_patterns or '<article class="card" data-searchable><p>[AI_FILL: Design patterns — patterns found in the code (RBAC, pagination, rate limiting, etc.)]</p></article>'}</div>
      </div>

      <!-- Easy mode -->
      <div class="easy-only">
        <h2>What does this app do?</h2>
        <p data-searchable>{emphasize(prod_easy_what)}</p>

        <h2>How do people use it?</h2>
        <div class="diagram-container">
          <pre class="mermaid" data-original="{esc(workflow_mermaid_easy)}">{workflow_mermaid_easy}</pre>
        </div>

        <h2>What can users do?</h2>
        {prod_easy_capabilities or '<p data-searchable>[AI_FILL: Capability checklist — list what users can do]</p>'}

        <h2>How is the app organized?</h2>
        <p data-searchable>{emphasize(prod_easy_org)}</p>
      </div>

      <h2>Entry Points</h2>
      <ul>{entry_list}</ul>
    </section>

    <!-- ============================================================= -->
    <!-- TAB 3: TECHNICAL                                               -->
    <!-- ============================================================= -->
    <section class="tab-panel" id="panel-technical" role="tabpanel">
      {panel_mode_toggle}

      <!-- Developer mode -->
      <div class="dev-only">
        <h2>Architecture Diagram</h2>
        <div class="diagram-container">
          <pre class="mermaid" data-original="{esc(arch_mermaid)}">{arch_mermaid}</pre>
        </div>

        <h2>Backend Analysis</h2>
        {tech_backend_html}

        <h2>Frontend Analysis</h2>
        {tech_frontend_html}

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
        <p data-searchable>{emphasize(tech_easy_how)}</p>

        <h2>The main parts</h2>
        <div class="diagram-container">
          <pre class="mermaid" data-original="{esc(arch_mermaid_easy)}">{arch_mermaid_easy}</pre>
        </div>
        <p data-searchable>{emphasize(tech_easy_parts)}</p>

        <h2>How the parts connect</h2>
        <p data-searchable>{emphasize(tech_easy_connect)}</p>

        <h2>Code health check</h2>
        {health_legend_html}
        {health_html or '<p data-searchable>[AI_FILL: Code health check \u2014 four-tier ratings (Health / Sick / Severe Sick / Death) for organization, complexity, consistency, size]</p>'}
      </div>
    </section>

    <!-- ============================================================= -->
    <!-- TAB 4: DATABASE (conditional)                                  -->
    <!-- ============================================================= -->
    {"" if not has_database else f'''<section class="tab-panel" id="panel-database" role="tabpanel">
      {panel_mode_toggle}

      <!-- Developer mode -->
      <div class="dev-only">
        <h2>Schema Design</h2>
        <div class="diagram-container">
          <pre class="mermaid" data-original="{esc(db_er_mermaid)}">{db_er_mermaid or "erDiagram\\n  SCHEMA ||--|| PENDING : generate"}</pre>
        </div>

        <h2>Index Analysis</h2>
        {db_index_html}

        <h2>Query Patterns</h2>
        {db_query_html}

        <h2>Backend Integration</h2>
        {db_integration_html}

        {"" if not db_flow_mermaid else f"""<h2>Data Flow</h2>
        <div class="diagram-container">
          <pre class="mermaid" data-original="{esc(db_flow_mermaid)}">{db_flow_mermaid}</pre>
        </div>"""}
      </div>

      <!-- Easy mode -->
      <div class="easy-only">
        <h2>What data does the app store?</h2>
        <p data-searchable>{emphasize(db_easy_what)}</p>

        <h2>How is data organized?</h2>
        {"" if not db_er_mermaid_easy else f"""<div class="diagram-container">
          <pre class="mermaid" data-original="{esc(db_er_mermaid_easy)}">{db_er_mermaid_easy}</pre>
        </div>"""}

        <h2>How does the app talk to the database?</h2>
        <p data-searchable>{emphasize(db_easy_talk)}</p>

        <h2>Is the data safe?</h2>
        <p data-searchable>{emphasize(db_easy_safe)}</p>
      </div>
    </section>'''}

    <!-- ============================================================= -->
    <!-- TAB 5: SECURITY                                                -->
    <!-- ============================================================= -->
    <section class="tab-panel" id="panel-security" role="tabpanel">
      {panel_mode_toggle}

      <!-- Developer mode -->
      <div class="dev-only">
        <h2>Risk Summary</h2>
        <div class="risk-summary" role="list" aria-label="Risk summary by severity">
          <article class="risk-card risk-high" role="listitem" data-searchable>
            <div class="risk-card-glyph" aria-hidden="true">\U0001f6a8</div>
            <div class="risk-card-tier">High</div>
            <div class="risk-card-count">{high_count}</div>
            <div class="risk-card-label">Immediate action required</div>
          </article>
          <article class="risk-card risk-medium" role="listitem" data-searchable>
            <div class="risk-card-glyph" aria-hidden="true">\u26a0\ufe0f</div>
            <div class="risk-card-tier">Medium</div>
            <div class="risk-card-count">{med_count}</div>
            <div class="risk-card-label">Harden before production</div>
          </article>
          <article class="risk-card risk-low" role="listitem" data-searchable>
            <div class="risk-card-glyph" aria-hidden="true">\U0001f50d</div>
            <div class="risk-card-tier">Low</div>
            <div class="risk-card-count">{low_count}</div>
            <div class="risk-card-label">Best-practice gaps</div>
          </article>
        </div>

        <h2>Findings</h2>
        {findings_html}

        <h2>Authentication &amp; Authorization</h2>
        {sec_auth_html}

        <h2>Input Validation Audit</h2>
        {sec_validation_html}

        <h2>Dependency Risk</h2>
        {sec_deps_html}

        <h2>Scalability Analysis</h2>
        {sec_scale_html}
      </div>

      <!-- Easy mode -->
      <div class="easy-only">
        <h2>Is the app safe?</h2>
        {sec_easy_safe_html}

        <h2>What needs attention?</h2>
        <p data-searchable>{emphasize(sec_easy_attention)}</p>

        <h2>Who can access what?</h2>
        <p data-searchable>{emphasize(sec_easy_access)}</p>

        <h2>Can the app handle growth?</h2>
        <p data-searchable>{emphasize(sec_easy_growth)}</p>
      </div>
    </section>

    <!-- ============================================================= -->
    <!-- TAB 6: SUGGESTIONS                                             -->
    <!-- ============================================================= -->
    <section class="tab-panel" id="panel-suggestions" role="tabpanel">
      {panel_mode_toggle}

      <!-- Developer mode -->
      <div class="dev-only">
        <h2>Product Suggestions</h2>
        {SEASONING_LEGEND_HTML}
        <div class="card-grid suggestions-grid">{sug_product or '<article class="card" data-searchable><p>[AI_FILL: Product suggestions \u2014 feature gaps, missing UX flows, each with title, bullets, affected files, effort]</p></article>'}</div>

        <h2>Technical Suggestions</h2>
        <div class="card-grid suggestions-grid">{sug_technical or '<article class="card" data-searchable><p>[AI_FILL: Technical suggestions \u2014 refactoring, architecture improvements, test coverage gaps]</p></article>'}</div>

        <h2>Security Hardening</h2>
        <div class="card-grid suggestions-grid">{sug_security or '<article class="card" data-searchable><p>[AI_FILL: Security hardening \u2014 specific fixes with file paths and code-level guidance]</p></article>'}</div>

        <h2>Scalability Roadmap</h2>
        {roadmap_html or '<p data-searchable>[AI_FILL: Scalability roadmap \u2014 concrete ordered steps]</p>'}

        <h2>Priority Matrix</h2>
        {render_priority_items(sug_priority) or '<p data-searchable>[AI_FILL: Priority matrix \u2014 effort-vs-impact ranking]</p>'}
      </div>

      <!-- Easy mode -->
      <div class="easy-only">
        <h2>How to make the product better</h2>
        {sug_easy_product_html}

        <h2>How to make the code stronger</h2>
        {sug_easy_code_html}

        <h2>How to make it safer</h2>
        {sug_easy_safer_html}

        <h2>How to handle more users</h2>
        {sug_easy_growth_html}

        <h2>What to do first</h2>
        {sug_easy_first or '<p data-searchable>[AI_FILL: What to do first \u2014 prioritized action items: Do now / Do soon / Do later]</p>'}
      </div>
    </section>

    <!-- ============================================================= -->
    <!-- TAB 7: PITCH (Boss View only)                                  -->
    <!-- ============================================================= -->
    <section class="tab-panel pitch-panel" id="panel-pitch" role="tabpanel">
      {boss_view_panel_header}

      <h2 class="no-h2-deco pitch-section-title pitch-oneliner-title">The one-liner</h2>
      <div class="pitch-oneliner copyable-block" onclick="navigator.clipboard.writeText(this.innerText)" data-searchable>{pitch_oneliner_html}</div>

      <h2 class="no-h2-deco pitch-section-title">Tell your story</h2>
      <div class="pitch-story copyable-block" onclick="navigator.clipboard.writeText(this.innerText)" data-searchable>{pitch_story_html}</div>

      <h2 class="no-h2-deco pitch-section-title">Who is this for?</h2>
      {pitch_audience_html}

      <h2 class="no-h2-deco pitch-section-title">Why does this matter?</h2>
      {pitch_why_html}

      <h2 class="no-h2-deco pitch-section-title">What makes it special?</h2>
      {pitch_special_html}

      <h2 class="no-h2-deco pitch-section-title">Architecture Strengths</h2>
      {pitch_strengths_html}

      <h2 class="no-h2-deco pitch-section-title">Tech Stack Justification</h2>
      {pitch_stack_html}

      <h2 class="no-h2-deco pitch-section-title">Integration Narrative</h2>
      {pitch_integration_html}
    </section>

    <!-- ============================================================= -->
    <!-- TAB 8: SIMULATION (Boss View only)                             -->
    <!-- ============================================================= -->
    <section class="tab-panel simulation-panel" id="panel-simulation" role="tabpanel">
      {boss_view_panel_header}

      <h2 class="no-h2-deco sim-section-title sim-takeoff-title">What if it takes off?</h2>
      <div class="sim-takeoff-card">{sim_takeoff_html}</div>

      <h2 class="no-h2-deco sim-section-title">What comes next?</h2>
      <div class="card-grid sim-next-grid">{sim_next_html or '<article class="card" data-searchable><p>[AI_FILL: What comes next \u2014 feature cards: title + bullets in product language with **bold** highlights]</p></article>'}</div>

      <h2 class="no-h2-deco sim-section-title">Growing pains to watch for</h2>
      {sim_pains_html}

      <h2 class="no-h2-deco sim-section-title">The big picture</h2>
      {sim_big_html}
    </section>

  </main>
</div>

<aside class="credits" aria-label="Credits">
  <div class="credits-line credits-team">designed by the <strong>PineApple Team</strong></div>
  <div class="credits-line">
    <span class="credits-handle">@HenryZou</span>
    <a class="credits-link" href="https://www.linkedin.com/in/cunhanzou/" target="_blank" rel="noopener noreferrer"
       aria-label="Henry Zou on LinkedIn" title="Henry Zou on LinkedIn">
      <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
        <path d="M20.45 20.45h-3.55v-5.57c0-1.33-.02-3.04-1.85-3.04-1.86 0-2.14 1.45-2.14 2.95v5.66H9.36V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 1 1 0-4.12 2.06 2.06 0 0 1 0 4.12zM7.12 20.45H3.56V9h3.56v11.45zM22.23 0H1.77C.79 0 0 .77 0 1.72v20.56C0 23.23.79 24 1.77 24h20.46c.98 0 1.77-.77 1.77-1.72V1.72C24 .77 23.21 0 22.23 0z"/>
      </svg>
    </a>
  </div>
  <div class="credits-line">
    <span class="credits-handle">@JennyZheng</span>
    <a class="credits-link" href="https://www.linkedin.com/in/jenzheny/" target="_blank" rel="noopener noreferrer"
       aria-label="Jenny Zheng on LinkedIn" title="Jenny Zheng on LinkedIn">
      <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
        <path d="M20.45 20.45h-3.55v-5.57c0-1.33-.02-3.04-1.85-3.04-1.86 0-2.14 1.45-2.14 2.95v5.66H9.36V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 1 1 0-4.12 2.06 2.06 0 0 1 0 4.12zM7.12 20.45H3.56V9h3.56v11.45zM22.23 0H1.77C.79 0 0 .77 0 1.72v20.56C0 23.23.79 24 1.77 24h20.46c.98 0 1.77-.77 1.77-1.72V1.72C24 .77 23.21 0 22.23 0z"/>
      </svg>
    </a>
  </div>
  <div class="credits-line credits-year">2026</div>
</aside>

<script>
  // === MERMAID INIT ===
    mermaid.initialize({{
    startOnLoad: false,
    theme: 'base',
    securityLevel: 'loose',
    /* useMaxWidth:false keeps every diagram at its NATURAL pixel size so
       small diagrams (e.g. the module dependency graph, the easy-mode
       'main parts' graph, the ER schema) don't stretch to 100% container
       width and balloon their text relative to larger architecture
       diagrams. CSS in `.diagram-container .mermaid svg` clamps oversize
       diagrams to the container with horizontal scroll, so this is safe. */
    flowchart: {{ useMaxWidth: false, htmlLabels: true, curve: 'basis' }},
    er: {{ useMaxWidth: false }},
    sequence: {{ useMaxWidth: false }},
    gantt: {{ useMaxWidth: false }},
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
    /* Batch 4: switching to ANY non-Overview tab resets the audience
       view to "Developer View" so users always see the technical content
       first when they navigate. The Overview tab has no mode split, so
       we leave the toggle state alone for it. */
    if (tabId !== 'overview') {{
      setMode('dev');
    }}
    document.querySelectorAll('.tab-btn').forEach((btn) => btn.classList.toggle('active', btn.dataset.tab === tabId));
    document.querySelectorAll('.tab-panel').forEach((panel) => panel.classList.toggle('active', panel.id === 'panel-' + tabId));
    renderVisibleMermaid(document.getElementById('panel-' + tabId));
  }}

  /* goToTab is what the Overview summary cards call. It does the same
     work as switchTab() but ALSO scrolls the main content area back to
     the top of the page so the user lands at the panel-header / first
     heading of the destination tab instead of mid-scroll. */
  function goToTab(tabId) {{
    switchTab(tabId);
    requestAnimationFrame(() => {{
      const main = document.querySelector('.main-content') || document.documentElement;
      try {{
        main.scrollTo({{ top: 0, behavior: 'smooth' }});
      }} catch (_) {{
        main.scrollTop = 0;
      }}
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
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

  /* Make Overview summary cards keyboard-activatable. They have
     role="link" + tabindex="0", so Enter / Space should trigger their
     onclick goToTab() handler. */
  document.querySelectorAll('.summary-link-card').forEach((el) => {{
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

  // === MODE TOGGLE (Developer View / General View) ===
  function setMode(mode) {{
    document.body.classList.toggle('easy-mode', mode === 'easy');
    document.querySelectorAll('.mode-toggle [data-mode]').forEach((btn) => {{
      btn.classList.toggle('active', btn.getAttribute('data-mode') === mode);
    }});
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
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    const map = {{ {key_map_js} }};
    if (map[e.key]) {{ switchTab(map[e.key]); return; }}
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
