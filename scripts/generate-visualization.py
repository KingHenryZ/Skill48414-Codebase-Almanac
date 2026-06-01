#!/usr/bin/env python3
"""
generate-visualization.py

Generate a single self-contained HTML code visualization from an analysis JSON
produced by `scripts/extract-codebase.py`. Follows the contracts in SKILL.md
and visualization-base.css.

Usage:
  python scripts/generate-visualization.py <analysis.json> <output.html> [title] [project_name] [--no-open]
"""

from __future__ import annotations

import html
import json
import os
import re
import subprocess
import sys
import webbrowser
from pathlib import Path


def _open_generated_html(path: Path) -> None:
    """Open the visualization in the user's default handler (browser on desktop)."""

    resolved = path.resolve()
    if not resolved.is_file():
        return
    try:
        if sys.platform == "darwin":
            subprocess.run(["open", str(resolved)], check=False)
        elif sys.platform == "win32":
            os.startfile(str(resolved))  # type: ignore[attr-defined]
        else:
            webbrowser.open(resolved.as_uri())
    except Exception:
        pass


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

/* Floating tropical emoji strip (real element — allows layered waves; see markup after <body>) */
.tropical-top-banner {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 500;
  pointer-events: none;
  overflow: hidden;
  border-bottom: 3px solid var(--rind);
  box-shadow: 0 2px 10px rgba(92, 58, 26, 0.25);
  background-image: linear-gradient(
    90deg,
    #F4A300 0%,
    #FFD700 22%,
    #4CAF50 48%,
    #FFD700 74%,
    #F4A300 100%
  );
  background-size: 200% 100%;
  animation: tropicalBannerGradientWave 26s linear infinite;
}
@keyframes tropicalBannerGradientWave {
  0% { background-position: 0% 50%; }
  100% { background-position: 200% 50%; }
}

/* Sliding wave tiles along the bottom of the banner */
.tropical-top-banner-wave {
  position: absolute;
  left: -5%;
  right: -5%;
  bottom: 0;
  height: 72%;
  min-height: 20px;
  opacity: 0.85;
  background-image:
    url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 120 28' preserveAspectRatio='none'%3E%3Cpath fill='%23ffffff' fill-opacity='0.14' d='M0 16 Q30 8 60 16 T120 16 L120 28 L0 28z'/%3E%3C/svg%3E"),
    url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 120 28' preserveAspectRatio='none'%3E%3Cpath fill='%231b3d0c' fill-opacity='0.10' d='M0 14 Q30 22 60 14 T120 14 L120 28 L0 28z'/%3E%3C/svg%3E");
  background-repeat: repeat-x, repeat-x;
  background-position: 0 100%, 60px 100%;
  background-size: 180px 100%, 220px 100%;
  animation: tropicalBannerSeaWave 9s linear infinite;
}
@keyframes tropicalBannerSeaWave {
  0% { transform: translate3d(0, 0, 0); }
  100% { transform: translate3d(-180px, 0, 0); }
}

/* Gentle vertical swell on emojis — same as visualization-20260517-032213 (whole-row bob) */
.tropical-top-banner-emoji {
  display: block;
  position: relative;
  z-index: 1;
  padding: 8px 12px 10px;
  font-size: 18px;
  line-height: 1.35;
  /* 032213 used 10px letter-spacing — widened further between glyphs */
  letter-spacing: 22px;
  text-align: center;
  white-space: nowrap;
  text-shadow:
    0 1px 0 rgba(255, 250, 220, 0.45),
    0 2px 8px rgba(92, 58, 26, 0.28);
  animation: tropicalBannerEmojiBob 3.6s ease-in-out infinite;
}
@keyframes tropicalBannerEmojiBob {
  0%, 100% { transform: translate3d(0, 0, 0); }
  50%      { transform: translate3d(0, -4px, 0); }
}

@media (prefers-reduced-motion: reduce) {
  .tropical-top-banner,
  .tropical-top-banner-wave,
  .tropical-top-banner-emoji {
    animation: none !important;
  }
  .tropical-top-banner-wave {
    opacity: 0.55;
    transform: none;
  }
}
@media print {
  .tropical-top-banner {
    display: none !important;
  }
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

/* ═══ Team intro banner (above pineapple / 48414 hero) ═══ */
.team-intro-banner {
  margin: 0 -32px 18px;
  padding-block-start: clamp(14px, 2.15vw, 22px);
  padding-block-end: clamp(10px, 1.35vw, 15px);
  padding-inline-start: clamp(14px, 2.8vw, 26px);
  padding-inline-end: clamp(22px, 3.6vw, 40px);
  border-radius: 18px;
  border: 2px solid rgba(212, 160, 23, 0.65);
  background:
    linear-gradient(
      105deg,
      rgba(76, 175, 80, 0.22) 0%,
      rgba(255, 236, 179, 0.92) 38%,
      rgba(255, 249, 230, 0.98) 72%
    ),
    var(--pineapple-skin-thick);
  background-size: auto, 96px 32px;
  box-shadow:
    0 10px 28px rgba(139, 90, 43, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.75),
    inset 0 -1px 0 rgba(139, 90, 43, 0.08);
  display: grid;
  grid-template-columns: fit-content(10.75rem) minmax(0, 1fr);
  column-gap: clamp(24px, 4.8vw, 52px);
  row-gap: 10px;
  align-items: start;
  position: relative;
  isolation: isolate;
  overflow: hidden;
}
.team-intro-banner::before {
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
.team-intro-banner > * {
  position: relative;
  z-index: 1;
}
.team-banner-title-cell {
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  min-width: 0;
  margin-top: calc(-1 * clamp(22px, 3.2vw, 38px));
}
.team-banner-title {
  font-family: var(--font-heading);
  font-weight: 900;
  font-size: clamp(1.25rem, 2.65vw, 1.92rem);
  line-height: 1.18;
  letter-spacing: -0.02em;
  color: var(--leaf-deep);
  margin: 0;
  padding: 2px 0 0;
  max-width: 10.75rem;
  text-shadow: 0 1px 0 rgba(255, 255, 255, 0.45);
}
.team-banner-body {
  font-family: var(--font-body);
  font-size: clamp(0.9rem, 1.32vw, 1.03rem);
  line-height: 1.62;
  color: var(--text-secondary);
  margin: 0;
  padding: 2px 0 0;
  max-width: none;
  text-wrap: balance;
  padding-inline-start: clamp(12px, 2.8vw, 32px);
  border-inline-start: 1px solid rgba(139, 90, 43, 0.12);
}
@media (max-width: 680px) {
  .team-intro-banner {
    grid-template-columns: 1fr;
    padding-inline-start: clamp(16px, 3.2vw, 28px);
    padding-inline-end: clamp(16px, 3.2vw, 28px);
  }
  .team-banner-title-cell {
    align-items: flex-start;
    margin-top: 0;
  }
  .team-banner-title {
    align-self: stretch;
    max-width: none;
  }
  .team-banner-body {
    padding-inline-start: 0;
    border-inline-start: none;
  }
}

/* ═══ HERO ═══ */

.hero {
  position: relative;
  isolation: isolate;
  margin: -28px -32px 0;
  padding: clamp(40px, 6vw, 80px) clamp(32px, 6vw, 84px) clamp(52px, 7vw, 96px);
  min-height: 460px;
  border-radius: 0 0 0 0;
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
  align-self: stretch;
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
  animation: none;
}
.hero-pineapple {
  width: 100%;
  height: auto;
  display: block;
}
@keyframes heroFloat {
  0%, 100% { transform: rotate(6deg) translateY(0); }
  50%      { transform: rotate(5deg) translateY(-14px); }
}

/* Decorative overlapping floating leaves poking over content */
.hero-leaf {
  position: absolute;
  pointer-events: none;
  z-index: 3;
  filter: drop-shadow(0 6px 10px rgba(46, 125, 50, 0.35));
  display: none;
}
.hero-leaf.one   { top: 20px;   left: 44%; width: 90px;  transform: rotate(-18deg); opacity: 0.9; }
.hero-leaf.two   { bottom: 60px; left: 36%; width: 70px; transform: rotate(28deg); opacity: 0.85; }

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
  display: flex;
  flex-direction: column;
  height: 100%;
}
.hero-evergreen-title {
  font-size: clamp(2rem, 4vw, 3.2rem) !important;
  line-height: 1.35;
  margin: 0 0 18px !important;
  display: flex;
  flex-direction: column;
  gap: 6px;
  text-shadow: none;
  /* Cancel the global h1 gradient-text + ::after decoration bar
     so each span's own color wins. */
  background: none !important;
  -webkit-background-clip: initial !important;
  background-clip: initial !important;
  -webkit-text-fill-color: initial !important;
  padding-bottom: 0 !important;
}
.hero-evergreen-title::after { display: none !important; }
.hero-title-main,
.hero-title-sub {
  background: none !important;
  -webkit-background-clip: initial !important;
  background-clip: initial !important;
  -webkit-text-fill-color: currentColor !important;
  text-shadow: none;
}
.hero-title-main {
  font-family: var(--font-heading);
  font-weight: 800;
  font-style: normal;
  font-size: 1em;
  line-height: 1.15;
  letter-spacing: -0.02em;
  color: var(--leaf-deep);
  white-space: nowrap;
}
.hero-title-sub {
  font-family: var(--font-heading);
  font-weight: 600;
  font-style: italic;
  font-size: 0.5em;
  line-height: 1.35;
  letter-spacing: 0.005em;
  color: var(--leaf-deep);
  opacity: 0.78;
  display: inline-block;
  width: max-content;
  max-width: min(100%, 42rem);
}
/* Pineapple-skin geometric underline (same motif as section dividers). */
.hero-title-sub::after {
  content: "";
  display: block;
  height: clamp(14px, 2.35vw, 22px);
  width: 100%;
  margin: 10px 0 0;
  border: 0;
  border-radius: 0;
  background-image: var(--pineapple-skin-thick);
  background-repeat: repeat-x;
  background-position: left center;
  background-size: auto 100%;
  filter: drop-shadow(0 1px 2px rgba(139, 90, 43, 0.22));
  opacity: 0.95;
}
.hero-evergreen-body {
  font-family: var(--font-body);
  font-size: 1rem;
  line-height: 1.55;
  color: var(--text-secondary);
  margin: 0;
  max-width: 56ch;
}
.hero-evergreen .hero-evergreen-body + .hero-evergreen-body {
  margin-top: 0.85em;
}
.hero-team-section {
  margin-top: auto;
  padding-top: 18px;
}
.hero-team-subtitle {
  font-family: var(--font-heading);
  font-weight: 700;
  font-size: 0.82rem;
  letter-spacing: 0.04em;
  color: var(--leaf-deep);
  opacity: 0.7;
  margin: 0 0 6px;
  text-transform: uppercase;
}
.hero-team-intro {
  font-family: var(--font-body);
  font-size: 0.82rem;
  line-height: 1.5;
  color: var(--text-secondary);
  margin: 0;
  max-width: 56ch;
  opacity: 0.85;
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
  margin: 0 auto 32px;
  padding: 4px;
  border-radius: 0 0 28px 28px;
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

/* Overview only: Language Breakdown → Explore by Tab */
#panel-overview .lang-bar-container {
  margin-bottom: 2px;
}
#panel-overview .lang-bar-container + h2 {
  margin-top: 0.95em;
  padding-top: 12px;
  background-size: auto 14px;
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
  overflow: visible;
}
/* Decorative halo sits top-right on generic cards — that overlaps the
   right-aligned tab title on Overview link cards, so park it bottom-left. */
.summary-link-card::before {
  top: auto;
  right: auto;
  bottom: -48px;
  left: -48px;
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
  flex: 1;
  min-width: 0;
  font-family: var(--font-heading) !important;
  font-weight: 700;
  font-size: clamp(1.2rem, 1.6vw, 1.55rem) !important;
  letter-spacing: -0.01em;
  line-height: 1.15;
  margin: 0;
  color: var(--leaf-deep);
  text-align: right;
  overflow-wrap: break-word;
  word-break: normal;
  hyphens: auto;
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
   Health / Sick / Critically Ill / Death Penalty scale that uses the warm pineapple
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

/* === Boss View glow (Pitch + Simulation) ============================
   TranslateY lift + colored box-shadow halo tinted in pineapple gold
   so it matches the theme. Applied to both .pitch-panel and
   .simulation-panel so the single decorative "Boss View" pill pulses on both tabs. Selector
   includes `.panel-header` and `button.active` so it beats
   `.panel-header .mode-toggle button.active` further down the
   stylesheet. The pill is non-interactive, so the glow is always-on
   with a gentle pulse for visibility. Respects prefers-reduced-motion. */
.pitch-panel .panel-header .mode-toggle.boss-view-toggle > button.active,
.pitch-panel .panel-header .mode-toggle.boss-view-toggle > button,
.simulation-panel .panel-header .mode-toggle.boss-view-toggle > button.active,
.simulation-panel .panel-header .mode-toggle.boss-view-toggle > button {
  transform: translateY(-1px);
  box-shadow:
    0 2px 0 var(--rind),
    0 0 0 1.5px rgba(255, 215, 0, 0.7),
    0 4px 16px rgba(255, 215, 0, 0.6),
    0 0 32px rgba(255, 179, 0, 0.45);
  animation: bossViewPulse 2.4s ease-in-out infinite;
}
@keyframes bossViewPulse {
  0%, 100% {
    box-shadow:
      0 2px 0 var(--rind),
      0 0 0 1.5px rgba(255, 215, 0, 0.7),
      0 4px 16px rgba(255, 215, 0, 0.6),
      0 0 32px rgba(255, 179, 0, 0.45);
  }
  50% {
    box-shadow:
      0 2px 0 var(--rind),
      0 0 0 2px rgba(255, 215, 0, 0.95),
      0 6px 26px rgba(255, 215, 0, 0.95),
      0 0 56px rgba(255, 179, 0, 0.7);
  }
}
@media (prefers-reduced-motion: reduce) {
  .pitch-panel .panel-header .mode-toggle.boss-view-toggle > button.active,
  .pitch-panel .panel-header .mode-toggle.boss-view-toggle > button,
  .simulation-panel .panel-header .mode-toggle.boss-view-toggle > button.active,
  .simulation-panel .panel-header .mode-toggle.boss-view-toggle > button {
    animation: none;
  }
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


# ── Pineapple scale grid generator ─────────────────────────────────────
# Builds an explicit grid of <rect> scales for the pineapple body. Each
# scale is colored either "scale-yellow" (the 8-count spiral direction,
# warm golden #FFD700) or "scale-green" (the 13-count spiral direction,
# deep jungle #2D4A2D), assigned by parity of (col+row) so adjacent
# diagonals alternate. The whole grid is rotated 45° around the body
# center via a parent <g transform>, so each square becomes an upright
# interlocking diamond, with seam grooves stroked in near-black #0D1A0D.

_TILE = 56  # was 36 — bumped to match a real pineapple's eye density.
            # Real pineapples display Fibonacci phyllotactic spirals
            # of 8 / 13 / 21 (gradual / medium / steep slope), totalling
            # ~100 visible eyes on one side. With tile=56 and the body
            # silhouette mask, this grid produces ~80-100 visible scales
            # whose diagonal counts roughly approximate that pattern
            # (~6-9 along the gradual diagonal, ~9-13 along the steeper
            # one). True golden-angle phyllotaxis would require a
            # Vogel-spiral placement, but a 45°-rotated square grid
            # at this tile size lands in the right visual neighborhood.
_GRID_RADIUS = 380  # pre-rotation half-extent (must cover body after 45°)
_GRID_CX, _GRID_CY = 320, 585
_GRID_N = _GRID_RADIUS // _TILE + 1


def _build_pineapple_scales_html() -> str:
    rects = []
    for col in range(-_GRID_N, _GRID_N + 1):
        for row in range(-_GRID_N, _GRID_N + 1):
            x = _GRID_CX + col * _TILE - _TILE / 2
            y = _GRID_CY + row * _TILE - _TILE / 2
            cls = "scale-yellow" if (col + row) % 2 == 0 else "scale-green"
            rects.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" '
                f'width="{_TILE}" height="{_TILE}" class="{cls}"/>'
            )
    return "\n        ".join(rects)


def _build_pineapple_intersection_dots_html() -> str:
    """Tiny dark circles at every grid corner — the shadow pockets where
    four scales meet. After the parent 45° rotation these land exactly
    on the X-junction between adjacent diamonds."""
    dots = []
    for col in range(-_GRID_N, _GRID_N + 1):
        for row in range(-_GRID_N, _GRID_N + 1):
            x = _GRID_CX + col * _TILE
            y = _GRID_CY + row * _TILE
            dots.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" '
                f'r="1.6" class="scale-pocket"/>'
            )
    return "\n        ".join(dots)


def _build_pineapple_dome_scales_html() -> str:
    """Build per-scale rects for the raised-dome pineapple skin.

    Each scale carries a class `.dome-tN` (N=0..3) chosen by the
    scale's SCREEN-SPACE distance from an upper-center light source.
    Closer to the light → lower tier index → brighter dome gradient.
    Rects are inset inside their grid cells so the dark body fills
    the gaps as deep carved groove channels.

    Critically, we compute the screen position by applying the same
    +45° rotation that the parent <g transform="rotate(45 320 585)">
    will apply at render time — so a scale that LOOKS like it sits
    at the top of the body in screen space gets the bright tier even
    though its pre-rotation grid coords don't reflect that directly.
    """
    import math
    cos45 = math.cos(math.radians(45))
    sin45 = math.sin(math.radians(45))

    light_cx, light_cy = 320, 380     # upper-center of the body
    inset = 2.5                        # px of pre-rotation gap on each side
    half = _TILE / 2

    # Tier thresholds (px from light source in screen space).
    t0_max = 175  # bright top zone
    t1_max = 280  # upper-mid
    t2_max = 380  # lower-mid

    rects = []
    for col in range(-_GRID_N, _GRID_N + 1):
        for row in range(-_GRID_N, _GRID_N + 1):
            x = _GRID_CX + col * _TILE - half + inset
            y = _GRID_CY + row * _TILE - half + inset
            w = _TILE - 2 * inset

            # Project the scale center through the parent rotation so
            # the lighting tier matches what we'll see on screen.
            ox = col * _TILE
            oy = row * _TILE
            sx = _GRID_CX + ox * cos45 - oy * sin45
            sy = _GRID_CY + ox * sin45 + oy * cos45
            dist = math.hypot(sx - light_cx, sy - light_cy)
            if dist < t0_max:
                tier = 0
            elif dist < t1_max:
                tier = 1
            elif dist < t2_max:
                tier = 2
            else:
                tier = 3

            rects.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" '
                f'width="{w:.1f}" height="{w:.1f}" class="dome-t{tier}"/>'
            )
    return "\n        ".join(rects)


def _build_pineapple_crystal_facets_html() -> str:
    """Per-scale rendering for the prismatic crystal pineapple.

    Each scale is deterministically assigned one of four brightness
    tiers — bright near-white / lit gold / mid amber / deep amber —
    based on a pseudo-random stable per-cell hash. Stable seed means
    the shimmer pattern is identical across runs (no diff churn). The
    distribution is biased toward the mid tiers so bright facets
    really pop as accents and dark facets read as deep shadow pockets.
    """
    import random
    rng = random.Random(48414)  # stable seed → identical pattern every run
    rects = []
    for col in range(-_GRID_N, _GRID_N + 1):
        for row in range(-_GRID_N, _GRID_N + 1):
            x = _GRID_CX + col * _TILE - _TILE / 2
            y = _GRID_CY + row * _TILE - _TILE / 2
            r = rng.random()
            # Distribution: 18% bright / 32% lit / 32% mid / 18% deep.
            if r < 0.18:
                tier = 0
            elif r < 0.50:
                tier = 1
            elif r < 0.82:
                tier = 2
            else:
                tier = 3
            rects.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" '
                f'width="{_TILE}" height="{_TILE}" class="facet-t{tier}"/>'
            )
    return "\n        ".join(rects)


_PINEAPPLE_SCALES_HTML = _build_pineapple_scales_html()
_PINEAPPLE_POCKETS_HTML = _build_pineapple_intersection_dots_html()
_PINEAPPLE_CRYSTAL_FACETS_HTML = _build_pineapple_crystal_facets_html()
_PINEAPPLE_DOME_SCALES_HTML = _build_pineapple_dome_scales_html()


def _build_pineapple_fibonacci_spirals_html() -> str:
    """Build three Fibonacci-spiral overlay families (8 / 13 / 21).

    Each family is a set of parallel straight line segments spanning
    the body silhouette at a specific slope. Lines are clipped to the
    body via the parent <g clip-path>, so they always end at the
    pineapple's edge no matter how the spirals are angled.

    Slopes are chosen to evoke real pineapple phyllotaxis:
      • 8 spirals  ↘  gentle ~28° slope (the gradual diagonal)
      • 13 spirals ↗  medium ~55° slope (the steeper diagonal)
      • 21 spirals │  near-vertical ~82° (the parallel ribs)
    """
    import math

    cx, cy = _SPIRAL_BODY_CX, _SPIRAL_BODY_CY
    rx, ry = _SPIRAL_BODY_RX, _SPIRAL_BODY_RY  # body half-axes

    def lines_at_slope(angle_deg: float, count: int, family: str) -> str:
        angle_rad = math.radians(angle_deg)
        dx = math.cos(angle_rad)
        dy = math.sin(angle_rad)
        # Perpendicular direction (for spacing the parallel lines).
        px, py = -dy, dx
        # True perpendicular extent of an ellipse at this angle:
        # max |px*x + py*y| over the ellipse = sqrt((px*rx)² + (py*ry)²).
        # Using this exact extent (instead of the bounding-box projection)
        # ensures every offset lands inside the body so all 8/13/21 lines
        # actually intersect the silhouette.
        max_perp = math.hypot(px * rx, py * ry)
        out = []
        for i in range(count):
            t = (i + 0.5) / count - 0.5  # span -0.5 → +0.5
            # Inset to 0.92 keeps even the outermost lines well inside
            # the body (the extreme tangent lines can still be skipped
            # by the discriminant check below if they fall just outside).
            offset = t * 2 * max_perp * 0.92
            ox = cx + px * offset
            oy = cy + py * offset
            # Intersect line (ox + dx*s, oy + dy*s) with body ellipse.
            ax = (ox - cx) / rx
            ay = (oy - cy) / ry
            bx = dx / rx
            by = dy / ry
            A = bx * bx + by * by
            B = 2 * (ax * bx + ay * by)
            C = ax * ax + ay * ay - 1
            discr = B * B - 4 * A * C
            if discr <= 0:
                continue  # line misses the body
            sd = math.sqrt(discr)
            s1 = (-B - sd) / (2 * A)
            s2 = (-B + sd) / (2 * A)
            x1 = ox + dx * s1
            y1 = oy + dy * s1
            x2 = ox + dx * s2
            y2 = oy + dy * s2
            out.append(
                f'<line x1="{x1:.1f}" y1="{y1:.1f}" '
                f'x2="{x2:.1f}" y2="{y2:.1f}" '
                f'class="spiral-line spiral-{family}"/>'
            )
        return "\n          ".join(out)

    fam8 = lines_at_slope(28, 8, "f8")
    fam13 = lines_at_slope(55, 13, "f13")
    fam21 = lines_at_slope(82, 21, "f21")
    return (
        '<g class="spiral-family-8" data-count="8">\n          '
        + fam8 + '\n        </g>\n        '
        '<g class="spiral-family-13" data-count="13">\n          '
        + fam13 + '\n        </g>\n        '
        '<g class="spiral-family-21" data-count="21">\n          '
        + fam21 + '\n        </g>'
    )


# Original geometry — matches the generated SVG body silhouette.
_SPIRAL_BODY_CX, _SPIRAL_BODY_CY = 320, 580
_SPIRAL_BODY_RX, _SPIRAL_BODY_RY = 248, 298
_PINEAPPLE_FIBONACCI_SPIRALS_HTML = _build_pineapple_fibonacci_spirals_html()

# Photo geometry — fit to the cropped crystal pineapple sculpture
# (taller, slightly narrower than the earlier warm-gold reference).
# Photo is placed at x=40 y=80 w=560 h=800; within it the body
# (no crown) sits roughly x≈170..505, y≈395..855, giving an
# ellipse center (337, 625) with rx≈170 ry≈230.
_SPIRAL_BODY_CX, _SPIRAL_BODY_CY = 337, 625
_SPIRAL_BODY_RX, _SPIRAL_BODY_RY = 170, 225
_PINEAPPLE_FIBONACCI_SPIRALS_PHOTO_HTML = _build_pineapple_fibonacci_spirals_html()


def _build_pineapple_natural_skin_html() -> str:
    """Build per-scale rects + per-scale eye dots for a realistic
    pineapple skin (matte naturalistic palette, not glassy crystal).

    Each scale gets a class `.natural-tN` (N=0..3) chosen by SCREEN-
    SPACE distance from the upper-center light source — same lighting
    logic as the dome skin, but the per-tier gradients are tuned to
    natural pineapple colors (warm gold center → greenish-brown edge),
    and a small dark eye dot is placed at every scale center to mimic
    the dried bract you see on real fruit.
    """
    import math
    cos45 = math.cos(math.radians(45))
    sin45 = math.sin(math.radians(45))

    light_cx, light_cy = 320, 380
    inset = 2.0
    half = _TILE / 2

    # Subtler tier banding than the crystal version — real pineapples
    # don't have dramatic light/shadow ranges across their skin.
    t0_max = 200
    t1_max = 310
    t2_max = 410

    scales = []
    eyes = []
    for col in range(-_GRID_N, _GRID_N + 1):
        for row in range(-_GRID_N, _GRID_N + 1):
            x = _GRID_CX + col * _TILE - half + inset
            y = _GRID_CY + row * _TILE - half + inset
            w = _TILE - 2 * inset

            # Project to screen position so the lighting matches what
            # you'll actually see after the parent's 45° rotation.
            ox = col * _TILE
            oy = row * _TILE
            sx = _GRID_CX + ox * cos45 - oy * sin45
            sy = _GRID_CY + ox * sin45 + oy * cos45
            dist = math.hypot(sx - light_cx, sy - light_cy)
            if dist < t0_max:
                tier = 0
            elif dist < t1_max:
                tier = 1
            elif dist < t2_max:
                tier = 2
            else:
                tier = 3

            scales.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" '
                f'width="{w:.1f}" height="{w:.1f}" class="natural-t{tier}"/>'
            )
            # Eye dot at scale center (in the same pre-rotation coords
            # so it rotates with the grid and stays centered visually).
            eye_x = _GRID_CX + col * _TILE
            eye_y = _GRID_CY + row * _TILE
            eyes.append(
                f'<circle cx="{eye_x:.1f}" cy="{eye_y:.1f}" '
                f'r="2.4" class="scale-eye"/>'
            )
    return (
        "\n        ".join(scales)
        + "\n\n        <!-- Eye dots — one per scale, at each scale's center -->\n        "
        + "\n        ".join(eyes)
    )


_PINEAPPLE_NATURAL_SKIN_HTML = _build_pineapple_natural_skin_html()


def _build_pineapple_premium_skin_html() -> str:
    """Build premium pineapple scales.

    Each scale is a pillowed diamond (cubic-bezier sides, slightly
    convex) placed on a brick-offset lattice in normalized (u, v)
    body coordinates. The lattice is then cylindrically warped so
    horizontal distances compress near the body edges (giving the
    fruit a real 3D barrel feel) and tapered at top/bottom so
    scales shrink near the poles. Each scale is assigned to one of
    eight gradient variants with row-based biasing (greener/cream
    near the top, warm honey in the middle, warm brown near the
    bottom) and per-scale pseudo-randomness, so no two scales look
    identical.

    Returns a string of <path class="psc-pN"/> elements.
    """
    import math
    import random

    cx, cy = 320, 580
    rx, ry = 244, 296

    # Scale geometry (screen pixels at u = 0).
    dia_w_max = 25.0
    dia_h = 17.0

    # Lattice spacing in normalized (u, v) coords. Tuned so the
    # visible diagonal counts roughly approximate a real pineapple
    # (Fibonacci 8 / 13 / 21).
    u_step = 0.155
    v_step = 0.082

    # Cylindrical wrap intensity. 1.0 → hemisphere (full edge
    # compression to zero); 0.94 keeps a bit of width at the edges
    # so the silhouette stays photogenic.
    wrap = 0.94
    wrap_norm = math.sin(wrap * math.pi / 2)

    rng = random.Random(48414)
    scales: list[str] = []

    # Walk enough rows / cols to cover the body in pre-warp space.
    r_max = int(1.4 / v_step) + 1
    c_max = int(1.4 / u_step) + 1

    for r in range(-r_max, r_max + 1):
        v_pre = r * v_step
        if abs(v_pre) > 1.04:
            continue
        # Brick offset every other row → creates the diagonal
        # Fibonacci-spiral visual alignment.
        row_offset = (u_step * 0.5) if (r & 1) else 0.0
        for c in range(-c_max, c_max + 1):
            u_pre = c * u_step + row_offset
            if abs(u_pre) > 1.04:
                continue
            # Skip outside the unit ellipse in pre-warp coords (with
            # a tiny buffer so the clip-path handles the silhouette).
            if u_pre * u_pre + v_pre * v_pre > 0.985:
                continue

            # Cylindrical horizontal warp.
            sx = cx + math.sin(u_pre * wrap * math.pi / 2) / wrap_norm * rx
            # Slight v warp: rows dip outward at the sides so the
            # band visually curves around the body.
            v_curve = v_pre * (1.0 + 0.05 * (u_pre * u_pre))
            sy = cy + v_curve * ry

            # Horizontal compression near body edges.
            compress = math.cos(u_pre * wrap * math.pi / 2)
            w = dia_w_max * compress
            # Vertical taper near top/bottom poles.
            pole_taper = max(0.62, 1.0 - abs(v_pre) * 0.42)
            w *= pole_taper
            h = dia_h * pole_taper

            # Drop the smallest fringe scales for cleaner edges.
            if w < 4.5:
                continue

            # Choose variant: row-based palette bias, then per-scale
            # randomization within the allowed pool.
            if v_pre < -0.45:
                pool = ("p4", "p4", "p3", "p0", "p1", "p7")
            elif v_pre > 0.45:
                pool = ("p5", "p5", "p2", "p6", "p1", "p2")
            else:
                pool = ("p0", "p1", "p3", "p6", "p7", "p1", "p0", "p3")
            variant = rng.choice(pool)

            # Pillowed-diamond path (cubic bezier on each side,
            # slightly convex toward the outside → soft, premium).
            d = (
                f"M {sx:.1f} {sy - h:.1f} "
                f"C {sx + w * 0.50:.1f} {sy - h * 0.92:.1f}, "
                f"{sx + w * 0.92:.1f} {sy - h * 0.50:.1f}, "
                f"{sx + w:.1f} {sy:.1f} "
                f"C {sx + w * 0.92:.1f} {sy + h * 0.50:.1f}, "
                f"{sx + w * 0.50:.1f} {sy + h * 0.92:.1f}, "
                f"{sx:.1f} {sy + h:.1f} "
                f"C {sx - w * 0.50:.1f} {sy + h * 0.92:.1f}, "
                f"{sx - w * 0.92:.1f} {sy + h * 0.50:.1f}, "
                f"{sx - w:.1f} {sy:.1f} "
                f"C {sx - w * 0.92:.1f} {sy - h * 0.50:.1f}, "
                f"{sx - w * 0.50:.1f} {sy - h * 0.92:.1f}, "
                f"{sx:.1f} {sy - h:.1f} Z"
            )
            scales.append(f'<path d="{d}" class="psc-{variant}"/>')

    return "\n        ".join(scales)


_PINEAPPLE_PREMIUM_SKIN_HTML = _build_pineapple_premium_skin_html()


def _build_pineapple_glass_skin_html() -> str:
    """Build translucent 3D-faceted GLASS scales.

    Each scale renders as four layered SVG elements (drawn in
    document order so light reads correctly):

      1. Pillowed-diamond fill with a translucent amber gradient
         (uses fill-opacity stops so the warm body backdrop is
         visible through every facet → glass effect).
      2. A subtle internal facet cross — four short lines from
         the scale center to each vertex, stroked in pale gold.
         This is the "cut gemstone" gimmick: it reads as the
         interior planes of a faceted crystal.
      3. A bright specular glint near the top-right peak of every
         large-enough scale, sized proportionally to the scale.
      4. (The pillowed-diamond border itself is handled via the
         shared `.gsc-g*` stroke rule in CSS — warm bright gold
         instead of dark grout, since the seams are RAISED edges
         catching light, not sunken grooves.)

    Layout, warp, and per-scale color biasing match the premium
    skin helper so the silhouette stays identical — only the
    surface material changes.
    """
    import math
    import random

    cx, cy = 320, 580
    rx, ry = 244, 296

    dia_w_max = 25.0
    dia_h = 17.0
    u_step = 0.155
    v_step = 0.082

    wrap = 0.94
    wrap_norm = math.sin(wrap * math.pi / 2)

    rng = random.Random(48414)
    pieces: list[str] = []

    r_max = int(1.4 / v_step) + 1
    c_max = int(1.4 / u_step) + 1

    for r in range(-r_max, r_max + 1):
        v_pre = r * v_step
        if abs(v_pre) > 1.04:
            continue
        row_offset = (u_step * 0.5) if (r & 1) else 0.0
        for c in range(-c_max, c_max + 1):
            u_pre = c * u_step + row_offset
            if abs(u_pre) > 1.04:
                continue
            if u_pre * u_pre + v_pre * v_pre > 0.985:
                continue

            sx = cx + math.sin(u_pre * wrap * math.pi / 2) / wrap_norm * rx
            v_curve = v_pre * (1.0 + 0.05 * (u_pre * u_pre))
            sy = cy + v_curve * ry

            compress = math.cos(u_pre * wrap * math.pi / 2)
            w = dia_w_max * compress
            pole_taper = max(0.62, 1.0 - abs(v_pre) * 0.42)
            w *= pole_taper
            h = dia_h * pole_taper
            if w < 4.5:
                continue

            # Glass palette: cooler/clearer at top, deep amber at
            # bottom, all amber-gold in the middle.
            if v_pre < -0.45:
                pool = ("g0", "g0", "g3", "g7", "g1")
            elif v_pre > 0.45:
                pool = ("g5", "g5", "g2", "g6", "g2")
            else:
                pool = ("g0", "g1", "g3", "g6", "g7", "g1", "g0", "g3")
            variant = rng.choice(pool)

            d = (
                f"M {sx:.1f} {sy - h:.1f} "
                f"C {sx + w * 0.50:.1f} {sy - h * 0.92:.1f}, "
                f"{sx + w * 0.92:.1f} {sy - h * 0.50:.1f}, "
                f"{sx + w:.1f} {sy:.1f} "
                f"C {sx + w * 0.92:.1f} {sy + h * 0.50:.1f}, "
                f"{sx + w * 0.50:.1f} {sy + h * 0.92:.1f}, "
                f"{sx:.1f} {sy + h:.1f} "
                f"C {sx - w * 0.50:.1f} {sy + h * 0.92:.1f}, "
                f"{sx - w * 0.92:.1f} {sy + h * 0.50:.1f}, "
                f"{sx - w:.1f} {sy:.1f} "
                f"C {sx - w * 0.92:.1f} {sy - h * 0.50:.1f}, "
                f"{sx - w * 0.50:.1f} {sy - h * 0.92:.1f}, "
                f"{sx:.1f} {sy - h:.1f} Z"
            )
            pieces.append(f'<path d="{d}" class="gsc-{variant}"/>')

            # Interior facet cross — 4 lines from center → vertex.
            # Reads as the internal planes of a cut gemstone.
            pieces.append(
                f'<line class="gsc-facet" x1="{sx:.1f}" y1="{sy:.1f}" '
                f'x2="{sx:.1f}" y2="{sy - h:.1f}"/>'
            )
            pieces.append(
                f'<line class="gsc-facet" x1="{sx:.1f}" y1="{sy:.1f}" '
                f'x2="{sx + w:.1f}" y2="{sy:.1f}"/>'
            )
            pieces.append(
                f'<line class="gsc-facet" x1="{sx:.1f}" y1="{sy:.1f}" '
                f'x2="{sx:.1f}" y2="{sy + h:.1f}"/>'
            )
            pieces.append(
                f'<line class="gsc-facet" x1="{sx:.1f}" y1="{sy:.1f}" '
                f'x2="{sx - w:.1f}" y2="{sy:.1f}"/>'
            )

            # Specular highlight — small white ellipse near the
            # upper-right vertex. Skip the tiniest scales so the
            # body doesn't end up over-speckled.
            if w > 8.0:
                glint_x = sx + w * 0.30
                glint_y = sy - h * 0.55
                glint_r = max(1.2, w * 0.11)
                pieces.append(
                    f'<ellipse class="gsc-glint" '
                    f'cx="{glint_x:.1f}" cy="{glint_y:.1f}" '
                    f'rx="{glint_r:.2f}" ry="{glint_r * 0.65:.2f}"/>'
                )

    return "\n        ".join(pieces)


_PINEAPPLE_GLASS_SKIN_HTML = _build_pineapple_glass_skin_html()


def _build_pineapple_glass_v2_skin_html() -> str:
    """Build photo-grade 3D-faceted glass scales.

    Each scale is constructed as FOUR triangular facets meeting at
    the scale center (true cut-gemstone topology), plus a thin
    bright-gold perimeter outline and a small white specular glint
    at the upper vertex.

    Light direction is fixed to upper-left, so the four facets get
    four different brightness classes (gv-ul brightest, gv-lr in
    deepest shadow). Per-scale variation comes from a brightness
    tier (gv-t0/t1/t2) chosen by deterministic random so no two
    scales look identical, exactly like a real crystal sculpture.

    Reuses the premium-variant warp / lattice / silhouette math so
    the underlying body shape stays consistent.
    """
    import math
    import random

    cx, cy = 320, 580
    rx, ry = 244, 296

    dia_w_max = 25.0
    dia_h = 17.0
    u_step = 0.155
    v_step = 0.082

    wrap = 0.94
    wrap_norm = math.sin(wrap * math.pi / 2)

    rng = random.Random(48414)
    pieces: list[str] = []

    r_max = int(1.4 / v_step) + 1
    c_max = int(1.4 / u_step) + 1

    for r in range(-r_max, r_max + 1):
        v_pre = r * v_step
        if abs(v_pre) > 1.04:
            continue
        row_offset = (u_step * 0.5) if (r & 1) else 0.0
        for c in range(-c_max, c_max + 1):
            u_pre = c * u_step + row_offset
            if abs(u_pre) > 1.04:
                continue
            if u_pre * u_pre + v_pre * v_pre > 0.985:
                continue

            sx = cx + math.sin(u_pre * wrap * math.pi / 2) / wrap_norm * rx
            v_curve = v_pre * (1.0 + 0.05 * (u_pre * u_pre))
            sy = cy + v_curve * ry

            compress = math.cos(u_pre * wrap * math.pi / 2)
            w = dia_w_max * compress
            pole_taper = max(0.62, 1.0 - abs(v_pre) * 0.42)
            w *= pole_taper
            h = dia_h * pole_taper
            if w < 4.5:
                continue

            # Per-scale brightness tier (mostly normal, a few dim).
            tier = rng.choice(("t0", "t0", "t0", "t0", "t1", "t1", "t2"))

            # Diamond vertices.
            tx, ty = sx, sy - h
            rxv, ryv = sx + w, sy
            bx, by = sx, sy + h
            lxv, lyv = sx - w, sy

            # 4 facet triangles, each meeting at scale center.
            # UL — center → left → top
            pieces.append(
                f'<path class="gv-ul gv-{tier}" '
                f'd="M {sx:.1f} {sy:.1f} L {lxv:.1f} {lyv:.1f} '
                f'L {tx:.1f} {ty:.1f} Z"/>'
            )
            # UR — center → top → right
            pieces.append(
                f'<path class="gv-ur gv-{tier}" '
                f'd="M {sx:.1f} {sy:.1f} L {tx:.1f} {ty:.1f} '
                f'L {rxv:.1f} {ryv:.1f} Z"/>'
            )
            # LL — center → bottom → left
            pieces.append(
                f'<path class="gv-ll gv-{tier}" '
                f'd="M {sx:.1f} {sy:.1f} L {bx:.1f} {by:.1f} '
                f'L {lxv:.1f} {lyv:.1f} Z"/>'
            )
            # LR — center → right → bottom
            pieces.append(
                f'<path class="gv-lr gv-{tier}" '
                f'd="M {sx:.1f} {sy:.1f} L {rxv:.1f} {ryv:.1f} '
                f'L {bx:.1f} {by:.1f} Z"/>'
            )
            # Bright perimeter outline (the raised gold ridges).
            pieces.append(
                f'<path class="gv-edge" '
                f'd="M {tx:.1f} {ty:.1f} L {rxv:.1f} {ryv:.1f} '
                f'L {bx:.1f} {by:.1f} L {lxv:.1f} {lyv:.1f} Z"/>'
            )
            # Specular glint at the top peak.
            if w > 7.5:
                glint_r = max(1.2, w * 0.13)
                pieces.append(
                    f'<ellipse class="gv-glint" '
                    f'cx="{tx:.1f}" cy="{ty + glint_r * 0.4:.1f}" '
                    f'rx="{glint_r:.2f}" ry="{glint_r * 0.55:.2f}"/>'
                )

    return "\n        ".join(pieces)


_PINEAPPLE_GLASS_V2_SKIN_HTML = _build_pineapple_glass_v2_skin_html()


# ── Hero illustration: pineapple in SVG ────────────────────────────────
# Crown leaves attach to a single point at (320, 360) on the body's
# upper rim. The body skin is a 45° interlocking diamond grid whose
# scales are individually colored on two alternating diagonals (yellow
# 8-spiral, green 13-spiral), with near-black seam grooves and a slow
# two-beat pulse that syncs yellow → green like a heartbeat.

# Legacy diamond-grid pineapple: flat golden body, brown 45° grid,
# orange center dots, dark green crown. Parked as inert reference so
# we can flip back to it later by re-assigning HERO_PINEAPPLE_SVG.
_HERO_PINEAPPLE_SVG_DIAMOND_GRID = """\
<svg class="hero-pineapple" viewBox="0 0 640 920" xmlns="http://www.w3.org/2000/svg"
     role="img" aria-hidden="true" preserveAspectRatio="xMidYMid meet">
  <defs>
    <!-- Bright golden body — flat-feeling yellow with a subtle warm
         shift toward amber at the edges. -->
    <radialGradient id="body-yellow" cx="42%" cy="32%" r="78%">
      <stop offset="0%"   stop-color="#FFE974"/>
      <stop offset="35%"  stop-color="#FFD700"/>
      <stop offset="80%"  stop-color="#F2C200"/>
      <stop offset="100%" stop-color="#E2A800"/>
    </radialGradient>

    <!-- Specular sheen: tight bright spot upper-left for surface gloss -->
    <radialGradient id="body-sheen" cx="32%" cy="26%" r="22%">
      <stop offset="0%"   stop-color="#FFFFFF" stop-opacity="0.55"/>
      <stop offset="60%"  stop-color="#FFFFFF" stop-opacity="0.10"/>
      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0"/>
    </radialGradient>

    <!-- Crown blade gradients: dark green silhouette + brighter accent -->
    <linearGradient id="crown-deep" x1="0.5" y1="0" x2="0.5" y2="1">
      <stop offset="0%"   stop-color="#3F7A3F"/>
      <stop offset="55%"  stop-color="#2D4A2D"/>
      <stop offset="100%" stop-color="#1F3A1F"/>
    </linearGradient>
    <linearGradient id="crown-bright" x1="0.5" y1="0" x2="0.5" y2="1">
      <stop offset="0%"   stop-color="#7BD17B"/>
      <stop offset="55%"  stop-color="#4CAF50"/>
      <stop offset="100%" stop-color="#2D6B2D"/>
    </linearGradient>

    <!-- Thin amber 45° diamond grid — the "engraved" pineapple skin.
         Each tile is a 36×36 square rotated 45° via patternTransform,
         giving a uniform interlocking diamond crosshatch. A small
         orange eye dot sits in each scale center. -->
    <pattern id="diamond-skin" x="0" y="0" width="36" height="36"
             patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
      <rect x="0" y="0" width="36" height="36" fill="none"
            stroke="#7A5008" stroke-opacity="0.55" stroke-width="0.9"/>
      <!-- Soft top-left highlight stroke for subtle bevel -->
      <path d="M 0 36 L 0 0 L 36 0" fill="none"
            stroke="#FFFAE0" stroke-opacity="0.35" stroke-width="0.6"/>
      <!-- Centered orange eye dot -->
      <circle cx="18" cy="18" r="1.6" fill="#E08A0A" fill-opacity="0.85"/>
    </pattern>

    <!-- Heavy amber outer glow halo -->
    <filter id="amber-glow" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="34"/>
    </filter>

    <!-- Pineapple silhouette + clip path used for the skin grid. -->
    <path id="body-path"
          d="M 320 285 C 200 290, 92 400, 80 530 C 65 670, 95 830, 220 875
             C 280 895, 360 895, 420 875 C 545 830, 575 670, 560 530
             C 550 400, 440 290, 320 285 Z"/>
    <clipPath id="body-clip"><use href="#body-path"/></clipPath>
  </defs>

  <!-- ===== AMBER OUTER GLOW (warm halo bleeding outward) ===== -->
  <g filter="url(#amber-glow)" opacity="0.7">
    <ellipse cx="320" cy="580" rx="280" ry="320" fill="#FFC107" opacity="0.45"/>
    <ellipse cx="320" cy="580" rx="180" ry="220" fill="#FFE066" opacity="0.45"/>
  </g>

  <!-- ===== CROWN — dark green spiky blades, fanned in a wide arc =====
       Drawn behind the body so the blade bases tuck under the rim. -->
  <g class="hero-crown">
    <!-- Layer 1: deep dark-green back blades (widest fan) -->
    <g stroke="#1F3A1F" stroke-width="0.8" stroke-linejoin="round">
      <path d="M 302 360 L 96 145 L 116 178 L 314 360 Z" fill="url(#crown-deep)" opacity="0.95"/>
      <path d="M 338 360 L 544 145 L 524 178 L 326 360 Z" fill="url(#crown-deep)" opacity="0.95"/>
      <path d="M 305 360 L 145 65 L 170 100 L 313 360 Z" fill="url(#crown-deep)"/>
      <path d="M 335 360 L 495 65 L 470 100 L 327 360 Z" fill="url(#crown-deep)"/>
      <path d="M 308 360 L 215 25 L 242 60 L 312 360 Z" fill="url(#crown-deep)"/>
      <path d="M 332 360 L 425 25 L 398 60 L 328 360 Z" fill="url(#crown-deep)"/>
      <path d="M 311 360 L 92 240 L 110 270 L 318 360 Z" fill="url(#crown-deep)" opacity="0.88"/>
      <path d="M 329 360 L 548 240 L 530 270 L 322 360 Z" fill="url(#crown-deep)" opacity="0.88"/>
    </g>

    <!-- Layer 2: medium green inner blades (4) -->
    <g stroke="#2D6B2D" stroke-width="0.8" stroke-linejoin="round">
      <path d="M 311 360 L 270 8 L 296 48 L 315 360 Z" fill="url(#crown-deep)"/>
      <path d="M 329 360 L 370 8 L 344 48 L 325 360 Z" fill="url(#crown-deep)"/>
      <path d="M 314 360 L 250 16 L 280 56 L 317 360 Z" fill="url(#crown-deep)"/>
      <path d="M 326 360 L 390 16 L 360 56 L 323 360 Z" fill="url(#crown-deep)"/>
    </g>

    <!-- Layer 3: two bright accent blades up center for the highlight -->
    <g stroke="#1F3A1F" stroke-width="0.8" stroke-linejoin="round">
      <path d="M 314 360 L 318 -2 L 332 56 L 322 360 Z" fill="url(#crown-bright)"/>
      <path d="M 326 360 L 322 -2 L 308 56 L 318 360 Z" fill="url(#crown-bright)"/>
    </g>
  </g>

  <!-- ===== PINEAPPLE BODY ===== -->
  <!-- Body fill: pineapple silhouette + bright golden gradient -->
  <use href="#body-path" fill="url(#body-yellow)"
       stroke="#7A5008" stroke-width="2.5" stroke-opacity="0.7"/>

  <!-- 45° interlocking diamond skin pattern (clipped to body) -->
  <g clip-path="url(#body-clip)">
    <rect x="40" y="270" width="560" height="650" fill="url(#diamond-skin)"/>
  </g>

  <!-- Specular sheen (upper-left) for glossy surface highlight -->
  <g clip-path="url(#body-clip)">
    <ellipse cx="240" cy="430" rx="160" ry="200" fill="url(#body-sheen)"/>
  </g>

  <!-- Crisp body outline drawn last for a clean rim. -->
  <use href="#body-path" fill="none"
       stroke="#7A5008" stroke-width="2.4" stroke-opacity="0.55"/>
</svg>
"""


# Legacy template kept for the previous spiral-pulse pineapple. Unused
# while the design is reverted to the diamond-grid version above; kept
# in the module so we can switch back without re-typing the SVG.
_HERO_PINEAPPLE_SVG_TEMPLATE = """\
<svg class="hero-pineapple" viewBox="0 0 640 920" xmlns="http://www.w3.org/2000/svg"
     role="img" aria-hidden="true" preserveAspectRatio="xMidYMid meet">
  <style>
    /* ── Organic pineapple palette (sampled-from-photo) ───────────────
       Each scale is a 36×36 rect inside a parent <g> rotated 45°.
         • 8-spiral (col+row even)  → mustard center #C8A020 fading to
           yellow-green spike-tip #8BAA1A at the edges.
         • 13-spiral (col+row odd) → deep forest green #2D4A15.
         • Seam grooves stroked in the same forest green so the green
           spiral visually merges with the grooves (the "unifying
           thread" the brief asks for).
         • Tiny near-black-green dots (.scale-pocket) sit at every
           grid corner — the shadow pockets where four scales meet.

       The pulse is intentionally subtle here — no harsh neon, no
       color flash. We animate transform + brightness only, so the
       gradient fills stay intact and the fruit just *breathes*.
       Yellow breath leads at 14%; green breath answers at 54%. */
    .hero-pineapple .scale-yellow,
    .hero-pineapple .scale-green {
      stroke: #2D4A15;
      stroke-width: 1;
      transform-box: fill-box;
      transform-origin: center;
    }
    .hero-pineapple .scale-yellow {
      fill: url(#scale-fill-yellow);
      animation: pineappleHeartbeatYellow 3.4s ease-in-out infinite;
    }
    .hero-pineapple .scale-green {
      fill: url(#scale-fill-green);
      animation: pineappleHeartbeatGreen 3.4s ease-in-out infinite;
    }
    .hero-pineapple .scale-pocket {
      fill: #1A2D0A;
      pointer-events: none;
    }
    @keyframes pineappleHeartbeatYellow {
      0%, 100% { transform: scale(1);    filter: brightness(1); }
      14%      { transform: scale(1.04); filter: brightness(1.12); }
      28%      { transform: scale(1);    filter: brightness(1); }
    }
    @keyframes pineappleHeartbeatGreen {
      0%, 100% { transform: scale(1);    filter: brightness(1); }
      54%      { transform: scale(1.04); filter: brightness(1.18); }
      68%      { transform: scale(1);    filter: brightness(1); }
    }
    /* Hover deepens the breath slightly (still organic, no neon). */
    .hero-pineapple:hover .scale-yellow {
      animation: pineappleHeartbeatYellowHover 2.6s ease-in-out infinite;
    }
    .hero-pineapple:hover .scale-green {
      animation: pineappleHeartbeatGreenHover 2.6s ease-in-out infinite;
    }
    @keyframes pineappleHeartbeatYellowHover {
      0%, 100% { transform: scale(1);    filter: brightness(1); }
      14%      { transform: scale(1.06); filter: brightness(1.22); }
      30%      { transform: scale(1);    filter: brightness(1); }
    }
    @keyframes pineappleHeartbeatGreenHover {
      0%, 100% { transform: scale(1);    filter: brightness(1); }
      54%      { transform: scale(1.06); filter: brightness(1.30); }
      70%      { transform: scale(1);    filter: brightness(1); }
    }
    @media (prefers-reduced-motion: reduce) {
      .hero-pineapple .scale-yellow,
      .hero-pineapple .scale-green { animation: none; }
    }
  </style>
  <defs>
    <!-- Per-scale radial gradients. Default gradientUnits is
         objectBoundingBox, so each <rect> gets its own copy mapped to
         its own bounding box — every diamond fades from a mustard
         (or forest) center out to a yellow-green (or near-black-green)
         tip. This is what gives the scales their organic, photographic
         feel instead of a flat color block. -->
    <radialGradient id="scale-fill-yellow" cx="50%" cy="50%" r="62%">
      <stop offset="0%"   stop-color="#D3AB28"/>  <!-- lifted center -->
      <stop offset="45%"  stop-color="#C8A020"/>  <!-- mustard core   -->
      <stop offset="80%"  stop-color="#A89018"/>  <!-- mid transition -->
      <stop offset="100%" stop-color="#8BAA1A"/>  <!-- yellow-green tips -->
    </radialGradient>
    <radialGradient id="scale-fill-green" cx="50%" cy="50%" r="62%">
      <stop offset="0%"   stop-color="#3F6320"/>  <!-- lit forest center -->
      <stop offset="55%"  stop-color="#345218"/>
      <stop offset="100%" stop-color="#2D4A15"/>  <!-- deep forest edges -->
    </radialGradient>

    <!-- Body underglow kept beneath the scales as a warm fallback in
         case any micro-gaps show through. -->
    <radialGradient id="body-lit" cx="50%" cy="22%" r="78%">
      <stop offset="0%"   stop-color="#FFFAE0"/>
      <stop offset="20%"  stop-color="#FFE9A0"/>
      <stop offset="45%"  stop-color="#FFE066"/>
      <stop offset="70%"  stop-color="#F5C518"/>
      <stop offset="100%" stop-color="#7A5008"/>
    </radialGradient>

    <!-- Crown frond / blade gradients (line-art monochrome gold). -->
    <linearGradient id="frond-gold" x1="0.5" y1="0" x2="0.5" y2="1">
      <stop offset="0%"   stop-color="#FFE9A0"/>
      <stop offset="60%"  stop-color="#F5C518"/>
      <stop offset="100%" stop-color="#8A6510"/>
    </linearGradient>
    <linearGradient id="blade-deep" x1="0.5" y1="0" x2="0.5" y2="1">
      <stop offset="0%"   stop-color="#FFD56B"/>
      <stop offset="55%"  stop-color="#C28C12"/>
      <stop offset="100%" stop-color="#6B4408"/>
    </linearGradient>
    <linearGradient id="blade-mid" x1="0.5" y1="0" x2="0.5" y2="1">
      <stop offset="0%"   stop-color="#FFE9A0"/>
      <stop offset="55%"  stop-color="#F5C518"/>
      <stop offset="100%" stop-color="#8A6510"/>
    </linearGradient>
    <linearGradient id="blade-light" x1="0.5" y1="0" x2="0.5" y2="1">
      <stop offset="0%"   stop-color="#FFFAE0"/>
      <stop offset="50%"  stop-color="#FFE066"/>
      <stop offset="100%" stop-color="#C28C12"/>
    </linearGradient>

    <!-- Heavy amber outer glow halo. -->
    <filter id="amber-glow" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="34"/>
    </filter>

    <!-- True pineapple silhouette + clip for the scale grid. -->
    <path id="body-path"
          d="M 320 285 C 200 290, 92 400, 80 530 C 65 670, 95 830, 220 875
             C 280 895, 360 895, 420 875 C 545 830, 575 670, 560 530
             C 550 400, 440 290, 320 285 Z"/>
    <clipPath id="body-clip"><use href="#body-path"/></clipPath>
  </defs>

  <!-- ===== AMBER OUTER GLOW ===== -->
  <g filter="url(#amber-glow)" opacity="0.85">
    <ellipse cx="320" cy="580" rx="310" ry="350" fill="#FFA500" opacity="0.55"/>
    <ellipse cx="320" cy="580" rx="230" ry="270" fill="#FFC107" opacity="0.7"/>
    <ellipse cx="320" cy="580" rx="150" ry="180" fill="#FFE066" opacity="0.55"/>
  </g>

  <!-- ===== CROWN (line-art monochrome gold, layered) ===== -->
  <g class="hero-crown">
    <g stroke="url(#frond-gold)" stroke-width="1.2" opacity="0.88"
       stroke-linecap="round">
      <line x1="320" y1="360" x2="125" y2="343"/>
      <line x1="320" y1="360" x2="108" y2="315"/>
      <line x1="320" y1="360" x2="92"  y2="277"/>
      <line x1="320" y1="360" x2="86"  y2="236"/>
      <line x1="320" y1="360" x2="88"  y2="198"/>
      <line x1="320" y1="360" x2="98"  y2="153"/>
      <line x1="320" y1="360" x2="116" y2="116"/>
      <line x1="320" y1="360" x2="144" y2="78"/>
      <line x1="320" y1="360" x2="175" y2="49"/>
      <line x1="320" y1="360" x2="212" y2="26"/>
      <line x1="320" y1="360" x2="246" y2="12"/>
      <line x1="320" y1="360" x2="283" y2="3"/>
      <line x1="320" y1="360" x2="357" y2="3"/>
      <line x1="320" y1="360" x2="394" y2="12"/>
      <line x1="320" y1="360" x2="428" y2="26"/>
      <line x1="320" y1="360" x2="465" y2="49"/>
      <line x1="320" y1="360" x2="496" y2="78"/>
      <line x1="320" y1="360" x2="524" y2="116"/>
      <line x1="320" y1="360" x2="542" y2="153"/>
      <line x1="320" y1="360" x2="552" y2="198"/>
      <line x1="320" y1="360" x2="554" y2="236"/>
      <line x1="320" y1="360" x2="548" y2="277"/>
      <line x1="320" y1="360" x2="532" y2="315"/>
      <line x1="320" y1="360" x2="515" y2="343"/>
    </g>
    <g stroke="#6B4408" stroke-width="0.8" stroke-linejoin="round">
      <path d="M 302 360 L 96 145 L 114 175 L 314 360 Z" fill="url(#blade-deep)" opacity="0.95"/>
      <path d="M 338 360 L 544 145 L 526 175 L 326 360 Z" fill="url(#blade-deep)" opacity="0.95"/>
      <path d="M 305 360 L 145 65 L 168 95 L 313 360 Z" fill="url(#blade-deep)"/>
      <path d="M 335 360 L 495 65 L 472 95 L 327 360 Z" fill="url(#blade-deep)"/>
      <path d="M 308 360 L 215 25 L 240 55 L 312 360 Z" fill="url(#blade-deep)"/>
      <path d="M 332 360 L 425 25 L 400 55 L 328 360 Z" fill="url(#blade-deep)"/>
      <path d="M 311 360 L 92 240 L 108 268 L 318 360 Z" fill="url(#blade-deep)" opacity="0.88"/>
      <path d="M 329 360 L 548 240 L 532 268 L 322 360 Z" fill="url(#blade-deep)" opacity="0.88"/>
    </g>
    <g stroke="#8A6510" stroke-width="0.8" stroke-linejoin="round">
      <path d="M 311 360 L 270 8 L 296 48 L 315 360 Z" fill="url(#blade-mid)"/>
      <path d="M 329 360 L 370 8 L 344 48 L 325 360 Z" fill="url(#blade-mid)"/>
      <path d="M 314 360 L 250 16 L 280 56 L 317 360 Z" fill="url(#blade-mid)"/>
      <path d="M 326 360 L 390 16 L 360 56 L 323 360 Z" fill="url(#blade-mid)"/>
    </g>
    <g stroke="#A57414" stroke-width="0.8" stroke-linejoin="round">
      <path d="M 314 360 L 318 -2 L 332 56 L 322 360 Z" fill="url(#blade-light)"/>
      <path d="M 326 360 L 322 -2 L 308 56 L 318 360 Z" fill="url(#blade-light)"/>
    </g>
    <g stroke="#FFFAE0" stroke-width="1.2" fill="none" opacity="0.72"
       stroke-linecap="round">
      <path d="M 320 350 L 320 8"/>
      <path d="M 312 348 L 282 38"/>
      <path d="M 328 348 L 358 38"/>
      <path d="M 305 348 L 240 60"/>
      <path d="M 335 348 L 400 60"/>
      <path d="M 296 350 L 175 100"/>
      <path d="M 344 350 L 465 100"/>
    </g>
    <g stroke="#FFE066" stroke-width="0.7" fill="none" opacity="0.55"
       stroke-linecap="round">
      <path d="M 286 352 L 130 180"/>
      <path d="M 354 352 L 510 180"/>
      <path d="M 276 354 L 100 260"/>
      <path d="M 364 354 L 540 260"/>
    </g>
  </g>

  <!-- ===== PINEAPPLE BODY ===== -->
  <!-- Underglow body fill — mostly hidden by the scale grid, but acts
       as a warm fallback under the seam grooves. -->
  <use href="#body-path" fill="url(#body-lit)"
       stroke="#7A5008" stroke-width="2.5" stroke-opacity="0.55"/>

  <!-- 45° interlocking diamond grid: every scale is its own <rect>
       so it can carry a per-spiral fill class and pulse independently.
       The whole grid is rotated 45° around the body center, then
       clipped to the body silhouette. The pocket-dot layer sits on
       top so the shadow points read at every X-junction. -->
  <g clip-path="url(#body-clip)">
    <g class="pineapple-skin-grid" transform="rotate(45 320 585)">
        {SCALES}
    </g>
    <g class="pineapple-skin-pockets" transform="rotate(45 320 585)">
        {POCKETS}
    </g>
  </g>

  <!-- Crisp body outline drawn last so the rim stays clean. -->
  <use href="#body-path" fill="none"
       stroke="#7A5008" stroke-width="2.8" stroke-opacity="0.45"/>
</svg>
"""

# ── Crystal / glass pineapple (current active design) ─────────────────
# Translucent golden body with sharply faceted diamond scales (each cell
# carries a bright top-left highlight + dark bottom-right shadow + a
# tiny specular sparkle), and an emerald-crystal crown made of multiple
# layered blades with white edge-light to read as cut glass. Inspired
# by a crystal sculpture reference.
_HERO_PINEAPPLE_SVG_CRYSTAL = """\
<svg class="hero-pineapple" viewBox="0 0 640 920" xmlns="http://www.w3.org/2000/svg"
     role="img" aria-hidden="true" preserveAspectRatio="xMidYMid meet">
  <defs>
    <!-- Translucent glass body: bright cream-amber center fading to
         deep amber at the rim. The central brightness mimics how
         backlight passes through a glass pineapple. -->
    <radialGradient id="glass-body" cx="50%" cy="40%" r="68%">
      <stop offset="0%"   stop-color="#FFF1A8"/>
      <stop offset="25%"  stop-color="#FFD54F"/>
      <stop offset="55%"  stop-color="#F2B602"/>
      <stop offset="85%"  stop-color="#A8770A"/>
      <stop offset="100%" stop-color="#5A3F08"/>
    </radialGradient>

    <!-- Vertical bright "edge-light" stripe down the body center —
         the signature refraction line on glass. -->
    <linearGradient id="glass-center-flare" x1="0" y1="0.5" x2="1" y2="0.5">
      <stop offset="0%"   stop-color="#FFFAE0" stop-opacity="0"/>
      <stop offset="48%"  stop-color="#FFFAE0" stop-opacity="0.45"/>
      <stop offset="52%"  stop-color="#FFFFFF" stop-opacity="0.55"/>
      <stop offset="56%"  stop-color="#FFFAE0" stop-opacity="0.40"/>
      <stop offset="100%" stop-color="#FFFAE0" stop-opacity="0"/>
    </linearGradient>

    <!-- Inner rim shadow: darkens the glass at the silhouette edges
         so the body reads as round and glassy, not flat. -->
    <radialGradient id="glass-rim-shadow" cx="50%" cy="50%" r="60%">
      <stop offset="68%"  stop-color="#3D2400" stop-opacity="0"/>
      <stop offset="100%" stop-color="#2A1A00" stop-opacity="0.65"/>
    </radialGradient>

    <!-- Per-facet bevel: bright top-left → dark bottom-right.
         Drives the 3D faceted look of every diamond scale. -->
    <linearGradient id="facet-bevel" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%"   stop-color="#FFFAE0" stop-opacity="0.55"/>
      <stop offset="48%"  stop-color="#FFE066" stop-opacity="0.05"/>
      <stop offset="52%"  stop-color="#5C3A1A" stop-opacity="0.05"/>
      <stop offset="100%" stop-color="#3D2400" stop-opacity="0.55"/>
    </linearGradient>

    <!-- Crystal scale pattern — square 36×36 tile rotated 45°.
         Each cell layers: a bevel-gradient base, a bright top-left
         specular stroke, a dark bottom-right shadow stroke, a faint
         outline, and a tiny white "twinkle" near the upper-left
         corner that catches the eye and reads as cut-glass sparkle. -->
    <pattern id="crystal-skin" x="0" y="0" width="36" height="36"
             patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
      <rect x="0" y="0" width="36" height="36" fill="url(#facet-bevel)"/>
      <!-- Bright specular edge (top + left of each diamond) -->
      <path d="M 0 36 L 0 0 L 36 0" fill="none"
            stroke="#FFFFFF" stroke-opacity="0.85" stroke-width="0.95"/>
      <!-- Inner cream highlight (lifts the bevel) -->
      <path d="M 3 33 L 3 3 L 33 3" fill="none"
            stroke="#FFFAE0" stroke-opacity="0.45" stroke-width="0.6"/>
      <!-- Dark shadow edge (bottom + right) -->
      <path d="M 36 0 L 36 36 L 0 36" fill="none"
            stroke="#2A1A00" stroke-opacity="0.75" stroke-width="0.95"/>
      <!-- Inner shadow under the bevel -->
      <path d="M 33 3 L 33 33 L 3 33" fill="none"
            stroke="#5C3A1A" stroke-opacity="0.35" stroke-width="0.6"/>
      <!-- Cell outline -->
      <rect x="0" y="0" width="36" height="36" fill="none"
            stroke="#7A5008" stroke-opacity="0.45" stroke-width="0.6"/>
      <!-- Tiny white sparkle (cut-glass twinkle) -->
      <circle cx="9" cy="9" r="1.5" fill="#FFFFFF" fill-opacity="0.85"/>
      <!-- Inner amber dot (refraction core of the facet) -->
      <circle cx="20" cy="20" r="1.2" fill="#FFE066" fill-opacity="0.55"/>
    </pattern>

    <!-- Emerald crystal blade gradients — bright cream-green tip
         fading to deep forest base. The white-cream highlight at
         the very top sells the cut-glass quality. -->
    <linearGradient id="crystal-blade" x1="0.5" y1="0" x2="0.5" y2="1">
      <stop offset="0%"   stop-color="#FFFFFF"/>
      <stop offset="8%"   stop-color="#E8F8E9"/>
      <stop offset="22%"  stop-color="#76C57A"/>
      <stop offset="55%"  stop-color="#2E7D32"/>
      <stop offset="100%" stop-color="#0F3018"/>
    </linearGradient>
    <linearGradient id="crystal-blade-mid" x1="0.5" y1="0" x2="0.5" y2="1">
      <stop offset="0%"   stop-color="#C8EBC9"/>
      <stop offset="25%"  stop-color="#43A047"/>
      <stop offset="65%"  stop-color="#1B5E20"/>
      <stop offset="100%" stop-color="#0A2810"/>
    </linearGradient>
    <linearGradient id="crystal-blade-deep" x1="0.5" y1="0" x2="0.5" y2="1">
      <stop offset="0%"   stop-color="#88C58C"/>
      <stop offset="40%"  stop-color="#1B5E20"/>
      <stop offset="100%" stop-color="#072008"/>
    </linearGradient>

    <!-- Soft amber outer halo to suggest the bright window backlight. -->
    <filter id="amber-glow" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="32"/>
    </filter>

    <!-- Pineapple silhouette + clip path. -->
    <path id="body-path"
          d="M 320 285 C 200 290, 92 400, 80 530 C 65 670, 95 830, 220 875
             C 280 895, 360 895, 420 875 C 545 830, 575 670, 560 530
             C 550 400, 440 290, 320 285 Z"/>
    <clipPath id="body-clip"><use href="#body-path"/></clipPath>
  </defs>

  <!-- ===== AMBER OUTER GLOW (warm window backlight) ===== -->
  <g filter="url(#amber-glow)" opacity="0.65">
    <ellipse cx="320" cy="580" rx="290" ry="330" fill="#FFC107" opacity="0.45"/>
    <ellipse cx="320" cy="580" rx="180" ry="220" fill="#FFE066" opacity="0.45"/>
  </g>

  <!-- ===== CROWN — emerald crystal blades, layered for depth =====
       Drawn behind the body so blade bases tuck under the rim. Each
       blade carries a bright cream tip → forest base gradient that
       reads as cut glass. -->
  <g class="hero-crown">
    <!-- Layer 1: deepest back blades (widest fan) -->
    <g stroke="#072008" stroke-width="0.7" stroke-linejoin="round">
      <path d="M 302 360 L 96 145 L 116 178 L 314 360 Z" fill="url(#crystal-blade-deep)" opacity="0.95"/>
      <path d="M 338 360 L 544 145 L 524 178 L 326 360 Z" fill="url(#crystal-blade-deep)" opacity="0.95"/>
      <path d="M 305 360 L 145 65 L 170 100 L 313 360 Z" fill="url(#crystal-blade-deep)"/>
      <path d="M 335 360 L 495 65 L 470 100 L 327 360 Z" fill="url(#crystal-blade-deep)"/>
      <path d="M 308 360 L 215 25 L 242 60 L 312 360 Z" fill="url(#crystal-blade-deep)"/>
      <path d="M 332 360 L 425 25 L 398 60 L 328 360 Z" fill="url(#crystal-blade-deep)"/>
      <path d="M 311 360 L 92 240 L 110 270 L 318 360 Z" fill="url(#crystal-blade-deep)" opacity="0.88"/>
      <path d="M 329 360 L 548 240 L 530 270 L 322 360 Z" fill="url(#crystal-blade-deep)" opacity="0.88"/>
    </g>

    <!-- Layer 2: mid-depth blades -->
    <g stroke="#0A2810" stroke-width="0.7" stroke-linejoin="round">
      <path d="M 304 360 L 168 90 L 190 130 L 316 360 Z" fill="url(#crystal-blade-mid)"/>
      <path d="M 336 360 L 472 90 L 450 130 L 324 360 Z" fill="url(#crystal-blade-mid)"/>
      <path d="M 309 360 L 240 30 L 268 70 L 314 360 Z" fill="url(#crystal-blade-mid)"/>
      <path d="M 331 360 L 400 30 L 372 70 L 326 360 Z" fill="url(#crystal-blade-mid)"/>
      <path d="M 311 360 L 270 8 L 296 48 L 315 360 Z" fill="url(#crystal-blade-mid)"/>
      <path d="M 329 360 L 370 8 L 344 48 L 325 360 Z" fill="url(#crystal-blade-mid)"/>
    </g>

    <!-- Layer 3: foreground bright blades — the cut-glass highlight set -->
    <g stroke="#0F3018" stroke-width="0.7" stroke-linejoin="round">
      <path d="M 314 360 L 318 -2 L 332 56 L 322 360 Z" fill="url(#crystal-blade)"/>
      <path d="M 326 360 L 322 -2 L 308 56 L 318 360 Z" fill="url(#crystal-blade)"/>
      <path d="M 308 360 L 284 18 L 308 60 L 318 360 Z" fill="url(#crystal-blade)" opacity="0.95"/>
      <path d="M 332 360 L 356 18 L 332 60 L 322 360 Z" fill="url(#crystal-blade)" opacity="0.95"/>
    </g>

    <!-- White edge-light highlights on the front blades (cut-glass tip glints) -->
    <g stroke="#FFFFFF" stroke-width="1.1" fill="none" opacity="0.78"
       stroke-linecap="round">
      <path d="M 320 8 L 320 200"/>
      <path d="M 312 14 L 296 200"/>
      <path d="M 328 14 L 344 200"/>
      <path d="M 300 28 L 270 220"/>
      <path d="M 340 28 L 370 220"/>
    </g>
    <!-- Secondary thinner highlights deeper into the fan -->
    <g stroke="#E8F8E9" stroke-width="0.7" fill="none" opacity="0.55"
       stroke-linecap="round">
      <path d="M 268 70 L 200 220"/>
      <path d="M 372 70 L 440 220"/>
      <path d="M 220 100 L 130 240"/>
      <path d="M 420 100 L 510 240"/>
    </g>
  </g>

  <!-- ===== PINEAPPLE BODY ===== -->
  <!-- Glass body fill — bright translucent gold gradient. -->
  <use href="#body-path" fill="url(#glass-body)"
       stroke="#7A5008" stroke-width="2.5" stroke-opacity="0.7"/>

  <!-- Crystal-faceted diamond skin (clipped to body). -->
  <g clip-path="url(#body-clip)">
    <rect x="40" y="270" width="560" height="650" fill="url(#crystal-skin)"/>
  </g>

  <!-- Vertical center edge-light flare — the glass refraction line. -->
  <g clip-path="url(#body-clip)">
    <rect x="40" y="270" width="560" height="650" fill="url(#glass-center-flare)"/>
  </g>

  <!-- Inner rim shadow for round glassy form. -->
  <g clip-path="url(#body-clip)">
    <ellipse cx="320" cy="580" rx="260" ry="320" fill="url(#glass-rim-shadow)"/>
  </g>

  <!-- Crisp body outline drawn last for a clean rim. -->
  <use href="#body-path" fill="none"
       stroke="#5A3F08" stroke-width="2.4" stroke-opacity="0.7"/>
</svg>
"""

# ── Crystal / glass pineapple — PHOTOREAL studio render ──────────────
# Translucent glass body with a vertical gold→honey gradient and a
# warm internal glow at the upper center, faceted with hundreds of
# individually-colored prismatic scales (4 brightness tiers, stable
# pseudo-random distribution). Crown is layered jade/emerald glass
# with bright mint tips. Sits in front of a dark elliptical backdrop
# with a warm amber underlight so it reads as a studio render even
# when the page hero behind it stays light.

_HERO_PINEAPPLE_SVG_CRYSTAL_PHOTOREAL = """\
<svg class="hero-pineapple" viewBox="0 0 640 920" xmlns="http://www.w3.org/2000/svg"
     role="img" aria-hidden="true" preserveAspectRatio="xMidYMid meet">
  <style>
    /* Per-tier prismatic facet colors — now translucent so the body's
       internal glow bleeds through every scale, and each facet carries
       a soft bloom halo (drop-shadow) so the brightest tiers read as
       miniature light sources. Strokes lightened so seams don't fight
       the glow. */
    .hero-pineapple .facet-t0,
    .hero-pineapple .facet-t1,
    .hero-pineapple .facet-t2,
    .hero-pineapple .facet-t3 {
      stroke: #4A2D00;
      stroke-width: 0.7;
      stroke-opacity: 0.45;
      transform-box: fill-box;
      transform-origin: center;
    }
    .hero-pineapple .facet-t0 {
      fill: #FFF5CC;
      fill-opacity: 0.78;
      filter: drop-shadow(0 0 6px rgba(255, 245, 204, 0.85))
              drop-shadow(0 0 14px rgba(255, 215, 0, 0.55));
      animation: shimmerBright 3.6s ease-in-out infinite;
    }
    .hero-pineapple .facet-t1 {
      fill: #FFE066;
      fill-opacity: 0.70;
      filter: drop-shadow(0 0 4px rgba(255, 224, 102, 0.55));
      animation: shimmerLit    4.4s ease-in-out infinite;
    }
    .hero-pineapple .facet-t2 {
      fill: #C8950A;
      fill-opacity: 0.55;
      animation: shimmerMid    5.2s ease-in-out infinite;
    }
    .hero-pineapple .facet-t3 {
      fill: #8B5E00;
      fill-opacity: 0.45;
      animation: shimmerDeep   5.8s ease-in-out infinite;
    }
    /* Different cycle lengths give the prismatic shimmer an organic,
       non-synchronized feel. We animate brightness only so the per-
       tier color identity stays readable, and the bright tiers get
       a bigger swing because they're the ones that "twinkle". */
    @keyframes shimmerBright { 0%, 100% { filter: brightness(1) drop-shadow(0 0 6px rgba(255, 245, 204, 0.85)) drop-shadow(0 0 14px rgba(255, 215, 0, 0.55)); }
                               50%      { filter: brightness(1.28) drop-shadow(0 0 9px rgba(255, 245, 204, 1)) drop-shadow(0 0 22px rgba(255, 215, 0, 0.85)); } }
    @keyframes shimmerLit    { 0%, 100% { filter: brightness(1) drop-shadow(0 0 4px rgba(255, 224, 102, 0.55)); }
                               50%      { filter: brightness(1.16) drop-shadow(0 0 7px rgba(255, 224, 102, 0.85)); } }
    @keyframes shimmerMid    { 0%, 100% { filter: brightness(1); } 50% { filter: brightness(1.10); } }
    @keyframes shimmerDeep   { 0%, 100% { filter: brightness(1); } 50% { filter: brightness(1.12); } }
    @media (prefers-reduced-motion: reduce) {
      .hero-pineapple .facet-t0,
      .hero-pineapple .facet-t1,
      .hero-pineapple .facet-t2,
      .hero-pineapple .facet-t3 { animation: none; }
    }

    /* ── Fibonacci spiral KEYBOARD-POP animation ─────────────────
       Three line families pop in sequentially over a 9-second cycle:
         0–3 s : 8 gradual-slope spirals appear (magenta)
         3–6 s : 13 medium-slope spirals join in (cyan)
         6–9 s : 21 near-vertical spirals join (yellow)
       Each line "pops up" with a bouncy translateY → 0 + scale(1)
       like a keyboard key being released. After all three families
       are visible the cycle restarts (lines fade out → loop). */
    .hero-pineapple .spiral-line {
      fill: none;
      stroke-width: 2.4;
      stroke-linecap: round;
      opacity: 0;
      transform-box: fill-box;
      transform-origin: center;
      filter: drop-shadow(0 0 4px currentColor)
              drop-shadow(0 0 10px currentColor);
    }
    .hero-pineapple .spiral-f8 {
      stroke: #FF3D8A;
      color: #FF3D8A;
      animation: spiralKeyPop8 9s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
    }
    .hero-pineapple .spiral-f13 {
      stroke: #18E5F0;
      color: #18E5F0;
      animation: spiralKeyPop13 9s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
    }
    .hero-pineapple .spiral-f21 {
      stroke: #FFE74C;
      color: #FFE74C;
      animation: spiralKeyPop21 9s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
    }
    /* 8 spirals: pop in 0–7%, peak bounce at 7%, settle at 14%, hold
       through the rest of the cycle, fade out at 95–100%. */
    @keyframes spiralKeyPop8 {
      0%   { opacity: 0;   transform: translateY(14px) scale(0.92); }
      7%   { opacity: 1;   transform: translateY(-5px) scale(1.06); }
      14%  { opacity: 1;   transform: translateY(0)    scale(1); }
      95%  { opacity: 1;   transform: translateY(0)    scale(1); }
      100% { opacity: 0;   transform: translateY(14px) scale(0.92); }
    }
    /* 13 spirals: hidden until 33%, then pop in. */
    @keyframes spiralKeyPop13 {
      0%, 33% { opacity: 0; transform: translateY(14px) scale(0.92); }
      40%     { opacity: 1; transform: translateY(-5px) scale(1.06); }
      47%     { opacity: 1; transform: translateY(0)    scale(1); }
      95%     { opacity: 1; transform: translateY(0)    scale(1); }
      100%    { opacity: 0; transform: translateY(14px) scale(0.92); }
    }
    /* 21 spirals: hidden until 66%, then pop in. */
    @keyframes spiralKeyPop21 {
      0%, 66% { opacity: 0; transform: translateY(14px) scale(0.92); }
      73%     { opacity: 1; transform: translateY(-5px) scale(1.06); }
      80%     { opacity: 1; transform: translateY(0)    scale(1); }
      95%     { opacity: 1; transform: translateY(0)    scale(1); }
      100%    { opacity: 0; transform: translateY(14px) scale(0.92); }
    }
    @media (prefers-reduced-motion: reduce) {
      .hero-pineapple .spiral-line {
        animation: none;
        opacity: 0.65;
      }
    }
  </style>
  <defs>
    <!-- Dark studio backdrop ellipse — fades from near-black at the
         pineapple's center out to fully transparent so it doesn't
         create a hard rectangle on the surrounding hero canvas. -->
    <radialGradient id="dark-backdrop" cx="50%" cy="55%" r="62%">
      <stop offset="0%"   stop-color="#0A0A0A" stop-opacity="0.92"/>
      <stop offset="55%"  stop-color="#0A0A0A" stop-opacity="0.55"/>
      <stop offset="100%" stop-color="#0A0A0A" stop-opacity="0"/>
    </radialGradient>

    <!-- Body vertical glass gradient: bright luminous gold up top,
         deep honey at the base. This is the "translucent glass"
         core fill that the per-scale facets sit on top of. -->
    <linearGradient id="glass-body-vertical" x1="0.5" y1="0" x2="0.5" y2="1">
      <stop offset="0%"   stop-color="#FFEB7A"/>
      <stop offset="20%"  stop-color="#FFD700"/>
      <stop offset="55%"  stop-color="#E8AE08"/>
      <stop offset="85%"  stop-color="#D4900A"/>
      <stop offset="100%" stop-color="#8B5E00"/>
    </linearGradient>

    <!-- Internal warm glow — the "light from within the fruit".
         Now bigger and brighter; pairs with the translucent facets
         so the body genuinely looks lit from inside. -->
    <radialGradient id="internal-glow" cx="50%" cy="38%" r="55%">
      <stop offset="0%"   stop-color="#FFFFFF" stop-opacity="0.85"/>
      <stop offset="22%"  stop-color="#FFFAE0" stop-opacity="0.65"/>
      <stop offset="55%"  stop-color="#FFE066" stop-opacity="0.30"/>
      <stop offset="100%" stop-color="#FFC107" stop-opacity="0"/>
    </radialGradient>

    <!-- Secondary bloom that bleeds upward from the body center,
         giving a strong "inner sun" feel under the translucent skin. -->
    <radialGradient id="skin-bloom" cx="50%" cy="48%" r="48%">
      <stop offset="0%"   stop-color="#FFFAE0" stop-opacity="0.55"/>
      <stop offset="60%"  stop-color="#FFD700" stop-opacity="0.25"/>
      <stop offset="100%" stop-color="#FFA000" stop-opacity="0"/>
    </radialGradient>

    <!-- Soft blur for the skin-bloom layer. -->
    <filter id="skin-bloom-blur" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="18"/>
    </filter>

    <!-- Inner rim shadow rounds the silhouette so it reads as 3D glass. -->
    <radialGradient id="glass-rim-shadow" cx="50%" cy="50%" r="60%">
      <stop offset="65%"  stop-color="#3D2400" stop-opacity="0"/>
      <stop offset="100%" stop-color="#1A1100" stop-opacity="0.7"/>
    </radialGradient>

    <!-- Jade / emerald crystal blade gradients. Three depth tiers —
         deepest in the back, brightest in the front. -->
    <linearGradient id="jade-bright" x1="0.5" y1="0" x2="0.5" y2="1">
      <stop offset="0%"   stop-color="#FFFFFF"/>
      <stop offset="6%"   stop-color="#A8FFD0"/>
      <stop offset="22%"  stop-color="#6EE8A0"/>
      <stop offset="42%"  stop-color="#00C87A"/>
      <stop offset="72%"  stop-color="#1A7A4A"/>
      <stop offset="100%" stop-color="#0D3D20"/>
    </linearGradient>
    <linearGradient id="jade-mid" x1="0.5" y1="0" x2="0.5" y2="1">
      <stop offset="0%"   stop-color="#A8FFD0"/>
      <stop offset="20%"  stop-color="#3FBD78"/>
      <stop offset="55%"  stop-color="#1A7A4A"/>
      <stop offset="100%" stop-color="#0A2D14"/>
    </linearGradient>
    <linearGradient id="jade-deep" x1="0.5" y1="0" x2="0.5" y2="1">
      <stop offset="0%"   stop-color="#3FBD78"/>
      <stop offset="40%"  stop-color="#1A7A4A"/>
      <stop offset="78%"  stop-color="#0D3D20"/>
      <stop offset="100%" stop-color="#06200E"/>
    </linearGradient>

    <!-- Warm amber underlight — diffuse glow from below as if the
         pineapple is sitting on a glossy surface lit from beneath. -->
    <filter id="warm-underlight" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="40"/>
    </filter>

    <!-- Soft amber ambient halo (top + sides). -->
    <filter id="amber-ambient" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="28"/>
    </filter>

    <!-- Pineapple silhouette + clip path. -->
    <path id="body-path"
          d="M 320 285 C 200 290, 92 400, 80 530 C 65 670, 95 830, 220 875
             C 280 895, 360 895, 420 875 C 545 830, 575 670, 560 530
             C 550 400, 440 290, 320 285 Z"/>
    <clipPath id="body-clip"><use href="#body-path"/></clipPath>
  </defs>

  <!-- ===== DARK STUDIO BACKDROP =====
       Soft elliptical near-black halo behind the pineapple so the
       crystal pops without changing the surrounding page background. -->
  <ellipse cx="320" cy="500" rx="400" ry="520" fill="url(#dark-backdrop)"/>

  <!-- ===== WARM AMBER UNDERLIGHT =====
       Diffuse warm light from below, as if reflected off a glossy
       dark surface. Sits behind the body. -->
  <g filter="url(#warm-underlight)" opacity="0.95">
    <ellipse cx="320" cy="855" rx="260" ry="80" fill="#FFA000"/>
    <ellipse cx="320" cy="875" rx="190" ry="50" fill="#FFC107" opacity="0.85"/>
    <ellipse cx="320" cy="890" rx="140" ry="32" fill="#FFE066" opacity="0.75"/>
  </g>

  <!-- Faint amber ambient halo wrapping the whole sculpture. -->
  <g filter="url(#amber-ambient)" opacity="0.55">
    <ellipse cx="320" cy="540" rx="280" ry="340" fill="#C28C12"/>
  </g>

  <!-- Glossy surface reflection beneath the body (compressed dark sheen). -->
  <ellipse cx="320" cy="900" rx="220" ry="14" fill="#000000" opacity="0.6"/>

  <!-- ===== CROWN — jade / emerald crystal blades, 3 depth layers ===== -->
  <g class="hero-crown">
    <!-- Layer 1: deepest back blades -->
    <g stroke="#06200E" stroke-width="0.7" stroke-linejoin="round">
      <path d="M 302 360 L 96 145 L 116 178 L 314 360 Z" fill="url(#jade-deep)" opacity="0.95"/>
      <path d="M 338 360 L 544 145 L 524 178 L 326 360 Z" fill="url(#jade-deep)" opacity="0.95"/>
      <path d="M 305 360 L 145 65 L 170 100 L 313 360 Z" fill="url(#jade-deep)"/>
      <path d="M 335 360 L 495 65 L 470 100 L 327 360 Z" fill="url(#jade-deep)"/>
      <path d="M 308 360 L 215 25 L 242 60 L 312 360 Z" fill="url(#jade-deep)"/>
      <path d="M 332 360 L 425 25 L 398 60 L 328 360 Z" fill="url(#jade-deep)"/>
      <path d="M 311 360 L 92 240 L 110 270 L 318 360 Z" fill="url(#jade-deep)" opacity="0.88"/>
      <path d="M 329 360 L 548 240 L 530 270 L 322 360 Z" fill="url(#jade-deep)" opacity="0.88"/>
    </g>

    <!-- Layer 2: mid-depth blades -->
    <g stroke="#0A2D14" stroke-width="0.7" stroke-linejoin="round">
      <path d="M 304 360 L 168 90 L 190 130 L 316 360 Z" fill="url(#jade-mid)"/>
      <path d="M 336 360 L 472 90 L 450 130 L 324 360 Z" fill="url(#jade-mid)"/>
      <path d="M 309 360 L 240 30 L 268 70 L 314 360 Z" fill="url(#jade-mid)"/>
      <path d="M 331 360 L 400 30 L 372 70 L 326 360 Z" fill="url(#jade-mid)"/>
      <path d="M 311 360 L 270 8 L 296 48 L 315 360 Z" fill="url(#jade-mid)"/>
      <path d="M 329 360 L 370 8 L 344 48 L 325 360 Z" fill="url(#jade-mid)"/>
    </g>

    <!-- Layer 3: bright foreground blades — the cut-glass tip-glints -->
    <g stroke="#0D3D20" stroke-width="0.7" stroke-linejoin="round">
      <path d="M 314 360 L 318 -2 L 332 56 L 322 360 Z" fill="url(#jade-bright)"/>
      <path d="M 326 360 L 322 -2 L 308 56 L 318 360 Z" fill="url(#jade-bright)"/>
      <path d="M 308 360 L 284 18 L 308 60 L 318 360 Z" fill="url(#jade-bright)" opacity="0.95"/>
      <path d="M 332 360 L 356 18 L 332 60 L 322 360 Z" fill="url(#jade-bright)" opacity="0.95"/>
    </g>

    <!-- Bright mint edge-light highlights along front blades -->
    <g stroke="#A8FFD0" stroke-width="1.2" fill="none" opacity="0.85"
       stroke-linecap="round">
      <path d="M 320 4 L 320 200"/>
      <path d="M 312 14 L 296 200"/>
      <path d="M 328 14 L 344 200"/>
      <path d="M 300 28 L 270 220"/>
      <path d="M 340 28 L 370 220"/>
    </g>
    <!-- Secondary thinner mint highlights deeper into the fan -->
    <g stroke="#6EE8A0" stroke-width="0.7" fill="none" opacity="0.6"
       stroke-linecap="round">
      <path d="M 268 70 L 200 220"/>
      <path d="M 372 70 L 440 220"/>
      <path d="M 220 100 L 130 240"/>
      <path d="M 420 100 L 510 240"/>
    </g>
  </g>

  <!-- ===== PINEAPPLE BODY ===== -->
  <!-- Translucent glass core fill — vertical gold→honey gradient. -->
  <use href="#body-path" fill="url(#glass-body-vertical)"
       stroke="#3D2400" stroke-width="2" stroke-opacity="0.85"/>

  <!-- Internal warm glow (light from within the fruit) — larger and
       brighter so it bleeds visibly through the translucent facets. -->
  <g clip-path="url(#body-clip)">
    <ellipse cx="320" cy="460" rx="280" ry="280" fill="url(#internal-glow)"/>
  </g>

  <!-- Skin-bloom layer: a softly-blurred warm bloom sitting BENEATH
       the facets, giving the translucent skin a true inner-sun feel
       once light leaks through every scale. -->
  <g clip-path="url(#body-clip)">
    <ellipse cx="320" cy="540" rx="260" ry="320"
             fill="url(#skin-bloom)" filter="url(#skin-bloom-blur)"/>
  </g>

  <!-- Per-scale prismatic crystal facets — the rich shimmer.
       Each rect carries a .facet-t0..3 class (4 brightness tiers,
       distributed pseudo-randomly with a stable seed). The whole
       grid is rotated 45° around the body center, then clipped
       to the body silhouette. Facets are translucent + bloom-haloed
       so the inner glow radiates through the skin. -->
  <g clip-path="url(#body-clip)">
    <g class="pineapple-crystal-grid" transform="rotate(45 320 585)">
        {FACETS}
    </g>
  </g>

  <!-- Fibonacci spiral overlay (keyboard-pop animation).
       Three families of straight line segments — 8 / 13 / 21 — each
       spanning the body silhouette at a specific slope. Animated by
       per-family CSS keyframes so they pop in sequentially every
       9 s like keys on a keyboard. Drawn on top of the facets but
       still clipped to the body silhouette. -->
  <g clip-path="url(#body-clip)">
    <g class="pineapple-fibonacci-spirals">
        {SPIRALS}
    </g>
  </g>

  <!-- Inner rim shadow rounds the silhouette into a glassy 3D form. -->
  <g clip-path="url(#body-clip)">
    <ellipse cx="320" cy="580" rx="270" ry="320" fill="url(#glass-rim-shadow)"/>
  </g>

  <!-- Crisp body outline drawn last for a clean cut-glass rim. -->
  <use href="#body-path" fill="none"
       stroke="#1A1100" stroke-width="2.6" stroke-opacity="0.9"/>
</svg>
"""

# ── Faceted-3D pineapple — engineered cut-stone variant ──────────────
# Each diamond scale carries an explicit 3-zone vertical gradient that
# appears upper-right → lower-left after the pattern's 45° rotation:
#   • bright near-white  #FFF8C0  (UR highlight zone)
#   • flat golden amber  #D4900A  (center base zone)
#   • deep amber shadow  #8B5E00  (LL shadow zone)
# Stepped color stops produce visibly distinct zones (not a smooth
# fade) so each scale reads as a faceted convex surface catching a
# single light source from the upper right. Adjacent scales are
# separated by 2 px burnt-brown #3D1F00 grout, and a single white
# specular glint dot sits in the upper-right peak of each diamond.
# Crown blades are explicit 3-tone gradients (mint tip → emerald body
# → forest base) with bright mint spine highlights down the front.

_HERO_PINEAPPLE_SVG_FACETED_3D = """\
<svg class="hero-pineapple" viewBox="0 0 640 920" xmlns="http://www.w3.org/2000/svg"
     role="img" aria-hidden="true" preserveAspectRatio="xMidYMid meet">
  <defs>
    <!-- ── Body radial gradient (sits BENEATH the facets) ──────────
         Bright luminous gold center → deep amber edges. Provides
         overall tonal consistency and shows at the rim where the
         facet pattern doesn't reach. -->
    <radialGradient id="body-radial" cx="50%" cy="40%" r="68%">
      <stop offset="0%"   stop-color="#FFE082"/>
      <stop offset="35%"  stop-color="#FFD700"/>
      <stop offset="75%"  stop-color="#D4900A"/>
      <stop offset="100%" stop-color="#5A3F08"/>
    </radialGradient>

    <!-- ── 3-zone stepped facet gradient ───────────────────────────
         Vertical in pattern coords; appears UR→LL in screen space
         after the pattern's 45° rotation. Hard color stops produce
         three visibly distinct zones (highlight / base / shadow)
         instead of a smooth blend — that's what gives the carved
         "faceted" look. -->
    <linearGradient id="facet-3d-grad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%"   stop-color="#FFF8C0"/>  <!-- bright highlight -->
      <stop offset="28%"  stop-color="#FFF8C0"/>
      <stop offset="36%"  stop-color="#D4900A"/>  <!-- step → base -->
      <stop offset="64%"  stop-color="#D4900A"/>
      <stop offset="72%"  stop-color="#8B5E00"/>  <!-- step → shadow -->
      <stop offset="100%" stop-color="#8B5E00"/>
    </linearGradient>

    <!-- ── Faceted skin pattern ────────────────────────────────────
         A 36×36 square tile rotated 45° (so each tile renders as an
         interlocking diamond). Each tile carries:
           (1) the 3-zone vertical gradient fill
           (2) a 2 px burnt-brown #3D1F00 stroke (the deep grout)
           (3) a tiny white #FFFFFF specular glint at the upper-right
               peak of the diamond. Pattern coord (24, 6) maps to the
               upper-right area of the rotated diamond in screen space
               (verified: x_pat * cos45 - y_pat * sin45 ≈ 12.7,
               x_pat * sin45 + y_pat * cos45 ≈ 21.2 — sits inside the
               UR edge of the diamond). -->
    <pattern id="facet-skin" x="0" y="0" width="36" height="36"
             patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
      <rect x="0" y="0" width="36" height="36" fill="url(#facet-3d-grad)"/>
      <rect x="0" y="0" width="36" height="36" fill="none"
            stroke="#3D1F00" stroke-width="2" stroke-linejoin="miter"/>
      <circle cx="24" cy="6" r="1.6" fill="#FFFFFF" fill-opacity="0.92"/>
      <!-- Soft halo around the glint for a touch of bloom -->
      <circle cx="24" cy="6" r="3.4" fill="#FFFFFF" fill-opacity="0.18"/>
    </pattern>

    <!-- ── Crown leaf 3-tone gradients ─────────────────────────────
         Every blade is shaded mint tip → emerald body → forest base.
         Three depths (bright / mid / deep) for the layered fan. -->
    <linearGradient id="leaf-bright" x1="0.5" y1="0" x2="0.5" y2="1">
      <stop offset="0%"   stop-color="#A8FFD0"/>  <!-- bright mint tip -->
      <stop offset="25%"  stop-color="#3FBD78"/>
      <stop offset="55%"  stop-color="#1A7A4A"/>  <!-- emerald body -->
      <stop offset="100%" stop-color="#0D3D20"/>  <!-- forest base -->
    </linearGradient>
    <linearGradient id="leaf-mid" x1="0.5" y1="0" x2="0.5" y2="1">
      <stop offset="0%"   stop-color="#7EE0A8"/>
      <stop offset="35%"  stop-color="#1A7A4A"/>
      <stop offset="100%" stop-color="#0A2D14"/>
    </linearGradient>
    <linearGradient id="leaf-deep" x1="0.5" y1="0" x2="0.5" y2="1">
      <stop offset="0%"   stop-color="#3FBD78"/>
      <stop offset="50%"  stop-color="#0D3D20"/>
      <stop offset="100%" stop-color="#06200E"/>
    </linearGradient>
    <!-- Bright mint spine highlight gradient (thin elliptical stripe
         down the center of each front blade for the glossy spine). -->
    <linearGradient id="leaf-spine" x1="0.5" y1="0" x2="0.5" y2="1">
      <stop offset="0%"   stop-color="#FFFFFF" stop-opacity="0.9"/>
      <stop offset="20%"  stop-color="#A8FFD0" stop-opacity="0.85"/>
      <stop offset="60%"  stop-color="#A8FFD0" stop-opacity="0.45"/>
      <stop offset="100%" stop-color="#A8FFD0" stop-opacity="0"/>
    </linearGradient>

    <!-- Pineapple silhouette + clip path. -->
    <path id="body-path"
          d="M 320 285 C 200 290, 92 400, 80 530 C 65 670, 95 830, 220 875
             C 280 895, 360 895, 420 875 C 545 830, 575 670, 560 530
             C 550 400, 440 290, 320 285 Z"/>
    <clipPath id="body-clip"><use href="#body-path"/></clipPath>

    <!-- Soft amber ambient halo (warm backlight, not a directional
         light source — just atmospheric warmth). -->
    <filter id="amber-halo" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="32"/>
    </filter>

    <!-- Upper-right rim-light gradient: subtle bright crescent on
         the upper-right of the body silhouette confirming the
         single-light-source-from-upper-right convention. -->
    <radialGradient id="rim-light-ur" cx="78%" cy="22%" r="32%">
      <stop offset="0%"   stop-color="#FFFAE0" stop-opacity="0.55"/>
      <stop offset="60%"  stop-color="#FFE066" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="#FFE066" stop-opacity="0"/>
    </radialGradient>

    <!-- Lower-left ambient occlusion: subtle deepening on the
         opposite side of the light to round the body. -->
    <radialGradient id="ao-ll" cx="22%" cy="78%" r="32%">
      <stop offset="0%"   stop-color="#1A1100" stop-opacity="0.55"/>
      <stop offset="60%"  stop-color="#3D2400" stop-opacity="0.20"/>
      <stop offset="100%" stop-color="#3D2400" stop-opacity="0"/>
    </radialGradient>
  </defs>

  <!-- ===== AMBER AMBIENT HALO ===== -->
  <g filter="url(#amber-halo)" opacity="0.6">
    <ellipse cx="320" cy="580" rx="290" ry="330" fill="#FFC107" opacity="0.45"/>
    <ellipse cx="320" cy="580" rx="180" ry="220" fill="#FFE066" opacity="0.45"/>
  </g>

  <!-- ===== CROWN — 3-tone shaded jade blades, layered in depth ===== -->
  <g class="hero-crown">
    <!-- Layer 1: deepest back blades (widest fan) -->
    <g stroke="#06200E" stroke-width="1" stroke-linejoin="round">
      <path d="M 302 360 L 96 145 L 116 178 L 314 360 Z" fill="url(#leaf-deep)" opacity="0.95"/>
      <path d="M 338 360 L 544 145 L 524 178 L 326 360 Z" fill="url(#leaf-deep)" opacity="0.95"/>
      <path d="M 305 360 L 145 65 L 170 100 L 313 360 Z" fill="url(#leaf-deep)"/>
      <path d="M 335 360 L 495 65 L 470 100 L 327 360 Z" fill="url(#leaf-deep)"/>
      <path d="M 308 360 L 215 25 L 242 60 L 312 360 Z" fill="url(#leaf-deep)"/>
      <path d="M 332 360 L 425 25 L 398 60 L 328 360 Z" fill="url(#leaf-deep)"/>
      <path d="M 311 360 L 92 240 L 110 270 L 318 360 Z" fill="url(#leaf-deep)" opacity="0.88"/>
      <path d="M 329 360 L 548 240 L 530 270 L 322 360 Z" fill="url(#leaf-deep)" opacity="0.88"/>
    </g>

    <!-- Layer 2: mid-depth blades -->
    <g stroke="#0A2D14" stroke-width="1" stroke-linejoin="round">
      <path d="M 304 360 L 168 90 L 190 130 L 316 360 Z" fill="url(#leaf-mid)"/>
      <path d="M 336 360 L 472 90 L 450 130 L 324 360 Z" fill="url(#leaf-mid)"/>
      <path d="M 309 360 L 240 30 L 268 70 L 314 360 Z" fill="url(#leaf-mid)"/>
      <path d="M 331 360 L 400 30 L 372 70 L 326 360 Z" fill="url(#leaf-mid)"/>
      <path d="M 311 360 L 270 8 L 296 48 L 315 360 Z" fill="url(#leaf-mid)"/>
      <path d="M 329 360 L 370 8 L 344 48 L 325 360 Z" fill="url(#leaf-mid)"/>
    </g>

    <!-- Layer 3: foreground bright blades — full mint→forest 3-tone -->
    <g stroke="#0D3D20" stroke-width="1" stroke-linejoin="round">
      <path d="M 314 360 L 318 -2 L 332 56 L 322 360 Z" fill="url(#leaf-bright)"/>
      <path d="M 326 360 L 322 -2 L 308 56 L 318 360 Z" fill="url(#leaf-bright)"/>
      <path d="M 308 360 L 284 18 L 308 60 L 318 360 Z" fill="url(#leaf-bright)" opacity="0.95"/>
      <path d="M 332 360 L 356 18 L 332 60 L 322 360 Z" fill="url(#leaf-bright)" opacity="0.95"/>
    </g>

    <!-- Bright mint spines down the center of front blades.
         Drawn as thin wedge polygons filled with the spine gradient
         so they themselves are 3-tone (white → mint → fading mint). -->
    <g>
      <polygon points="320,4   322,300  318,300"  fill="url(#leaf-spine)"/>
      <polygon points="312,14  306,260  302,260"  fill="url(#leaf-spine)"/>
      <polygon points="328,14  338,260  334,260"  fill="url(#leaf-spine)"/>
      <polygon points="300,28  282,250  278,250"  fill="url(#leaf-spine)"/>
      <polygon points="340,28  362,250  358,250"  fill="url(#leaf-spine)"/>
    </g>

    <!-- Secondary thinner mint spines deeper into the fan -->
    <g stroke="#6EE8A0" stroke-width="0.8" fill="none" opacity="0.65"
       stroke-linecap="round">
      <path d="M 268 70 L 200 240"/>
      <path d="M 372 70 L 440 240"/>
      <path d="M 220 100 L 130 260"/>
      <path d="M 420 100 L 510 260"/>
    </g>
  </g>

  <!-- ===== PINEAPPLE BODY ===== -->
  <!-- Body radial gradient — bright gold center → deep amber edges.
       Sits BEHIND the faceted skin; visible at the rim. Stroked with
       the same burnt-brown as the grout for a continuous outline. -->
  <use href="#body-path" fill="url(#body-radial)"
       stroke="#3D1F00" stroke-width="2.5" stroke-opacity="0.9"/>

  <!-- 3D faceted skin (clipped to body): per-scale 3-zone gradient +
       2px burnt-brown grout + white specular glints. -->
  <g clip-path="url(#body-clip)">
    <rect x="40" y="270" width="560" height="650" fill="url(#facet-skin)"/>
  </g>

  <!-- Upper-right rim light (confirms single light source). -->
  <g clip-path="url(#body-clip)">
    <ellipse cx="450" cy="380" rx="180" ry="220" fill="url(#rim-light-ur)"/>
  </g>

  <!-- Lower-left ambient occlusion (rounds the body). -->
  <g clip-path="url(#body-clip)">
    <ellipse cx="190" cy="780" rx="180" ry="220" fill="url(#ao-ll)"/>
  </g>

  <!-- Crisp body outline drawn last for a clean cut-glass rim. -->
  <use href="#body-path" fill="none"
       stroke="#3D1F00" stroke-width="3" stroke-opacity="0.95"/>
</svg>
"""

# ── Raised-dome pineapple — gem-cluster skin ─────────────────────────
# Each scale is a fully enclosed convex diamond rendered as a 3D dome
# via a centered radial gradient (bright center → amber → dark edge).
# Adjacent scales are inset inside their grid cells, so the dark body
# fill underneath shows through the gaps as deep carved groove
# channels — not thin painted lines. Position-based brightness tiers
# (computed in screen space against an upper-center light source at
# (320, 380)) make scales near the top of the fruit visibly brighter
# overall and scales near the bottom-edges sit in deeper shadow.
# Result: hundreds of small raised golden gems on a sphere.

_HERO_PINEAPPLE_SVG_DOMES_TEMPLATE = """\
<svg class="hero-pineapple" viewBox="0 0 640 920" xmlns="http://www.w3.org/2000/svg"
     role="img" aria-hidden="true" preserveAspectRatio="xMidYMid meet">
  <style>
    /* Each tier = one shared radial-gradient fill. The same gradient
       is applied to every scale in that tier, but because radial
       gradients with default objectBoundingBox units are anchored
       to each filled element's own bounding box, each scale gets
       its own centered dome highlight (not one shared gradient
       smeared across the body). */
    .hero-pineapple .dome-t0 { fill: url(#dome-t0); }
    .hero-pineapple .dome-t1 { fill: url(#dome-t1); }
    .hero-pineapple .dome-t2 { fill: url(#dome-t2); }
    .hero-pineapple .dome-t3 { fill: url(#dome-t3); }
  </style>
  <defs>
    <!-- ── Dome gradients: 4 tiers, each with the same shape (bright
         center → mid amber → dark edge) but progressively darker
         overall colors. Tier 0 sits closest to the light, tier 3
         sits in the deepest shadow zone. r=58% gives a tight bright
         highlight that fades quickly to the dark edge — sells the
         "raised blister catching light" feel. -->
    <radialGradient id="dome-t0" cx="50%" cy="50%" r="58%">
      <stop offset="0%"   stop-color="#FFF5A0"/>
      <stop offset="32%"  stop-color="#FFE066"/>
      <stop offset="72%"  stop-color="#D4900A"/>
      <stop offset="100%" stop-color="#5A3F08"/>
    </radialGradient>
    <radialGradient id="dome-t1" cx="50%" cy="50%" r="58%">
      <stop offset="0%"   stop-color="#FFE066"/>
      <stop offset="32%"  stop-color="#F2C200"/>
      <stop offset="72%"  stop-color="#A8770A"/>
      <stop offset="100%" stop-color="#3D2400"/>
    </radialGradient>
    <radialGradient id="dome-t2" cx="50%" cy="50%" r="58%">
      <stop offset="0%"   stop-color="#E8AE08"/>
      <stop offset="32%"  stop-color="#C28C12"/>
      <stop offset="72%"  stop-color="#7A5008"/>
      <stop offset="100%" stop-color="#2A1A00"/>
    </radialGradient>
    <radialGradient id="dome-t3" cx="50%" cy="50%" r="58%">
      <stop offset="0%"   stop-color="#A8770A"/>
      <stop offset="32%"  stop-color="#7A5008"/>
      <stop offset="72%"  stop-color="#3D1F00"/>
      <stop offset="100%" stop-color="#1A0F00"/>
    </radialGradient>

    <!-- ── Body underglow: deep dark brown so groove gaps read as
         carved channels, with a hint of warm amber bleeding from
         the center so the silhouette doesn't read as pure black. -->
    <radialGradient id="body-underbrown" cx="50%" cy="38%" r="65%">
      <stop offset="0%"   stop-color="#5A3F08"/>
      <stop offset="55%"  stop-color="#3D1F00"/>
      <stop offset="100%" stop-color="#1A0F00"/>
    </radialGradient>

    <!-- ── Crown blade gradients (jade / emerald translucent glass) -->
    <linearGradient id="jade-bright" x1="0.5" y1="0" x2="0.5" y2="1">
      <stop offset="0%"   stop-color="#FFFFFF"/>
      <stop offset="6%"   stop-color="#A8FFD0"/>
      <stop offset="22%"  stop-color="#6EE8A0"/>
      <stop offset="42%"  stop-color="#00C87A"/>
      <stop offset="72%"  stop-color="#1A7A4A"/>
      <stop offset="100%" stop-color="#0D3D20"/>
    </linearGradient>
    <linearGradient id="jade-mid" x1="0.5" y1="0" x2="0.5" y2="1">
      <stop offset="0%"   stop-color="#A8FFD0"/>
      <stop offset="20%"  stop-color="#3FBD78"/>
      <stop offset="55%"  stop-color="#1A7A4A"/>
      <stop offset="100%" stop-color="#0A2D14"/>
    </linearGradient>
    <linearGradient id="jade-deep" x1="0.5" y1="0" x2="0.5" y2="1">
      <stop offset="0%"   stop-color="#3FBD78"/>
      <stop offset="40%"  stop-color="#1A7A4A"/>
      <stop offset="78%"  stop-color="#0D3D20"/>
      <stop offset="100%" stop-color="#06200E"/>
    </linearGradient>

    <!-- ── Studio backdrop + warm halo (kept from the photoreal
         iteration so the gem skin pops against a darker frame). -->
    <radialGradient id="dark-backdrop" cx="50%" cy="55%" r="62%">
      <stop offset="0%"   stop-color="#0A0A0A" stop-opacity="0.85"/>
      <stop offset="55%"  stop-color="#0A0A0A" stop-opacity="0.50"/>
      <stop offset="100%" stop-color="#0A0A0A" stop-opacity="0"/>
    </radialGradient>
    <filter id="amber-halo" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="32"/>
    </filter>

    <!-- ── Upper-center top-light wash — additive bright zone over
         the upper-center of the body. Reinforces the global lighting
         direction set by the per-scale tier system. -->
    <radialGradient id="top-light-wash" cx="50%" cy="14%" r="50%">
      <stop offset="0%"   stop-color="#FFFAE0" stop-opacity="0.55"/>
      <stop offset="50%"  stop-color="#FFE066" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="#FFE066" stop-opacity="0"/>
    </radialGradient>

    <!-- ── Lower-edge ambient occlusion — subtle dark crescent on
         the bottom edges so the body reads as a sphere. -->
    <radialGradient id="bottom-shadow" cx="50%" cy="92%" r="55%">
      <stop offset="0%"   stop-color="#0A0500" stop-opacity="0.55"/>
      <stop offset="60%"  stop-color="#1A0F00" stop-opacity="0.20"/>
      <stop offset="100%" stop-color="#1A0F00" stop-opacity="0"/>
    </radialGradient>

    <!-- Pineapple silhouette + clip path. -->
    <path id="body-path"
          d="M 320 285 C 200 290, 92 400, 80 530 C 65 670, 95 830, 220 875
             C 280 895, 360 895, 420 875 C 545 830, 575 670, 560 530
             C 550 400, 440 290, 320 285 Z"/>
    <clipPath id="body-clip"><use href="#body-path"/></clipPath>
  </defs>

  <!-- ===== STUDIO BACKDROP + AMBIENT HALO ===== -->
  <ellipse cx="320" cy="500" rx="400" ry="520" fill="url(#dark-backdrop)"/>
  <g filter="url(#amber-halo)" opacity="0.55">
    <ellipse cx="320" cy="540" rx="280" ry="340" fill="#C28C12"/>
    <ellipse cx="320" cy="380" rx="180" ry="160" fill="#FFE066" opacity="0.7"/>
  </g>

  <!-- ===== CROWN — jade crystal blades, layered ===== -->
  <g class="hero-crown">
    <g stroke="#06200E" stroke-width="0.7" stroke-linejoin="round">
      <path d="M 302 360 L 96 145 L 116 178 L 314 360 Z" fill="url(#jade-deep)" opacity="0.95"/>
      <path d="M 338 360 L 544 145 L 524 178 L 326 360 Z" fill="url(#jade-deep)" opacity="0.95"/>
      <path d="M 305 360 L 145 65 L 170 100 L 313 360 Z" fill="url(#jade-deep)"/>
      <path d="M 335 360 L 495 65 L 470 100 L 327 360 Z" fill="url(#jade-deep)"/>
      <path d="M 308 360 L 215 25 L 242 60 L 312 360 Z" fill="url(#jade-deep)"/>
      <path d="M 332 360 L 425 25 L 398 60 L 328 360 Z" fill="url(#jade-deep)"/>
      <path d="M 311 360 L 92 240 L 110 270 L 318 360 Z" fill="url(#jade-deep)" opacity="0.88"/>
      <path d="M 329 360 L 548 240 L 530 270 L 322 360 Z" fill="url(#jade-deep)" opacity="0.88"/>
    </g>
    <g stroke="#0A2D14" stroke-width="0.7" stroke-linejoin="round">
      <path d="M 304 360 L 168 90 L 190 130 L 316 360 Z" fill="url(#jade-mid)"/>
      <path d="M 336 360 L 472 90 L 450 130 L 324 360 Z" fill="url(#jade-mid)"/>
      <path d="M 309 360 L 240 30 L 268 70 L 314 360 Z" fill="url(#jade-mid)"/>
      <path d="M 331 360 L 400 30 L 372 70 L 326 360 Z" fill="url(#jade-mid)"/>
      <path d="M 311 360 L 270 8 L 296 48 L 315 360 Z" fill="url(#jade-mid)"/>
      <path d="M 329 360 L 370 8 L 344 48 L 325 360 Z" fill="url(#jade-mid)"/>
    </g>
    <g stroke="#0D3D20" stroke-width="0.7" stroke-linejoin="round">
      <path d="M 314 360 L 318 -2 L 332 56 L 322 360 Z" fill="url(#jade-bright)"/>
      <path d="M 326 360 L 322 -2 L 308 56 L 318 360 Z" fill="url(#jade-bright)"/>
      <path d="M 308 360 L 284 18 L 308 60 L 318 360 Z" fill="url(#jade-bright)" opacity="0.95"/>
      <path d="M 332 360 L 356 18 L 332 60 L 322 360 Z" fill="url(#jade-bright)" opacity="0.95"/>
    </g>
    <g stroke="#A8FFD0" stroke-width="1.2" fill="none" opacity="0.85"
       stroke-linecap="round">
      <path d="M 320 4 L 320 200"/>
      <path d="M 312 14 L 296 200"/>
      <path d="M 328 14 L 344 200"/>
      <path d="M 300 28 L 270 220"/>
      <path d="M 340 28 L 370 220"/>
    </g>
  </g>

  <!-- ===== PINEAPPLE BODY — DEEP-GROOVE GEM CLUSTER ===== -->
  <!-- Dark underbody — this is what shows through every groove gap. -->
  <use href="#body-path" fill="url(#body-underbrown)"
       stroke="#0A0500" stroke-width="2.8" stroke-opacity="0.95"/>

  <!-- Per-scale dome rects (four tiers, brightness picked by screen-
       space distance from the upper-center light at (320, 380)). The
       parent <g> rotates the entire grid 45° around (320, 585), so
       each square renders as an upright interlocking diamond. Inset
       on each rect leaves a ~5px deep groove gap between scales. -->
  <g clip-path="url(#body-clip)">
    <g class="pineapple-dome-grid" transform="rotate(45 320 585)">
        {DOMES}
    </g>
  </g>

  <!-- Top-light wash — an additive cream-amber bloom over the upper
       center of the body, reinforcing the global light direction. -->
  <g clip-path="url(#body-clip)">
    <ellipse cx="320" cy="320" rx="240" ry="220" fill="url(#top-light-wash)"/>
  </g>

  <!-- Bottom ambient occlusion — deeper shadow on the lower edge so
       the body reads as a sphere catching light from above. -->
  <g clip-path="url(#body-clip)">
    <ellipse cx="320" cy="850" rx="280" ry="140" fill="url(#bottom-shadow)"/>
  </g>

  <!-- Crisp body outline drawn last for a clean rim. -->
  <use href="#body-path" fill="none"
       stroke="#0A0500" stroke-width="3" stroke-opacity="1"/>
</svg>
"""

# ── Naturalistic pineapple (real-fruit palette) + Fibonacci spirals ──
# Matte gold-amber dome scales with greenish-brown edges and a small
# dark eye dot at every scale's center — the dried bract you see on a
# real pineapple. Subtle position-based brightness (light from above,
# slight darkening at the bottom) keeps the look organic rather than
# dramatic. The Fibonacci spiral keyboard-pop overlay (8 / 13 / 21)
# is layered on top for the teaching animation.

_HERO_PINEAPPLE_SVG_NATURAL_TEMPLATE = """\
<svg class="hero-pineapple" viewBox="0 0 640 920" xmlns="http://www.w3.org/2000/svg"
     role="img" aria-hidden="true" preserveAspectRatio="xMidYMid meet">
  <style>
    /* ── Per-tier scale gradients (each tier picks one shared
       radial gradient — same shape, slightly darker overall as
       you move away from the light source above). objectBoundingBox
       (default) anchors the gradient to each rect's own box, so
       every scale gets its own centered dome highlight. */
    .hero-pineapple .natural-t0 { fill: url(#dome-natural-0); }
    .hero-pineapple .natural-t1 { fill: url(#dome-natural-1); }
    .hero-pineapple .natural-t2 { fill: url(#dome-natural-2); }
    .hero-pineapple .natural-t3 { fill: url(#dome-natural-3); }
    /* Eye dot — the dried bract at the center of every fruitlet. */
    .hero-pineapple .scale-eye {
      fill: #1A0F00;
      pointer-events: none;
    }

    /* ── Fibonacci spiral KEYBOARD-POP animation (unchanged) ──── */
    .hero-pineapple .spiral-line {
      fill: none;
      stroke-width: 2.4;
      stroke-linecap: round;
      opacity: 0;
      transform-box: fill-box;
      transform-origin: center;
      filter: drop-shadow(0 0 4px currentColor)
              drop-shadow(0 0 10px currentColor);
    }
    .hero-pineapple .spiral-f8 {
      stroke: #FF3D8A;
      color: #FF3D8A;
      animation: spiralKeyPop8 9s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
    }
    .hero-pineapple .spiral-f13 {
      stroke: #18E5F0;
      color: #18E5F0;
      animation: spiralKeyPop13 9s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
    }
    .hero-pineapple .spiral-f21 {
      stroke: #FFE74C;
      color: #FFE74C;
      animation: spiralKeyPop21 9s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
    }
    @keyframes spiralKeyPop8 {
      0%   { opacity: 0; transform: translateY(14px) scale(0.92); }
      7%   { opacity: 1; transform: translateY(-5px) scale(1.06); }
      14%  { opacity: 1; transform: translateY(0)    scale(1); }
      95%  { opacity: 1; transform: translateY(0)    scale(1); }
      100% { opacity: 0; transform: translateY(14px) scale(0.92); }
    }
    @keyframes spiralKeyPop13 {
      0%, 33% { opacity: 0; transform: translateY(14px) scale(0.92); }
      40%     { opacity: 1; transform: translateY(-5px) scale(1.06); }
      47%     { opacity: 1; transform: translateY(0)    scale(1); }
      95%     { opacity: 1; transform: translateY(0)    scale(1); }
      100%    { opacity: 0; transform: translateY(14px) scale(0.92); }
    }
    @keyframes spiralKeyPop21 {
      0%, 66% { opacity: 0; transform: translateY(14px) scale(0.92); }
      73%     { opacity: 1; transform: translateY(-5px) scale(1.06); }
      80%     { opacity: 1; transform: translateY(0)    scale(1); }
      95%     { opacity: 1; transform: translateY(0)    scale(1); }
      100%    { opacity: 0; transform: translateY(14px) scale(0.92); }
    }
    @media (prefers-reduced-motion: reduce) {
      .hero-pineapple .spiral-line { animation: none; opacity: 0.65; }
    }
  </style>
  <defs>
    <!-- ── Naturalistic dome gradients, 4 tiers ───────────────────
         Each scale fades from a warm gold center (offset slightly
         upward, mimicking light-from-above) through amber to a
         greenish-brown edge — exactly the palette you see on a
         ripe pineapple's eye. Tiers darken slightly with distance
         from the light source. -->
    <radialGradient id="dome-natural-0" cx="48%" cy="38%" r="62%">
      <stop offset="0%"   stop-color="#FFE066"/>
      <stop offset="20%"  stop-color="#F4C430"/>
      <stop offset="55%"  stop-color="#C8950A"/>
      <stop offset="85%"  stop-color="#7A5A14"/>
      <stop offset="100%" stop-color="#3D2C18"/>
    </radialGradient>
    <radialGradient id="dome-natural-1" cx="48%" cy="38%" r="62%">
      <stop offset="0%"   stop-color="#F4C430"/>
      <stop offset="20%"  stop-color="#D8AB18"/>
      <stop offset="55%"  stop-color="#A8770A"/>
      <stop offset="85%"  stop-color="#5A4818"/>
      <stop offset="100%" stop-color="#2D2010"/>
    </radialGradient>
    <radialGradient id="dome-natural-2" cx="48%" cy="38%" r="62%">
      <stop offset="0%"   stop-color="#D8AB18"/>
      <stop offset="20%"  stop-color="#B88B0A"/>
      <stop offset="55%"  stop-color="#7A5A14"/>
      <stop offset="85%"  stop-color="#4A3818"/>
      <stop offset="100%" stop-color="#1F1A08"/>
    </radialGradient>
    <radialGradient id="dome-natural-3" cx="48%" cy="38%" r="62%">
      <stop offset="0%"   stop-color="#B88B0A"/>
      <stop offset="20%"  stop-color="#7A5A14"/>
      <stop offset="55%"  stop-color="#4A3818"/>
      <stop offset="85%"  stop-color="#2D2010"/>
      <stop offset="100%" stop-color="#0F0A02"/>
    </radialGradient>

    <!-- Body underbase: warm dark brown-green (the visible groove
         color between scales). Sits beneath the dome rects. -->
    <radialGradient id="body-natural-base" cx="50%" cy="38%" r="65%">
      <stop offset="0%"   stop-color="#5A4818"/>
      <stop offset="55%"  stop-color="#3D2C18"/>
      <stop offset="100%" stop-color="#1A1108"/>
    </radialGradient>

    <!-- Subtle top-light wash + bottom shadow for natural lighting. -->
    <radialGradient id="natural-top-light" cx="50%" cy="14%" r="50%">
      <stop offset="0%"   stop-color="#FFFAE0" stop-opacity="0.32"/>
      <stop offset="60%"  stop-color="#FFE066" stop-opacity="0.10"/>
      <stop offset="100%" stop-color="#FFE066" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="natural-bottom-shadow" cx="50%" cy="92%" r="55%">
      <stop offset="0%"   stop-color="#0F0A02" stop-opacity="0.50"/>
      <stop offset="60%"  stop-color="#1F1A08" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="#1F1A08" stop-opacity="0"/>
    </radialGradient>

    <!-- Crown gradients — naturalistic dark forest green (matches
         the reference photographs of a real pineapple crown). -->
    <linearGradient id="crown-bright" x1="0.5" y1="0" x2="0.5" y2="1">
      <stop offset="0%"   stop-color="#7BD17B"/>
      <stop offset="35%"  stop-color="#4CAF50"/>
      <stop offset="75%"  stop-color="#2D6B2D"/>
      <stop offset="100%" stop-color="#1A4A1A"/>
    </linearGradient>
    <linearGradient id="crown-mid" x1="0.5" y1="0" x2="0.5" y2="1">
      <stop offset="0%"   stop-color="#4CAF50"/>
      <stop offset="40%"  stop-color="#2D6B2D"/>
      <stop offset="100%" stop-color="#1A3A1A"/>
    </linearGradient>
    <linearGradient id="crown-deep" x1="0.5" y1="0" x2="0.5" y2="1">
      <stop offset="0%"   stop-color="#2D6B2D"/>
      <stop offset="55%"  stop-color="#1A4A1A"/>
      <stop offset="100%" stop-color="#0D2D0D"/>
    </linearGradient>

    <!-- Soft warm ambient halo (no harsh studio lighting) -->
    <filter id="warm-halo" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="34"/>
    </filter>

    <!-- Pineapple silhouette + clip path. -->
    <path id="body-path"
          d="M 320 285 C 200 290, 92 400, 80 530 C 65 670, 95 830, 220 875
             C 280 895, 360 895, 420 875 C 545 830, 575 670, 560 530
             C 550 400, 440 290, 320 285 Z"/>
    <clipPath id="body-clip"><use href="#body-path"/></clipPath>
  </defs>

  <!-- ===== AMBIENT WARM HALO (subtle, not dramatic) ===== -->
  <g filter="url(#warm-halo)" opacity="0.45">
    <ellipse cx="320" cy="580" rx="280" ry="320" fill="#C28C12" opacity="0.45"/>
    <ellipse cx="320" cy="380" rx="170" ry="150" fill="#FFE066" opacity="0.55"/>
  </g>

  <!-- ===== CROWN — dark green forest blades, layered ===== -->
  <g class="hero-crown">
    <g stroke="#0D2D0D" stroke-width="0.7" stroke-linejoin="round">
      <path d="M 302 360 L 96 145 L 116 178 L 314 360 Z" fill="url(#crown-deep)" opacity="0.95"/>
      <path d="M 338 360 L 544 145 L 524 178 L 326 360 Z" fill="url(#crown-deep)" opacity="0.95"/>
      <path d="M 305 360 L 145 65 L 170 100 L 313 360 Z" fill="url(#crown-deep)"/>
      <path d="M 335 360 L 495 65 L 470 100 L 327 360 Z" fill="url(#crown-deep)"/>
      <path d="M 308 360 L 215 25 L 242 60 L 312 360 Z" fill="url(#crown-deep)"/>
      <path d="M 332 360 L 425 25 L 398 60 L 328 360 Z" fill="url(#crown-deep)"/>
      <path d="M 311 360 L 92 240 L 110 270 L 318 360 Z" fill="url(#crown-deep)" opacity="0.88"/>
      <path d="M 329 360 L 548 240 L 530 270 L 322 360 Z" fill="url(#crown-deep)" opacity="0.88"/>
    </g>
    <g stroke="#1A3A1A" stroke-width="0.7" stroke-linejoin="round">
      <path d="M 304 360 L 168 90 L 190 130 L 316 360 Z" fill="url(#crown-mid)"/>
      <path d="M 336 360 L 472 90 L 450 130 L 324 360 Z" fill="url(#crown-mid)"/>
      <path d="M 309 360 L 240 30 L 268 70 L 314 360 Z" fill="url(#crown-mid)"/>
      <path d="M 331 360 L 400 30 L 372 70 L 326 360 Z" fill="url(#crown-mid)"/>
      <path d="M 311 360 L 270 8 L 296 48 L 315 360 Z" fill="url(#crown-mid)"/>
      <path d="M 329 360 L 370 8 L 344 48 L 325 360 Z" fill="url(#crown-mid)"/>
    </g>
    <g stroke="#1A4A1A" stroke-width="0.7" stroke-linejoin="round">
      <path d="M 314 360 L 318 -2 L 332 56 L 322 360 Z" fill="url(#crown-bright)"/>
      <path d="M 326 360 L 322 -2 L 308 56 L 318 360 Z" fill="url(#crown-bright)"/>
      <path d="M 308 360 L 284 18 L 308 60 L 318 360 Z" fill="url(#crown-bright)" opacity="0.95"/>
      <path d="M 332 360 L 356 18 L 332 60 L 322 360 Z" fill="url(#crown-bright)" opacity="0.95"/>
    </g>
    <!-- Subtle lighter spine highlights down the front blades -->
    <g stroke="#76C57A" stroke-width="0.9" fill="none" opacity="0.55"
       stroke-linecap="round">
      <path d="M 320 8 L 320 200"/>
      <path d="M 312 18 L 296 200"/>
      <path d="M 328 18 L 344 200"/>
    </g>
  </g>

  <!-- ===== PINEAPPLE BODY ===== -->
  <!-- Dark warm underbase (visible as the groove between scales). -->
  <use href="#body-path" fill="url(#body-natural-base)"
       stroke="#1A1108" stroke-width="2.5" stroke-opacity="0.95"/>

  <!-- Per-scale dome rects + per-scale eye dots. The whole grid is
       rotated 45° around the body center, then clipped to the body
       silhouette. Tiered brightness comes from each rect's class. -->
  <g clip-path="url(#body-clip)">
    <g class="pineapple-natural-grid" transform="rotate(45 320 585)">
        {NATURAL}
    </g>
  </g>

  <!-- Subtle top-light wash — natural sunlight from above. -->
  <g clip-path="url(#body-clip)">
    <ellipse cx="320" cy="320" rx="240" ry="220" fill="url(#natural-top-light)"/>
  </g>
  <!-- Bottom ambient occlusion — rounds the body subtly. -->
  <g clip-path="url(#body-clip)">
    <ellipse cx="320" cy="850" rx="280" ry="140" fill="url(#natural-bottom-shadow)"/>
  </g>

  <!-- Fibonacci spiral overlay — keyboard-pop animation, on top of
       the realistic skin so the geometry is still teachable. -->
  <g clip-path="url(#body-clip)">
    <g class="pineapple-fibonacci-spirals">
        {SPIRALS}
    </g>
  </g>

  <!-- Crisp body outline drawn last for a clean rim. -->
  <use href="#body-path" fill="none"
       stroke="#1A1108" stroke-width="2.8" stroke-opacity="0.95"/>
</svg>
"""

# Parked: naturalistic per-scale SVG pineapple (the gold-amber dome
# scales with eye dots). Kept for easy switch-back.
_HERO_PINEAPPLE_SVG_NATURAL = (
    _HERO_PINEAPPLE_SVG_NATURAL_TEMPLATE
    .replace("{NATURAL}", _PINEAPPLE_NATURAL_SKIN_HTML)
    .replace("{SPIRALS}", _PINEAPPLE_FIBONACCI_SPIRALS_HTML)
)


def _load_pineapple_photo_data_uri() -> str:
    """Load the cropped pineapple photograph and inline it as a
    base64 data URI so the visualization stays a single self-
    contained HTML file. The crop was produced from the reference
    screenshot via `sips` (see .codebase-almanac/assets/).

    Returns an empty string if the asset is missing — the photo
    variant is currently parked, so the file isn't required for
    the active design and a missing file should not crash the
    extractor.
    """
    import base64
    import os
    photo_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        ".codebase-almanac",
        "assets",
        "pineapple-photo.png",
    )
    try:
        with open(photo_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("ascii")
    except FileNotFoundError:
        return ""
    # sips wrote JPEG bytes under the .png extension — the real
    # bytes start with `/9j/` (JPEG SOI), so we declare image/jpeg.
    return f"data:image/jpeg;base64,{encoded}"


_PINEAPPLE_PHOTO_DATA_URI = _load_pineapple_photo_data_uri()


def _load_crystal_pineapple_render_data_uri() -> str:
    """Load the AI-generated faceted-crystal pineapple render and
    inline it as a base64 PNG data URI so the visualization stays a
    single self-contained HTML file.

    Looks for `assets/crystal-pineapple.png` next to the repo root.
    Returns an empty string if missing so the build does not crash.
    """
    import base64
    import os
    render_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "assets",
        "crystal-pineapple.png",
    )
    try:
        with open(render_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("ascii")
    except FileNotFoundError:
        return ""
    return f"data:image/png;base64,{encoded}"


_CRYSTAL_PINEAPPLE_RENDER_DATA_URI = _load_crystal_pineapple_render_data_uri()


def _load_approved_pineapple_concept_data_uri() -> str:
    """Load the user-approved concept PNG and inline as data URI.

    Tries a repo-local assets path first, then the Cursor-generated asset path
    used in this workspace session.
    """
    import base64
    import os

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidates = [
        os.path.join(repo_root, "assets", "pineapple-hero-concept-a-flat-minimal.png"),
        "/Users/kinghenry/.cursor/projects/Users-kinghenry-Project48414/assets/pineapple-hero-concept-a-flat-minimal.png",
    ]
    for path in candidates:
        try:
            with open(path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("ascii")
            return f"data:image/png;base64,{encoded}"
        except FileNotFoundError:
            continue
    return ""


_APPROVED_PINEAPPLE_CONCEPT_DATA_URI = _load_approved_pineapple_concept_data_uri()

# Hero variant that drops the AI-generated faceted-crystal pineapple
# render straight into the hero slot. Uses an <img> rather than an SVG
# so the photoreal PBR detail (caustics, fresnel, internal glow) is
# preserved 1:1. The `.hero-pineapple` class already supplies width
# 100% + object-fit:contain, so an <img> sits in the same frame as
# the previous SVG variants.
_HERO_PINEAPPLE_IMG_CRYSTAL_RENDER = (
    '<img class="hero-pineapple" '
    'src="{SRC}" alt="Faceted crystal pineapple" '
    'draggable="false" />'
).replace("{SRC}", _CRYSTAL_PINEAPPLE_RENDER_DATA_URI)

_HERO_PINEAPPLE_IMG_APPROVED = (
    '<img class="hero-pineapple hero-pineapple-approved" '
    'src="{SRC}" alt="Approved pineapple concept" '
    'draggable="false" />'
).replace("{SRC}", _APPROVED_PINEAPPLE_CONCEPT_DATA_URI)

# ── Active design: the actual pineapple photograph ───────────────
# Per the user: "take exactly the picture of the pineapple skin".
# We embed the cropped middle pineapple from the reference image as
# an SVG <image> so it sits in the same hero slot as the previous
# generated illustrations, with a soft radial mask that fades the
# cream studio background into the dark hero panel.
_HERO_PINEAPPLE_SVG_PHOTO_TEMPLATE = """\
<svg class="hero-pineapple" viewBox="0 0 640 920" xmlns="http://www.w3.org/2000/svg"
     role="img" aria-hidden="true" preserveAspectRatio="xMidYMid meet">
  <style>
    /* ── Fibonacci spiral KEYBOARD-POP animation overlay ──────────
       8 → 13 → 21 spirals pop in like keyboard keys on a 9-second
       loop. Each line is stroked with a glowing color so it reads
       clearly against the photographic skin. */
    .hero-pineapple .spiral-line {
      fill: none;
      stroke-width: 3.2;
      stroke-linecap: round;
      opacity: 0;
      transform-box: fill-box;
      transform-origin: center;
      filter: drop-shadow(0 0 5px currentColor)
              drop-shadow(0 0 12px currentColor);
    }
    .hero-pineapple .spiral-f8 {
      stroke: #FF3D8A;
      color: #FF3D8A;
      animation: spiralKeyPop8 9s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
    }
    .hero-pineapple .spiral-f13 {
      stroke: #18E5F0;
      color: #18E5F0;
      animation: spiralKeyPop13 9s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
    }
    .hero-pineapple .spiral-f21 {
      stroke: #FFE74C;
      color: #FFE74C;
      animation: spiralKeyPop21 9s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
    }
    @keyframes spiralKeyPop8 {
      0%   { opacity: 0; transform: translateY(14px) scale(0.92); }
      7%   { opacity: 1; transform: translateY(-5px) scale(1.06); }
      14%  { opacity: 1; transform: translateY(0)    scale(1); }
      95%  { opacity: 1; transform: translateY(0)    scale(1); }
      100% { opacity: 0; transform: translateY(14px) scale(0.92); }
    }
    @keyframes spiralKeyPop13 {
      0%, 33% { opacity: 0; transform: translateY(14px) scale(0.92); }
      40%     { opacity: 1; transform: translateY(-5px) scale(1.06); }
      47%     { opacity: 1; transform: translateY(0)    scale(1); }
      95%     { opacity: 1; transform: translateY(0)    scale(1); }
      100%    { opacity: 0; transform: translateY(14px) scale(0.92); }
    }
    @keyframes spiralKeyPop21 {
      0%, 66% { opacity: 0; transform: translateY(14px) scale(0.92); }
      73%     { opacity: 1; transform: translateY(-5px) scale(1.06); }
      80%     { opacity: 1; transform: translateY(0)    scale(1); }
      95%     { opacity: 1; transform: translateY(0)    scale(1); }
      100%    { opacity: 0; transform: translateY(14px) scale(0.92); }
    }
    @media (prefers-reduced-motion: reduce) {
      .hero-pineapple .spiral-line { animation: none; opacity: 0.7; }
    }
  </style>
  <defs>
    <!-- Feathered mask: keep the pineapple sharp in the center,
         fade the surrounding cream background out to transparent
         so it blends into the dark hero panel. -->
    <radialGradient id="photo-feather" cx="50%" cy="50%" r="50%">
      <stop offset="0%"   stop-color="#fff" stop-opacity="1"/>
      <stop offset="62%"  stop-color="#fff" stop-opacity="1"/>
      <stop offset="82%"  stop-color="#fff" stop-opacity="0.55"/>
      <stop offset="100%" stop-color="#fff" stop-opacity="0"/>
    </radialGradient>
    <mask id="photo-mask" maskUnits="userSpaceOnUse"
          x="40" y="80" width="560" height="800">
      <rect x="40" y="80" width="560" height="800"
            fill="url(#photo-feather)"/>
    </mask>

    <!-- Body silhouette clip — keeps the spiral lines on the fruit
         and off the surrounding background / crown. Fitted to the
         crystal-pineapple crop (taller, slightly narrower). -->
    <clipPath id="photo-body-clip">
      <ellipse cx="337" cy="625" rx="180" ry="232"/>
    </clipPath>

    <!-- Warm ambient halo behind the fruit. -->
    <filter id="photo-warm-halo" x="-60%" y="-60%"
            width="220%" height="220%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="38"/>
    </filter>
  </defs>

  <!-- Ambient warm glow that gives the fruit some context in the
       dark hero panel. -->
  <g filter="url(#photo-warm-halo)" opacity="0.55">
    <ellipse cx="320" cy="540" rx="280" ry="320" fill="#C28C12" opacity="0.55"/>
    <ellipse cx="320" cy="380" rx="170" ry="160" fill="#FFE066" opacity="0.55"/>
  </g>

  <!-- The actual pineapple photograph, inlined as a base64 data URI.
       Centered horizontally, sized to fill the hero slot, then
       softened at the edges by the radial feather mask. -->
  <image href="{PHOTO_URI}"
         x="40" y="80" width="560" height="800"
         preserveAspectRatio="xMidYMid meet"
         mask="url(#photo-mask)"/>

  <!-- Fibonacci spiral overlay — 8 (pink) → 13 (cyan) → 21 (yellow).
       Clipped to the body ellipse so lines hug the photographed fruit. -->
  <g clip-path="url(#photo-body-clip)">
    <g class="pineapple-fibonacci-spirals">
        {SPIRALS}
    </g>
  </g>
</svg>
"""

# ── Premium pineapple template — luxury botanical illustration ───
# Pillowed-diamond scales with cylindrical warp, per-scale color
# variation (row-biased green→gold→warm-brown), refined emerald→
# teal crown with subtle asymmetry, warm-brown grout outlines,
# luxury warm-gold background gradient, and the Fibonacci spiral
# keyboard-pop animation (8 / 13 / 21) layered on top.
_HERO_PINEAPPLE_SVG_PREMIUM_TEMPLATE = """\
<svg class="hero-pineapple" viewBox="0 0 640 920" xmlns="http://www.w3.org/2000/svg"
     role="img" aria-hidden="true" preserveAspectRatio="xMidYMid meet">
  <style>
    /* ── Per-variant scale fills + shared warm-brown grout ──── */
    .hero-pineapple [class^="psc-"] {
      stroke: #6B4A1A;
      stroke-width: 0.55;
      stroke-opacity: 0.55;
      stroke-linejoin: round;
    }
    .hero-pineapple .psc-p0 { fill: url(#prem-p0); }
    .hero-pineapple .psc-p1 { fill: url(#prem-p1); }
    .hero-pineapple .psc-p2 { fill: url(#prem-p2); }
    .hero-pineapple .psc-p3 { fill: url(#prem-p3); }
    .hero-pineapple .psc-p4 { fill: url(#prem-p4); }
    .hero-pineapple .psc-p5 { fill: url(#prem-p5); }
    .hero-pineapple .psc-p6 { fill: url(#prem-p6); }
    .hero-pineapple .psc-p7 { fill: url(#prem-p7); }

    /* ── Fibonacci spiral KEYBOARD-POP animation overlay ──── */
    .hero-pineapple .spiral-line {
      fill: none;
      stroke-width: 2.6;
      stroke-linecap: round;
      opacity: 0;
      transform-box: fill-box;
      transform-origin: center;
      filter: drop-shadow(0 0 4px currentColor)
              drop-shadow(0 0 10px currentColor);
    }
    .hero-pineapple .spiral-f8 {
      stroke: #FF3D8A; color: #FF3D8A;
      animation: spiralKeyPop8 9s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
    }
    .hero-pineapple .spiral-f13 {
      stroke: #18E5F0; color: #18E5F0;
      animation: spiralKeyPop13 9s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
    }
    .hero-pineapple .spiral-f21 {
      stroke: #FFE74C; color: #FFE74C;
      animation: spiralKeyPop21 9s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
    }
    @keyframes spiralKeyPop8 {
      0%   { opacity: 0; transform: translateY(14px) scale(0.92); }
      7%   { opacity: 1; transform: translateY(-5px) scale(1.06); }
      14%  { opacity: 1; transform: translateY(0)    scale(1); }
      95%  { opacity: 1; transform: translateY(0)    scale(1); }
      100% { opacity: 0; transform: translateY(14px) scale(0.92); }
    }
    @keyframes spiralKeyPop13 {
      0%, 33% { opacity: 0; transform: translateY(14px) scale(0.92); }
      40%     { opacity: 1; transform: translateY(-5px) scale(1.06); }
      47%     { opacity: 1; transform: translateY(0)    scale(1); }
      95%     { opacity: 1; transform: translateY(0)    scale(1); }
      100%    { opacity: 0; transform: translateY(14px) scale(0.92); }
    }
    @keyframes spiralKeyPop21 {
      0%, 66% { opacity: 0; transform: translateY(14px) scale(0.92); }
      73%     { opacity: 1; transform: translateY(-5px) scale(1.06); }
      80%     { opacity: 1; transform: translateY(0)    scale(1); }
      95%     { opacity: 1; transform: translateY(0)    scale(1); }
      100%    { opacity: 0; transform: translateY(14px) scale(0.92); }
    }
    @media (prefers-reduced-motion: reduce) {
      .hero-pineapple .spiral-line { animation: none; opacity: 0.7; }
    }
  </style>
  <defs>
    <!-- ── Eight scale-fill gradients ─────────────────────────────
         Each is a small radial gradient (offset slightly upper-left
         to read as "light from above-left"), going from a pale
         cream highlight through the variant's body color to a deep
         warm-brown edge. Variants differ in saturation, hue
         (olive vs. amber vs. honey), and brightness so the grid
         never feels machine-generated. -->
    <radialGradient id="prem-p0" cx="42%" cy="32%" r="62%">
      <stop offset="0%"   stop-color="#FFE890"/>
      <stop offset="22%"  stop-color="#F4C430"/>
      <stop offset="60%"  stop-color="#C89318"/>
      <stop offset="100%" stop-color="#5A3C14"/>
    </radialGradient>
    <radialGradient id="prem-p1" cx="42%" cy="32%" r="62%">
      <stop offset="0%"   stop-color="#FFD978"/>
      <stop offset="22%"  stop-color="#E8B838"/>
      <stop offset="60%"  stop-color="#A8780A"/>
      <stop offset="100%" stop-color="#4A3514"/>
    </radialGradient>
    <radialGradient id="prem-p2" cx="42%" cy="32%" r="62%">
      <stop offset="0%"   stop-color="#E0B454"/>
      <stop offset="22%"  stop-color="#B88B14"/>
      <stop offset="60%"  stop-color="#7A5A14"/>
      <stop offset="100%" stop-color="#3D2C18"/>
    </radialGradient>
    <radialGradient id="prem-p3" cx="42%" cy="32%" r="62%">
      <stop offset="0%"   stop-color="#FFF3C8"/>
      <stop offset="25%"  stop-color="#FFD978"/>
      <stop offset="60%"  stop-color="#D4A018"/>
      <stop offset="100%" stop-color="#5A4014"/>
    </radialGradient>
    <radialGradient id="prem-p4" cx="42%" cy="32%" r="62%">
      <stop offset="0%"   stop-color="#E8E480"/>
      <stop offset="22%"  stop-color="#C8B538"/>
      <stop offset="55%"  stop-color="#8B8B20"/>
      <stop offset="100%" stop-color="#4A4818"/>
    </radialGradient>
    <radialGradient id="prem-p5" cx="42%" cy="32%" r="62%">
      <stop offset="0%"   stop-color="#D8A044"/>
      <stop offset="25%"  stop-color="#A8780A"/>
      <stop offset="60%"  stop-color="#5A4014"/>
      <stop offset="100%" stop-color="#2D2010"/>
    </radialGradient>
    <radialGradient id="prem-p6" cx="42%" cy="32%" r="62%">
      <stop offset="0%"   stop-color="#FFCE58"/>
      <stop offset="22%"  stop-color="#D8A018"/>
      <stop offset="60%"  stop-color="#8B6818"/>
      <stop offset="100%" stop-color="#3D2C10"/>
    </radialGradient>
    <radialGradient id="prem-p7" cx="42%" cy="32%" r="62%">
      <stop offset="0%"   stop-color="#FFFAE0"/>
      <stop offset="25%"  stop-color="#F4D060"/>
      <stop offset="60%"  stop-color="#C89318"/>
      <stop offset="100%" stop-color="#5A4014"/>
    </radialGradient>

    <!-- ── Body deep underbase (visible as grout color between
         scales after they're drawn on top). -->
    <radialGradient id="prem-body-deep" cx="50%" cy="32%" r="68%">
      <stop offset="0%"   stop-color="#7A5A1A"/>
      <stop offset="55%"  stop-color="#4A3414"/>
      <stop offset="100%" stop-color="#1F1408"/>
    </radialGradient>

    <!-- ── Cylindrical-depth wash layers ──────────────────────── -->
    <radialGradient id="prem-top-wash" cx="50%" cy="14%" r="48%">
      <stop offset="0%"   stop-color="#FFF5D0" stop-opacity="0.38"/>
      <stop offset="55%"  stop-color="#FFE066" stop-opacity="0.12"/>
      <stop offset="100%" stop-color="#FFE066" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="prem-bottom-wash" cx="50%" cy="94%" r="58%">
      <stop offset="0%"   stop-color="#0F0A02" stop-opacity="0.55"/>
      <stop offset="55%"  stop-color="#1F1408" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="#1F1408" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="prem-side-shading" x1="0" y1="0.5" x2="1" y2="0.5">
      <stop offset="0%"   stop-color="#0A0604" stop-opacity="0.38"/>
      <stop offset="14%"  stop-color="#0A0604" stop-opacity="0.16"/>
      <stop offset="36%"  stop-color="#0A0604" stop-opacity="0"/>
      <stop offset="64%"  stop-color="#0A0604" stop-opacity="0"/>
      <stop offset="86%"  stop-color="#0A0604" stop-opacity="0.16"/>
      <stop offset="100%" stop-color="#0A0604" stop-opacity="0.38"/>
    </linearGradient>

    <!-- ── Luxury background gradient (warm radial backdrop) ───── -->
    <radialGradient id="prem-lux-bg" cx="50%" cy="50%" r="70%">
      <stop offset="0%"   stop-color="#3D2C18" stop-opacity="0.55"/>
      <stop offset="55%"  stop-color="#1A1108" stop-opacity="0.28"/>
      <stop offset="100%" stop-color="#0A0604" stop-opacity="0"/>
    </radialGradient>

    <!-- ── Crown leaf gradients (emerald → teal, three depths) ── -->
    <linearGradient id="prem-leaf-bright" x1="0.5" y1="0" x2="0.5" y2="1">
      <stop offset="0%"   stop-color="#B8FFD8"/>
      <stop offset="20%"  stop-color="#5BD18C"/>
      <stop offset="55%"  stop-color="#22A878"/>
      <stop offset="85%"  stop-color="#0D7058"/>
      <stop offset="100%" stop-color="#063D3A"/>
    </linearGradient>
    <linearGradient id="prem-leaf-mid" x1="0.5" y1="0" x2="0.5" y2="1">
      <stop offset="0%"   stop-color="#7DDDA8"/>
      <stop offset="25%"  stop-color="#2DB078"/>
      <stop offset="65%"  stop-color="#147858"/>
      <stop offset="100%" stop-color="#053828"/>
    </linearGradient>
    <linearGradient id="prem-leaf-deep" x1="0.5" y1="0" x2="0.5" y2="1">
      <stop offset="0%"   stop-color="#2DB078"/>
      <stop offset="35%"  stop-color="#0D6858"/>
      <stop offset="75%"  stop-color="#043828"/>
      <stop offset="100%" stop-color="#01201A"/>
    </linearGradient>

    <!-- Soft warm halo behind the fruit. -->
    <filter id="prem-warm-halo" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="36"/>
    </filter>

    <!-- Body silhouette (slight barrel: rounder middle, gentle
         taper at the shoulder and base). -->
    <path id="prem-body"
          d="M 320 290
             C 200 295, 92 400, 80 540
             C 65 690, 100 838, 220 880
             C 280 900, 360 900, 420 880
             C 540 838, 575 690, 560 540
             C 548 400, 440 295, 320 290 Z"/>
    <clipPath id="prem-body-clip"><use href="#prem-body"/></clipPath>
  </defs>

  <!-- ===== LUXURY BACKGROUND ===== -->
  <rect x="0" y="0" width="640" height="920" fill="url(#prem-lux-bg)"/>

  <!-- Warm golden ambient halo behind the fruit. -->
  <g filter="url(#prem-warm-halo)" opacity="0.55">
    <ellipse cx="320" cy="560" rx="280" ry="320" fill="#C28C12" opacity="0.6"/>
    <ellipse cx="320" cy="380" rx="170" ry="155" fill="#FFD060" opacity="0.55"/>
  </g>

  <!-- ===== CROWN — long sharp geometric leaves, asymmetric ===== -->
  <g class="hero-crown">
    <!-- BACK layer: deepest, longest, widest spread -->
    <g stroke="#01201A" stroke-width="0.6" stroke-linejoin="round">
      <path d="M 320 358 L 70 132 L 96 178 L 320 358 Z" fill="url(#prem-leaf-deep)" opacity="0.93"/>
      <path d="M 320 358 L 570 132 L 544 178 L 320 358 Z" fill="url(#prem-leaf-deep)" opacity="0.93"/>
      <path d="M 320 358 L 116 64 L 148 108 L 320 358 Z" fill="url(#prem-leaf-deep)" opacity="0.95"/>
      <path d="M 320 358 L 524 64 L 492 108 L 320 358 Z" fill="url(#prem-leaf-deep)" opacity="0.95"/>
      <path d="M 320 358 L 198 22 L 232 70 L 320 358 Z" fill="url(#prem-leaf-deep)"/>
      <path d="M 320 358 L 442 22 L 408 70 L 320 358 Z" fill="url(#prem-leaf-deep)"/>
      <path d="M 320 358 L 80 232 L 108 262 L 320 358 Z" fill="url(#prem-leaf-deep)" opacity="0.88"/>
      <path d="M 320 358 L 560 232 L 532 262 L 320 358 Z" fill="url(#prem-leaf-deep)" opacity="0.88"/>
    </g>
    <!-- MID layer: shorter, brighter, fills the front -->
    <g stroke="#053828" stroke-width="0.6" stroke-linejoin="round">
      <path d="M 320 358 L 152 78 L 180 124 L 320 358 Z" fill="url(#prem-leaf-mid)"/>
      <path d="M 320 358 L 488 78 L 460 124 L 320 358 Z" fill="url(#prem-leaf-mid)"/>
      <path d="M 320 358 L 232 34 L 262 76 L 320 358 Z" fill="url(#prem-leaf-mid)"/>
      <path d="M 320 358 L 408 34 L 378 76 L 320 358 Z" fill="url(#prem-leaf-mid)"/>
      <path d="M 320 358 L 268 16 L 296 56 L 320 358 Z" fill="url(#prem-leaf-mid)"/>
      <path d="M 320 358 L 372 16 L 344 56 L 320 358 Z" fill="url(#prem-leaf-mid)"/>
      <!-- subtle asymmetry: lightly tilted side leaves -->
      <path d="M 320 358 L 188 110 L 218 152 L 320 358 Z" fill="url(#prem-leaf-mid)" opacity="0.9"/>
      <path d="M 320 358 L 452 110 L 422 152 L 320 358 Z" fill="url(#prem-leaf-mid)" opacity="0.9"/>
    </g>
    <!-- FRONT layer: brightest emerald centerpieces -->
    <g stroke="#063D3A" stroke-width="0.6" stroke-linejoin="round">
      <path d="M 320 358 L 318 -2 L 332 56 L 320 358 Z" fill="url(#prem-leaf-bright)"/>
      <path d="M 320 358 L 322 -2 L 308 56 L 320 358 Z" fill="url(#prem-leaf-bright)"/>
      <path d="M 320 358 L 302 14 L 326 58 L 320 358 Z" fill="url(#prem-leaf-bright)" opacity="0.96"/>
      <path d="M 320 358 L 338 14 L 314 58 L 320 358 Z" fill="url(#prem-leaf-bright)" opacity="0.96"/>
    </g>
    <!-- Subtle bright spine highlights on the front leaves -->
    <g fill="none" stroke="#B8FFD8" stroke-width="0.9" stroke-linecap="round" opacity="0.55">
      <path d="M 320 6 L 320 220"/>
      <path d="M 312 18 L 296 220"/>
      <path d="M 328 18 L 344 220"/>
    </g>
  </g>

  <!-- ===== PINEAPPLE BODY ===== -->
  <!-- Deep warm underbase shows through between scales as the
       warm-brown "grout" of the eye lattice. -->
  <use href="#prem-body" fill="url(#prem-body-deep)"
       stroke="#2D2010" stroke-width="2.2" stroke-opacity="0.95"/>

  <!-- Premium pillowed-diamond scales, color-varied, warped. -->
  <g clip-path="url(#prem-body-clip)">
        {SCALES}
  </g>

  <!-- ===== CYLINDRICAL DEPTH PASSES (subtle, layered) ===== -->
  <!-- Top-light wash: cool cream highlight along the upper shoulder -->
  <g clip-path="url(#prem-body-clip)">
    <ellipse cx="320" cy="330" rx="240" ry="210" fill="url(#prem-top-wash)"/>
  </g>
  <!-- Side shading: dark left/right vignette → cylindrical roundness -->
  <g clip-path="url(#prem-body-clip)">
    <rect x="0" y="0" width="640" height="920" fill="url(#prem-side-shading)"/>
  </g>
  <!-- Bottom shadow: warm dark fade at the base -->
  <g clip-path="url(#prem-body-clip)">
    <ellipse cx="320" cy="855" rx="280" ry="130" fill="url(#prem-bottom-wash)"/>
  </g>

  <!-- ===== FIBONACCI SPIRAL OVERLAY (keyboard-pop animation) ===== -->
  <g clip-path="url(#prem-body-clip)">
    <g class="pineapple-fibonacci-spirals">
        {SPIRALS}
    </g>
  </g>

  <!-- Final crisp body outline for a clean rim. -->
  <use href="#prem-body" fill="none"
       stroke="#1F1408" stroke-width="2.4" stroke-opacity="0.9"/>
</svg>
"""

_HERO_PINEAPPLE_SVG_PREMIUM = (
    _HERO_PINEAPPLE_SVG_PREMIUM_TEMPLATE
    .replace("{SCALES}", _PINEAPPLE_PREMIUM_SKIN_HTML)
    .replace("{SPIRALS}", _PINEAPPLE_FIBONACCI_SPIRALS_HTML)
)


# ── Premium GLASS pineapple template — translucent 3D crystal ────
# Same body silhouette, warp, lattice, and crown shape as the
# premium variant, but every scale becomes a translucent amber
# facet with an interior gem-cut cross, a specular glint, and a
# luminous gold edge. Crown leaves render as translucent emerald
# crystal. Body backdrop has an internal warm glow you can see
# through the facets. Fibonacci spiral animation overlaid on top.
_HERO_PINEAPPLE_SVG_PREMIUM_GLASS_TEMPLATE = """\
<svg class="hero-pineapple" viewBox="0 0 640 920" xmlns="http://www.w3.org/2000/svg"
     role="img" aria-hidden="true" preserveAspectRatio="xMidYMid meet">
  <style>
    /* ── Translucent glass scales — fill driven by per-variant
       gradient (each gradient stop carries its own opacity), all
       sharing a warm bright-gold edge stroke so the seams read
       as RAISED light-catching ridges, not sunken grout. */
    .hero-pineapple [class^="gsc-g"] {
      stroke: #FFE090;
      stroke-width: 0.55;
      stroke-opacity: 0.85;
      stroke-linejoin: round;
    }
    .hero-pineapple .gsc-g0 { fill: url(#glass-g0); }
    .hero-pineapple .gsc-g1 { fill: url(#glass-g1); }
    .hero-pineapple .gsc-g2 { fill: url(#glass-g2); }
    .hero-pineapple .gsc-g3 { fill: url(#glass-g3); }
    .hero-pineapple .gsc-g5 { fill: url(#glass-g5); }
    .hero-pineapple .gsc-g6 { fill: url(#glass-g6); }
    .hero-pineapple .gsc-g7 { fill: url(#glass-g7); }

    /* Interior facet cross — pale-gold strokes, subtle. */
    .hero-pineapple .gsc-facet {
      stroke: #FFF0B8;
      stroke-width: 0.5;
      stroke-opacity: 0.32;
      stroke-linecap: round;
      pointer-events: none;
    }

    /* Specular glints — bright white ellipses with a slight halo. */
    .hero-pineapple .gsc-glint {
      fill: #FFFFFF;
      fill-opacity: 0.78;
      filter: drop-shadow(0 0 1.2px rgba(255,255,255,0.7));
      pointer-events: none;
    }

    /* Translucent crystal crown — fill opacity makes the leaves
       feel like emerald glass overlapping itself. */
    .hero-pineapple .glass-leaf {
      fill-opacity: 0.72;
    }
    .hero-pineapple .glass-leaf-front {
      fill-opacity: 0.82;
    }

    /* ── Fibonacci spiral KEYBOARD-POP animation overlay ──── */
    .hero-pineapple .spiral-line {
      fill: none;
      stroke-width: 2.6;
      stroke-linecap: round;
      opacity: 0;
      transform-box: fill-box;
      transform-origin: center;
      filter: drop-shadow(0 0 4px currentColor)
              drop-shadow(0 0 10px currentColor);
    }
    .hero-pineapple .spiral-f8 {
      stroke: #FF3D8A; color: #FF3D8A;
      animation: spiralKeyPop8 9s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
    }
    .hero-pineapple .spiral-f13 {
      stroke: #18E5F0; color: #18E5F0;
      animation: spiralKeyPop13 9s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
    }
    .hero-pineapple .spiral-f21 {
      stroke: #FFE74C; color: #FFE74C;
      animation: spiralKeyPop21 9s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
    }
    @keyframes spiralKeyPop8 {
      0%   { opacity: 0; transform: translateY(14px) scale(0.92); }
      7%   { opacity: 1; transform: translateY(-5px) scale(1.06); }
      14%  { opacity: 1; transform: translateY(0)    scale(1); }
      95%  { opacity: 1; transform: translateY(0)    scale(1); }
      100% { opacity: 0; transform: translateY(14px) scale(0.92); }
    }
    @keyframes spiralKeyPop13 {
      0%, 33% { opacity: 0; transform: translateY(14px) scale(0.92); }
      40%     { opacity: 1; transform: translateY(-5px) scale(1.06); }
      47%     { opacity: 1; transform: translateY(0)    scale(1); }
      95%     { opacity: 1; transform: translateY(0)    scale(1); }
      100%    { opacity: 0; transform: translateY(14px) scale(0.92); }
    }
    @keyframes spiralKeyPop21 {
      0%, 66% { opacity: 0; transform: translateY(14px) scale(0.92); }
      73%     { opacity: 1; transform: translateY(-5px) scale(1.06); }
      80%     { opacity: 1; transform: translateY(0)    scale(1); }
      95%     { opacity: 1; transform: translateY(0)    scale(1); }
      100%    { opacity: 0; transform: translateY(14px) scale(0.92); }
    }
    @media (prefers-reduced-motion: reduce) {
      .hero-pineapple .spiral-line { animation: none; opacity: 0.7; }
    }
  </style>
  <defs>
    <!-- ── Translucent amber glass gradients (7 variants) ───────
         Each stop carries its own opacity so the warm body
         underbase shows through every scale. Hot cream highlight
         at the upper-left → bright amber → deep honey edge. -->
    <radialGradient id="glass-g0" cx="40%" cy="30%" r="64%">
      <stop offset="0%"   stop-color="#FFFAE0" stop-opacity="0.96"/>
      <stop offset="22%"  stop-color="#F4CE48" stop-opacity="0.86"/>
      <stop offset="60%"  stop-color="#D8990A" stop-opacity="0.72"/>
      <stop offset="100%" stop-color="#6B4A0A" stop-opacity="0.55"/>
    </radialGradient>
    <radialGradient id="glass-g1" cx="40%" cy="30%" r="64%">
      <stop offset="0%"   stop-color="#FFEFB0" stop-opacity="0.94"/>
      <stop offset="22%"  stop-color="#E8BC38" stop-opacity="0.82"/>
      <stop offset="60%"  stop-color="#B07810" stop-opacity="0.70"/>
      <stop offset="100%" stop-color="#5A3C0C" stop-opacity="0.55"/>
    </radialGradient>
    <radialGradient id="glass-g2" cx="40%" cy="30%" r="64%">
      <stop offset="0%"   stop-color="#E8C470" stop-opacity="0.92"/>
      <stop offset="22%"  stop-color="#B88B14" stop-opacity="0.80"/>
      <stop offset="60%"  stop-color="#7A5810" stop-opacity="0.68"/>
      <stop offset="100%" stop-color="#3D2A08" stop-opacity="0.55"/>
    </radialGradient>
    <radialGradient id="glass-g3" cx="40%" cy="30%" r="64%">
      <stop offset="0%"   stop-color="#FFFFE8" stop-opacity="0.98"/>
      <stop offset="25%"  stop-color="#FFE078" stop-opacity="0.86"/>
      <stop offset="60%"  stop-color="#D8A018" stop-opacity="0.72"/>
      <stop offset="100%" stop-color="#5A3C0C" stop-opacity="0.55"/>
    </radialGradient>
    <radialGradient id="glass-g5" cx="40%" cy="30%" r="64%">
      <stop offset="0%"   stop-color="#E0AC50" stop-opacity="0.92"/>
      <stop offset="22%"  stop-color="#B07810" stop-opacity="0.78"/>
      <stop offset="60%"  stop-color="#5A3C0A" stop-opacity="0.66"/>
      <stop offset="100%" stop-color="#2D1F08" stop-opacity="0.55"/>
    </radialGradient>
    <radialGradient id="glass-g6" cx="40%" cy="30%" r="64%">
      <stop offset="0%"   stop-color="#FFD460" stop-opacity="0.95"/>
      <stop offset="22%"  stop-color="#D8A018" stop-opacity="0.82"/>
      <stop offset="60%"  stop-color="#8B6810" stop-opacity="0.68"/>
      <stop offset="100%" stop-color="#3D2A08" stop-opacity="0.55"/>
    </radialGradient>
    <radialGradient id="glass-g7" cx="40%" cy="30%" r="64%">
      <stop offset="0%"   stop-color="#FFFFFA" stop-opacity="0.98"/>
      <stop offset="22%"  stop-color="#FFE078" stop-opacity="0.88"/>
      <stop offset="60%"  stop-color="#C89318" stop-opacity="0.72"/>
      <stop offset="100%" stop-color="#5A3C0C" stop-opacity="0.55"/>
    </radialGradient>

    <!-- ── Body underbase: luminous amber core (internal glow). -->
    <radialGradient id="glass-body-core" cx="50%" cy="40%" r="68%">
      <stop offset="0%"   stop-color="#FFE066" stop-opacity="0.95"/>
      <stop offset="40%"  stop-color="#D8A018" stop-opacity="0.85"/>
      <stop offset="75%"  stop-color="#7A5410" stop-opacity="0.78"/>
      <stop offset="100%" stop-color="#2D1F08" stop-opacity="0.9"/>
    </radialGradient>

    <!-- Internal-glow blur (the warm radiance you see through
         the facets when light passes through real glass). -->
    <filter id="glass-internal-glow" x="-30%" y="-30%"
            width="160%" height="160%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="22"/>
    </filter>

    <!-- ── Cylindrical depth washes (lighter for glass) ──────── -->
    <radialGradient id="glass-top-wash" cx="50%" cy="14%" r="48%">
      <stop offset="0%"   stop-color="#FFFFF0" stop-opacity="0.42"/>
      <stop offset="55%"  stop-color="#FFE066" stop-opacity="0.14"/>
      <stop offset="100%" stop-color="#FFE066" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glass-bottom-wash" cx="50%" cy="94%" r="58%">
      <stop offset="0%"   stop-color="#0F0A02" stop-opacity="0.42"/>
      <stop offset="55%"  stop-color="#1F1408" stop-opacity="0.14"/>
      <stop offset="100%" stop-color="#1F1408" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="glass-side-shading" x1="0" y1="0.5" x2="1" y2="0.5">
      <stop offset="0%"   stop-color="#0A0604" stop-opacity="0.32"/>
      <stop offset="14%"  stop-color="#0A0604" stop-opacity="0.12"/>
      <stop offset="36%"  stop-color="#0A0604" stop-opacity="0"/>
      <stop offset="64%"  stop-color="#0A0604" stop-opacity="0"/>
      <stop offset="86%"  stop-color="#0A0604" stop-opacity="0.12"/>
      <stop offset="100%" stop-color="#0A0604" stop-opacity="0.32"/>
    </linearGradient>

    <!-- ── Luxury cool-warm gradient background. -->
    <radialGradient id="glass-lux-bg" cx="50%" cy="50%" r="72%">
      <stop offset="0%"   stop-color="#3D2C18" stop-opacity="0.5"/>
      <stop offset="55%"  stop-color="#1A1108" stop-opacity="0.28"/>
      <stop offset="100%" stop-color="#0A0604" stop-opacity="0"/>
    </radialGradient>

    <!-- ── Translucent emerald glass leaf gradients ──────────── -->
    <linearGradient id="glass-leaf-bright" x1="0.5" y1="0" x2="0.5" y2="1">
      <stop offset="0%"   stop-color="#D0FFE8" stop-opacity="0.95"/>
      <stop offset="22%"  stop-color="#60E098" stop-opacity="0.85"/>
      <stop offset="60%"  stop-color="#22A878" stop-opacity="0.72"/>
      <stop offset="100%" stop-color="#0D5848" stop-opacity="0.6"/>
    </linearGradient>
    <linearGradient id="glass-leaf-mid" x1="0.5" y1="0" x2="0.5" y2="1">
      <stop offset="0%"   stop-color="#90EAB8" stop-opacity="0.88"/>
      <stop offset="28%"  stop-color="#2DB078" stop-opacity="0.78"/>
      <stop offset="65%"  stop-color="#147858" stop-opacity="0.66"/>
      <stop offset="100%" stop-color="#053828" stop-opacity="0.55"/>
    </linearGradient>
    <linearGradient id="glass-leaf-deep" x1="0.5" y1="0" x2="0.5" y2="1">
      <stop offset="0%"   stop-color="#40C088" stop-opacity="0.85"/>
      <stop offset="35%"  stop-color="#147858" stop-opacity="0.70"/>
      <stop offset="75%"  stop-color="#053828" stop-opacity="0.58"/>
      <stop offset="100%" stop-color="#01201A" stop-opacity="0.5"/>
    </linearGradient>

    <!-- Soft warm halo behind the fruit. -->
    <filter id="glass-warm-halo" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="40"/>
    </filter>

    <!-- Body silhouette (same as premium). -->
    <path id="glass-body"
          d="M 320 290
             C 200 295, 92 400, 80 540
             C 65 690, 100 838, 220 880
             C 280 900, 360 900, 420 880
             C 540 838, 575 690, 560 540
             C 548 400, 440 295, 320 290 Z"/>
    <clipPath id="glass-body-clip"><use href="#glass-body"/></clipPath>
  </defs>

  <!-- ===== LUXURY BACKGROUND ===== -->
  <rect x="0" y="0" width="640" height="920" fill="url(#glass-lux-bg)"/>

  <!-- Warm golden halo behind the fruit (transmitted-light look). -->
  <g filter="url(#glass-warm-halo)" opacity="0.65">
    <ellipse cx="320" cy="560" rx="290" ry="330" fill="#D49A0A" opacity="0.6"/>
    <ellipse cx="320" cy="380" rx="180" ry="160" fill="#FFE066" opacity="0.65"/>
  </g>

  <!-- ===== CROWN — translucent emerald crystal leaves ===== -->
  <g class="hero-crown">
    <!-- BACK layer: deep translucent emerald, longest, widest -->
    <g stroke="#053828" stroke-width="0.5" stroke-linejoin="round">
      <path class="glass-leaf" d="M 320 358 L 70 132 L 96 178 L 320 358 Z" fill="url(#glass-leaf-deep)"/>
      <path class="glass-leaf" d="M 320 358 L 570 132 L 544 178 L 320 358 Z" fill="url(#glass-leaf-deep)"/>
      <path class="glass-leaf" d="M 320 358 L 116 64 L 148 108 L 320 358 Z" fill="url(#glass-leaf-deep)"/>
      <path class="glass-leaf" d="M 320 358 L 524 64 L 492 108 L 320 358 Z" fill="url(#glass-leaf-deep)"/>
      <path class="glass-leaf" d="M 320 358 L 198 22 L 232 70 L 320 358 Z" fill="url(#glass-leaf-deep)"/>
      <path class="glass-leaf" d="M 320 358 L 442 22 L 408 70 L 320 358 Z" fill="url(#glass-leaf-deep)"/>
      <path class="glass-leaf" d="M 320 358 L 80 232 L 108 262 L 320 358 Z" fill="url(#glass-leaf-deep)"/>
      <path class="glass-leaf" d="M 320 358 L 560 232 L 532 262 L 320 358 Z" fill="url(#glass-leaf-deep)"/>
    </g>
    <!-- MID layer: brighter translucent emerald, shorter -->
    <g stroke="#0D5848" stroke-width="0.5" stroke-linejoin="round">
      <path class="glass-leaf" d="M 320 358 L 152 78 L 180 124 L 320 358 Z" fill="url(#glass-leaf-mid)"/>
      <path class="glass-leaf" d="M 320 358 L 488 78 L 460 124 L 320 358 Z" fill="url(#glass-leaf-mid)"/>
      <path class="glass-leaf" d="M 320 358 L 232 34 L 262 76 L 320 358 Z" fill="url(#glass-leaf-mid)"/>
      <path class="glass-leaf" d="M 320 358 L 408 34 L 378 76 L 320 358 Z" fill="url(#glass-leaf-mid)"/>
      <path class="glass-leaf" d="M 320 358 L 268 16 L 296 56 L 320 358 Z" fill="url(#glass-leaf-mid)"/>
      <path class="glass-leaf" d="M 320 358 L 372 16 L 344 56 L 320 358 Z" fill="url(#glass-leaf-mid)"/>
      <path class="glass-leaf" d="M 320 358 L 188 110 L 218 152 L 320 358 Z" fill="url(#glass-leaf-mid)"/>
      <path class="glass-leaf" d="M 320 358 L 452 110 L 422 152 L 320 358 Z" fill="url(#glass-leaf-mid)"/>
    </g>
    <!-- FRONT layer: brightest translucent emerald centerpieces -->
    <g stroke="#0D5848" stroke-width="0.5" stroke-linejoin="round">
      <path class="glass-leaf-front" d="M 320 358 L 318 -2 L 332 56 L 320 358 Z" fill="url(#glass-leaf-bright)"/>
      <path class="glass-leaf-front" d="M 320 358 L 322 -2 L 308 56 L 320 358 Z" fill="url(#glass-leaf-bright)"/>
      <path class="glass-leaf-front" d="M 320 358 L 302 14 L 326 58 L 320 358 Z" fill="url(#glass-leaf-bright)"/>
      <path class="glass-leaf-front" d="M 320 358 L 338 14 L 314 58 L 320 358 Z" fill="url(#glass-leaf-bright)"/>
    </g>
    <!-- Bright mint spine highlights (catch-the-light edge) -->
    <g fill="none" stroke="#D0FFE8" stroke-width="1.0" stroke-linecap="round" opacity="0.7">
      <path d="M 320 6 L 320 220"/>
      <path d="M 312 18 L 296 220"/>
      <path d="M 328 18 L 344 220"/>
    </g>
    <!-- Per-leaf tip glints — small white dots at each leaf tip -->
    <g fill="#FFFFFF" fill-opacity="0.85">
      <circle cx="320" cy="-2" r="1.6"/>
      <circle cx="268" cy="16" r="1.4"/>
      <circle cx="372" cy="16" r="1.4"/>
      <circle cx="232" cy="34" r="1.3"/>
      <circle cx="408" cy="34" r="1.3"/>
      <circle cx="152" cy="78" r="1.2"/>
      <circle cx="488" cy="78" r="1.2"/>
    </g>
  </g>

  <!-- ===== GLASS BODY ===== -->
  <!-- Luminous amber CORE — the internal light source the facets
       refract. Heavily blurred so it reads as soft inner glow. -->
  <g clip-path="url(#glass-body-clip)" filter="url(#glass-internal-glow)" opacity="0.9">
    <use href="#glass-body" fill="url(#glass-body-core)"/>
  </g>
  <!-- Sharper underbase so the edges of the body are still defined. -->
  <use href="#glass-body" fill="url(#glass-body-core)" opacity="0.55"/>

  <!-- Per-scale translucent facets + interior cross + glints. -->
  <g clip-path="url(#glass-body-clip)">
        {SCALES}
  </g>

  <!-- ===== CYLINDRICAL DEPTH PASSES ===== -->
  <g clip-path="url(#glass-body-clip)">
    <ellipse cx="320" cy="330" rx="240" ry="210" fill="url(#glass-top-wash)"/>
  </g>
  <g clip-path="url(#glass-body-clip)">
    <rect x="0" y="0" width="640" height="920" fill="url(#glass-side-shading)"/>
  </g>
  <g clip-path="url(#glass-body-clip)">
    <ellipse cx="320" cy="855" rx="280" ry="130" fill="url(#glass-bottom-wash)"/>
  </g>

  <!-- A big specular streak across the upper-left of the body —
       the way light hits a real glass sphere. -->
  <g clip-path="url(#glass-body-clip)" opacity="0.55"
     style="mix-blend-mode: screen">
    <ellipse cx="220" cy="400" rx="120" ry="60" fill="#FFFAE0"
             transform="rotate(-22 220 400)"/>
  </g>

  <!-- ===== FIBONACCI SPIRAL OVERLAY ===== -->
  <g clip-path="url(#glass-body-clip)">
    <g class="pineapple-fibonacci-spirals">
        {SPIRALS}
    </g>
  </g>

  <!-- Crisp body rim. -->
  <use href="#glass-body" fill="none"
       stroke="#7A5A1A" stroke-width="2.0" stroke-opacity="0.85"/>
</svg>
"""

_HERO_PINEAPPLE_SVG_PREMIUM_GLASS = (
    _HERO_PINEAPPLE_SVG_PREMIUM_GLASS_TEMPLATE
    .replace("{SCALES}", _PINEAPPLE_GLASS_SKIN_HTML)
    .replace("{SPIRALS}", _PINEAPPLE_FIBONACCI_SPIRALS_HTML)
)


# ── Photo-grade crystal pineapple, NO background ──────────────────
# Pure SVG synthesis of the user's crystal-pineapple reference
# image: every scale is built from 4 lit triangular facets (true
# cut-gemstone topology with upper-left light), the body is a
# warm translucent amber core, the crown is translucent emerald
# blades, and the canvas is left fully transparent. Fibonacci
# spiral keyboard-pop animation overlaid on top.
_HERO_PINEAPPLE_SVG_GLASS_NOBG_TEMPLATE = """\
<svg class="hero-pineapple" viewBox="0 0 640 920" xmlns="http://www.w3.org/2000/svg"
     role="img" aria-hidden="true" preserveAspectRatio="xMidYMid meet">
  <style>
    /* ── 4 facet shades for each scale (upper-left light) ──── */
    .hero-pineapple .gv-ul { fill: url(#gv-amber-ul); }
    .hero-pineapple .gv-ur { fill: url(#gv-amber-ur); }
    .hero-pineapple .gv-ll { fill: url(#gv-amber-ll); }
    .hero-pineapple .gv-lr { fill: url(#gv-amber-lr); }

    /* ── Per-scale brightness tier (multiplies the facet color). */
    .hero-pineapple .gv-t0 { fill-opacity: 0.95; }
    .hero-pineapple .gv-t1 { fill-opacity: 0.82; }
    .hero-pineapple .gv-t2 { fill-opacity: 0.68; }

    /* Raised gold perimeter ridge between scales. */
    .hero-pineapple .gv-edge {
      fill: none;
      stroke: #C89318;
      stroke-width: 0.55;
      stroke-opacity: 0.7;
      stroke-linejoin: round;
    }

    /* Specular glints at scale peaks. */
    .hero-pineapple .gv-glint {
      fill: #FFFFFF;
      fill-opacity: 0.85;
      filter: drop-shadow(0 0 1.4px rgba(255,255,255,0.7));
      pointer-events: none;
    }

    /* Translucent emerald glass crown. */
    .hero-pineapple .gv-leaf       { fill-opacity: 0.78; }
    .hero-pineapple .gv-leaf-front { fill-opacity: 0.88; }

    /* ── Fibonacci spiral KEYBOARD-POP animation overlay ──── */
    .hero-pineapple .spiral-line {
      fill: none;
      stroke-width: 2.6;
      stroke-linecap: round;
      opacity: 0;
      transform-box: fill-box;
      transform-origin: center;
      filter: drop-shadow(0 0 4px currentColor)
              drop-shadow(0 0 10px currentColor);
    }
    .hero-pineapple .spiral-f8 {
      stroke: #FF3D8A; color: #FF3D8A;
      animation: spiralKeyPop8 9s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
    }
    .hero-pineapple .spiral-f13 {
      stroke: #18E5F0; color: #18E5F0;
      animation: spiralKeyPop13 9s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
    }
    .hero-pineapple .spiral-f21 {
      stroke: #FFE74C; color: #FFE74C;
      animation: spiralKeyPop21 9s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
    }
    @keyframes spiralKeyPop8 {
      0%   { opacity: 0; transform: translateY(14px) scale(0.92); }
      7%   { opacity: 1; transform: translateY(-5px) scale(1.06); }
      14%  { opacity: 1; transform: translateY(0)    scale(1); }
      95%  { opacity: 1; transform: translateY(0)    scale(1); }
      100% { opacity: 0; transform: translateY(14px) scale(0.92); }
    }
    @keyframes spiralKeyPop13 {
      0%, 33% { opacity: 0; transform: translateY(14px) scale(0.92); }
      40%     { opacity: 1; transform: translateY(-5px) scale(1.06); }
      47%     { opacity: 1; transform: translateY(0)    scale(1); }
      95%     { opacity: 1; transform: translateY(0)    scale(1); }
      100%    { opacity: 0; transform: translateY(14px) scale(0.92); }
    }
    @keyframes spiralKeyPop21 {
      0%, 66% { opacity: 0; transform: translateY(14px) scale(0.92); }
      73%     { opacity: 1; transform: translateY(-5px) scale(1.06); }
      80%     { opacity: 1; transform: translateY(0)    scale(1); }
      95%     { opacity: 1; transform: translateY(0)    scale(1); }
      100%    { opacity: 0; transform: translateY(14px) scale(0.92); }
    }
    @media (prefers-reduced-motion: reduce) {
      .hero-pineapple .spiral-line { animation: none; opacity: 0.7; }
    }
  </style>
  <defs>
    <!-- ── Per-facet amber gradients ─────────────────────────────
         Each facet is a small linear gradient running from the
         scale center outward (the "ridge" → the "valley"), so the
         pyramid shape reads correctly. Brightness ranks: UL > UR
         > LL > LR (upper-left light). -->
    <linearGradient id="gv-amber-ul" x1="1" y1="1" x2="0" y2="0">
      <stop offset="0%"   stop-color="#7A5410" stop-opacity="0.85"/>
      <stop offset="55%"  stop-color="#F4C430" stop-opacity="0.95"/>
      <stop offset="100%" stop-color="#FFFAE0" stop-opacity="0.98"/>
    </linearGradient>
    <linearGradient id="gv-amber-ur" x1="0" y1="1" x2="1" y2="0">
      <stop offset="0%"   stop-color="#5A3C0A" stop-opacity="0.85"/>
      <stop offset="55%"  stop-color="#D8A018" stop-opacity="0.95"/>
      <stop offset="100%" stop-color="#FFE078" stop-opacity="0.96"/>
    </linearGradient>
    <linearGradient id="gv-amber-ll" x1="1" y1="0" x2="0" y2="1">
      <stop offset="0%"   stop-color="#3D2A08" stop-opacity="0.85"/>
      <stop offset="55%"  stop-color="#A8780A" stop-opacity="0.88"/>
      <stop offset="100%" stop-color="#D8A018" stop-opacity="0.90"/>
    </linearGradient>
    <linearGradient id="gv-amber-lr" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%"   stop-color="#2D1F08" stop-opacity="0.88"/>
      <stop offset="55%"  stop-color="#7A5410" stop-opacity="0.85"/>
      <stop offset="100%" stop-color="#A8780A" stop-opacity="0.82"/>
    </linearGradient>

    <!-- ── Body warm amber core (the internal glow visible
         through every translucent facet). -->
    <radialGradient id="gv-body-core" cx="42%" cy="34%" r="68%">
      <stop offset="0%"   stop-color="#FFE680" stop-opacity="0.95"/>
      <stop offset="35%"  stop-color="#E8B838" stop-opacity="0.92"/>
      <stop offset="68%"  stop-color="#A8780A" stop-opacity="0.88"/>
      <stop offset="100%" stop-color="#3D2A08" stop-opacity="0.92"/>
    </radialGradient>

    <!-- ── Translucent emerald crown gradients ───────────────── -->
    <linearGradient id="gv-leaf-bright" x1="0.5" y1="0" x2="0.5" y2="1">
      <stop offset="0%"   stop-color="#D8FFE8" stop-opacity="0.95"/>
      <stop offset="22%"  stop-color="#60E098" stop-opacity="0.88"/>
      <stop offset="60%"  stop-color="#22A878" stop-opacity="0.78"/>
      <stop offset="100%" stop-color="#0D5848" stop-opacity="0.7"/>
    </linearGradient>
    <linearGradient id="gv-leaf-mid" x1="0.5" y1="0" x2="0.5" y2="1">
      <stop offset="0%"   stop-color="#90EAB8" stop-opacity="0.9"/>
      <stop offset="28%"  stop-color="#2DB078" stop-opacity="0.8"/>
      <stop offset="65%"  stop-color="#147858" stop-opacity="0.7"/>
      <stop offset="100%" stop-color="#053828" stop-opacity="0.62"/>
    </linearGradient>
    <linearGradient id="gv-leaf-deep" x1="0.5" y1="0" x2="0.5" y2="1">
      <stop offset="0%"   stop-color="#40C088" stop-opacity="0.88"/>
      <stop offset="35%"  stop-color="#147858" stop-opacity="0.74"/>
      <stop offset="75%"  stop-color="#053828" stop-opacity="0.62"/>
      <stop offset="100%" stop-color="#01201A" stop-opacity="0.55"/>
    </linearGradient>

    <!-- Body silhouette (same as premium). -->
    <path id="gv-body"
          d="M 320 290
             C 200 295, 92 400, 80 540
             C 65 690, 100 838, 220 880
             C 280 900, 360 900, 420 880
             C 540 838, 575 690, 560 540
             C 548 400, 440 295, 320 290 Z"/>
    <clipPath id="gv-body-clip"><use href="#gv-body"/></clipPath>
  </defs>

  <!-- NO BACKGROUND — canvas stays transparent. -->

  <!-- ===== CROWN — translucent emerald crystal blades ===== -->
  <g class="hero-crown">
    <g stroke="#053828" stroke-width="0.5" stroke-linejoin="round">
      <path class="gv-leaf" d="M 320 358 L 70 132 L 96 178 L 320 358 Z" fill="url(#gv-leaf-deep)"/>
      <path class="gv-leaf" d="M 320 358 L 570 132 L 544 178 L 320 358 Z" fill="url(#gv-leaf-deep)"/>
      <path class="gv-leaf" d="M 320 358 L 116 64 L 148 108 L 320 358 Z" fill="url(#gv-leaf-deep)"/>
      <path class="gv-leaf" d="M 320 358 L 524 64 L 492 108 L 320 358 Z" fill="url(#gv-leaf-deep)"/>
      <path class="gv-leaf" d="M 320 358 L 198 22 L 232 70 L 320 358 Z" fill="url(#gv-leaf-deep)"/>
      <path class="gv-leaf" d="M 320 358 L 442 22 L 408 70 L 320 358 Z" fill="url(#gv-leaf-deep)"/>
      <path class="gv-leaf" d="M 320 358 L 80 232 L 108 262 L 320 358 Z" fill="url(#gv-leaf-deep)"/>
      <path class="gv-leaf" d="M 320 358 L 560 232 L 532 262 L 320 358 Z" fill="url(#gv-leaf-deep)"/>
    </g>
    <g stroke="#0D5848" stroke-width="0.5" stroke-linejoin="round">
      <path class="gv-leaf" d="M 320 358 L 152 78 L 180 124 L 320 358 Z" fill="url(#gv-leaf-mid)"/>
      <path class="gv-leaf" d="M 320 358 L 488 78 L 460 124 L 320 358 Z" fill="url(#gv-leaf-mid)"/>
      <path class="gv-leaf" d="M 320 358 L 232 34 L 262 76 L 320 358 Z" fill="url(#gv-leaf-mid)"/>
      <path class="gv-leaf" d="M 320 358 L 408 34 L 378 76 L 320 358 Z" fill="url(#gv-leaf-mid)"/>
      <path class="gv-leaf" d="M 320 358 L 268 16 L 296 56 L 320 358 Z" fill="url(#gv-leaf-mid)"/>
      <path class="gv-leaf" d="M 320 358 L 372 16 L 344 56 L 320 358 Z" fill="url(#gv-leaf-mid)"/>
      <path class="gv-leaf" d="M 320 358 L 188 110 L 218 152 L 320 358 Z" fill="url(#gv-leaf-mid)"/>
      <path class="gv-leaf" d="M 320 358 L 452 110 L 422 152 L 320 358 Z" fill="url(#gv-leaf-mid)"/>
    </g>
    <g stroke="#0D5848" stroke-width="0.5" stroke-linejoin="round">
      <path class="gv-leaf-front" d="M 320 358 L 318 -2 L 332 56 L 320 358 Z" fill="url(#gv-leaf-bright)"/>
      <path class="gv-leaf-front" d="M 320 358 L 322 -2 L 308 56 L 320 358 Z" fill="url(#gv-leaf-bright)"/>
      <path class="gv-leaf-front" d="M 320 358 L 302 14 L 326 58 L 320 358 Z" fill="url(#gv-leaf-bright)"/>
      <path class="gv-leaf-front" d="M 320 358 L 338 14 L 314 58 L 320 358 Z" fill="url(#gv-leaf-bright)"/>
    </g>
    <!-- Bright mint spine highlights -->
    <g fill="none" stroke="#D8FFE8" stroke-width="1.0" stroke-linecap="round" opacity="0.75">
      <path d="M 320 6 L 320 220"/>
      <path d="M 312 18 L 296 220"/>
      <path d="M 328 18 L 344 220"/>
    </g>
    <!-- Per-leaf tip glints -->
    <g fill="#FFFFFF" fill-opacity="0.85">
      <circle cx="320" cy="-2" r="1.7"/>
      <circle cx="268" cy="16" r="1.5"/>
      <circle cx="372" cy="16" r="1.5"/>
      <circle cx="232" cy="34" r="1.4"/>
      <circle cx="408" cy="34" r="1.4"/>
      <circle cx="152" cy="78" r="1.3"/>
      <circle cx="488" cy="78" r="1.3"/>
    </g>
  </g>

  <!-- ===== GLASS BODY ===== -->
  <!-- Warm amber core — the internal glow you see through every
       translucent facet. Drawn once at full opacity as the body
       backdrop. -->
  <use href="#gv-body" fill="url(#gv-body-core)"/>

  <!-- Per-scale 4-facet pyramids + perimeter ridges + glints. -->
  <g clip-path="url(#gv-body-clip)">
        {SCALES}
  </g>

  <!-- Big specular sweep across the upper-left of the body
       (the broad light reflection you see on a real glass sphere). -->
  <g clip-path="url(#gv-body-clip)" opacity="0.55"
     style="mix-blend-mode: screen">
    <ellipse cx="220" cy="430" rx="130" ry="62" fill="#FFFAE0"
             transform="rotate(-22 220 430)"/>
  </g>

  <!-- ===== FIBONACCI SPIRAL OVERLAY ===== -->
  <g clip-path="url(#gv-body-clip)">
    <g class="pineapple-fibonacci-spirals">
        {SPIRALS}
    </g>
  </g>

  <!-- Crisp body rim (subtle, warm). -->
  <use href="#gv-body" fill="none"
       stroke="#7A5A1A" stroke-width="1.8" stroke-opacity="0.85"/>
</svg>
"""

_HERO_PINEAPPLE_SVG_GLASS_NOBG = (
    _HERO_PINEAPPLE_SVG_GLASS_NOBG_TEMPLATE
    .replace("{SCALES}", _PINEAPPLE_GLASS_V2_SKIN_HTML)
    .replace("{SPIRALS}", _PINEAPPLE_FIBONACCI_SPIRALS_HTML)
)


# Literal-photograph variant (current crop: the crystal pineapple
# sculpture) with the Fibonacci spiral keyboard-pop overlay aligned
# to the photographed fruit body.
_HERO_PINEAPPLE_SVG_PHOTO = (
    _HERO_PINEAPPLE_SVG_PHOTO_TEMPLATE
    .replace("{PHOTO_URI}", _PINEAPPLE_PHOTO_DATA_URI)
    .replace("{SPIRALS}", _PINEAPPLE_FIBONACCI_SPIRALS_PHOTO_HTML)
)

def _build_hero_pineapple_svg_flat_minimal() -> str:
    """Concept A flat-minimal pineapple (design mockup style).

    Flat gold body + 45° diamond grid, layered green crown. Body extends
    below the viewBox; .hero / .hero-art overflow clips the lower third.
    """
    return """\
<svg class="hero-pineapple" viewBox="0 0 400 560" xmlns="http://www.w3.org/2000/svg"
     role="img" aria-label="Pineapple illustration" preserveAspectRatio="xMidYMax meet">
  <defs>
    <linearGradient id="fm-crown-mid" x1="0.5" y1="0" x2="0.5" y2="1">
      <stop offset="0%" stop-color="#81C784"/>
      <stop offset="100%" stop-color="#43A047"/>
    </linearGradient>
    <linearGradient id="fm-crown-deep" x1="0.5" y1="0" x2="0.5" y2="1">
      <stop offset="0%" stop-color="#4CAF50"/>
      <stop offset="100%" stop-color="#2E7D32"/>
    </linearGradient>
    <pattern id="fm-diamond-grid" x="0" y="0" width="34" height="34"
             patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
      <rect x="0.5" y="0.5" width="33" height="33" rx="4.5"
            fill="none" stroke="#D0870B" stroke-width="1.2" stroke-opacity="0.68"/>
      <path d="M 0 34 L 0 0 L 34 0" fill="none"
            stroke="#FFF8E0" stroke-width="0.5" stroke-opacity="0.5"/>
      <circle cx="17" cy="17" r="1.3" fill="#E09010" fill-opacity="0.46"/>
    </pattern>
    <path id="fm-body-path"
          d="M 200 90
             C 134 94, 88 156, 82 244
             C 74 372, 100 516, 160 636
             C 178 672, 222 672, 240 636
             C 300 516, 326 372, 318 244
             C 312 156, 266 94, 200 90 Z"/>
    <clipPath id="fm-body-clip"><use href="#fm-body-path"/></clipPath>
    <filter id="fm-fruit-shadow" x="-25%" y="-15%" width="150%" height="140%">
      <feDropShadow dx="8" dy="10" stdDeviation="8"
                    flood-color="#8B5A2B" flood-opacity="0.22"/>
    </filter>
  </defs>
  <g filter="url(#fm-fruit-shadow)">
    <g class="hero-crown">
      <path d="M 200 88 L 170 10 L 190 46 Z" fill="url(#fm-crown-deep)" stroke="#1B5E20" stroke-width="0.62"/>
      <path d="M 200 88 L 230 10 L 210 46 Z" fill="url(#fm-crown-deep)" stroke="#1B5E20" stroke-width="0.62"/>
      <path d="M 200 88 L 146 32 L 168 62 Z" fill="#2E7D32" stroke="#1B5E20" stroke-width="0.56"/>
      <path d="M 200 88 L 254 32 L 232 62 Z" fill="#2E7D32" stroke="#1B5E20" stroke-width="0.56"/>
      <path d="M 200 88 L 126 58 L 150 82 Z" fill="#2E7D32" stroke="#1B5E20" stroke-width="0.52" opacity="0.9"/>
      <path d="M 200 88 L 274 58 L 250 82 Z" fill="#2E7D32" stroke="#1B5E20" stroke-width="0.52" opacity="0.9"/>
      <path d="M 200 88 L 200 2 L 214 42 Z" fill="#A5D6A7" stroke="#1B5E20" stroke-width="0.62"/>
      <path d="M 200 88 L 200 2 L 186 42 Z" fill="url(#fm-crown-mid)" stroke="#1B5E20" stroke-width="0.62"/>
    </g>
    <use href="#fm-body-path" fill="#F8B63A" stroke="#C68A12" stroke-width="1.9"/>
    <g clip-path="url(#fm-body-clip)">
      <rect x="40" y="74" width="320" height="500" fill="url(#fm-diamond-grid)"/>
    </g>
    <use href="#fm-body-path" fill="none" stroke="#B8860B" stroke-width="1.7" stroke-opacity="0.42"/>
  </g>
</svg>"""


_HERO_PINEAPPLE_SVG_FLAT_MINIMAL = _build_hero_pineapple_svg_flat_minimal()

# ── Active design: flat minimal pineapple (Concept A) ─────────────
# Sits on the hero gradient directly (no inner card); static, no float
# animation. Legacy crystal PNG / glass SVG variants remain for forks.
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

  <!-- ambient sun aura -->
  <circle cx="320" cy="520" r="340" fill="#FFD700" opacity="0.18"/>
  <circle cx="320" cy="520" r="260" fill="#FFE27A" opacity="0.28"/>

  <!-- back leaves (far layer) -->
  <g filter="url(#soft-shadow)">
    <path d="M 210 340 Q 150 180 90 80  Q 140 220 170 330 Z"  fill="url(#leaf-back)"/>
    <path d="M 430 340 Q 490 180 550 80 Q 500 220 470 330 Z"  fill="url(#leaf-back)"/>
    <path d="M 260 345 Q 220 140 200 20 Q 250 180 265 335 Z"  fill="url(#leaf-back)"/>
    <path d="M 380 345 Q 420 140 440 20 Q 390 180 375 335 Z"  fill="url(#leaf-back)"/>
  </g>

  <!-- mid leaves -->
  <g>
    <path d="M 240 355 Q 210 170 190 40  Q 245 200 258 345 Z" fill="url(#leaf-mid)"/>
    <path d="M 400 355 Q 430 170 450 40  Q 395 200 382 345 Z" fill="url(#leaf-mid)"/>
    <path d="M 285 355 Q 270 130 260 0   Q 295 170 298 345 Z" fill="url(#leaf-mid)"/>
    <path d="M 355 355 Q 370 130 380 0   Q 345 170 342 345 Z" fill="url(#leaf-mid)"/>
  </g>

  <!-- front leaves (tall, center) -->
  <g>
    <path d="M 315 360 Q 308 140 318 15 Q 325 160 325 355 Z" fill="url(#leaf-front)"/>
    <path d="M 325 360 Q 335 140 322 15 Q 317 160 315 355 Z" fill="url(#leaf-front)" opacity="0.85"/>
    <!-- central leaf highlights -->
    <path d="M 320 140 Q 322 80 325 30" stroke="#E8F5E9" stroke-width="2" fill="none" opacity="0.6"/>
    <path d="M 300 200 Q 292 120 280 50" stroke="#C8E6C9" stroke-width="1.5" fill="none" opacity="0.5"/>
    <path d="M 340 200 Q 348 120 360 50" stroke="#C8E6C9" stroke-width="1.5" fill="none" opacity="0.5"/>
  </g>

  <!-- Body -->
  <g filter="url(#soft-shadow)">
    <ellipse cx="320" cy="580" rx="240" ry="300" fill="url(#body-grad)"
             stroke="#8B5A2B" stroke-width="5"/>
  </g>
  <!-- Diamond lattice overlay clipped to body -->
  <ellipse cx="320" cy="580" rx="236" ry="296" fill="url(#diamond)" opacity="0.85"/>
  <!-- Sheen -->
  <ellipse cx="250" cy="470" rx="110" ry="150" fill="url(#body-sheen)"/>
  <!-- Bottom shadow crescent -->
  <path d="M 130 720 Q 320 920 510 720 Q 430 870 320 880 Q 210 870 130 720 Z"
        fill="#8B5A2B" opacity="0.18"/>

  <!-- Floating little leaf accents (decorative particles) -->
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
    # SKILL.md layout (`.codebase-almanac/codebase-analysis.json` +
    # `.codebase-almanac/enrichment.json`) — without auto-discovery the
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
    tab_labels.update({
        "security": "Security",
        "suggestions": "Strategic Suggestions",
        "pitch": "Idea Validation",
        "simulation": "Future Outlook",
    })

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

    # === Code Health Check: 4-tier scale (Health / Sick / Critically Ill / Death Penalty) ===
    # Enrichment may use either the new 4-tier color tokens (`health`, `sick`,
    # `severe`, `death`) or the legacy 3-tier (`green`, `yellow`, `red`). We
    # map both to the same .traffic-* CSS classes; if the author also omits a
    # `label`, we fall back to a sensible default per tier.
    HEALTH_TIER_MAP = {
        "health": ("health", "Health"),
        "sick": ("sick", "Sick"),
        "severe": ("severe", "Critically Ill"),
        "severe-sick": ("severe", "Critically Ill"),
        "severe_sick": ("severe", "Critically Ill"),
        "death": ("death", "Death Penalty"),
        # Legacy
        "green": ("health", "Health"),
        "yellow": ("sick", "Sick"),
        "orange": ("severe", "Critically Ill"),
        "red": ("severe", "Critically Ill"),
        "black": ("death", "Death Penalty"),
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
        '<span class="traffic-light traffic-severe">Critically Ill</span>'
        '<span class="traffic-light traffic-death">Death Penalty</span>'
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
<meta name="generator" content="codebase-almanac (SKILL.md)" />
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
<div class="tropical-top-banner" aria-hidden="true">
  <div class="tropical-top-banner-wave" aria-hidden="true"></div>
  <span class="tropical-top-banner-emoji">
    🍍 🌴 🌺 🥭 🌞 🍹 🌿 🍍 🌴 🌺 🥭 🌞 🍹 🌿 🍍 🌴 🌺 🥭
  </span>
</div>
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
        <div class="hero-content">
          <div class="hero-evergreen">
            <h1 class="hero-evergreen-title">
              <span class="hero-title-main"><span>Pineapple</span> <span class="hero-title-num">48414</span></span>
              <span class="hero-title-sub">Codebase Almanac</span>
            </h1>
            <p class="hero-evergreen-body">This is a skill that streamlines the &quot;vibe-coding&quot; experience by providing a clear visual map of your codebase to assemble contexts by offering actionable insights and intelligent suggestions for product features, architectural improvements, security risks, databases, and the idea validation process.</p>
            <div class="hero-team-section">
              <h3 class="hero-team-subtitle">About Pineapple Team</h3>
              <p class="hero-team-intro">In the coming era of AGI, building solutions becomes a collective process akin to a pineapple, where technical and non-technical contributors fuse like individual berries into a unified, organic whole. This partnership mirrors the 8 &amp; 13 dual spirals of the Fibonacci sequence, intertwining creative human intent with AI-driven structural analysis to assemble a perfect, high-resolution context for building at the speed of thought.</p>
            </div>
          </div>
        </div>
        <div class="hero-art">{HERO_PINEAPPLE_SVG}</div>
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
        {health_html or '<p data-searchable>[AI_FILL: Code health check \u2014 four-tier ratings (Health / Sick / Critically Ill / Death Penalty) for organization, complexity, consistency, size]</p>'}
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
  <div class="credits-line credits-team">Designed by the <strong>Pineapple Team</strong></div>
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
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Do not open the output HTML after generation (CI / headless).",
    )
    args = parser.parse_args()

    analysis_path = Path(args.analysis).resolve()
    output_path = Path(args.output).resolve()
    enrichment_path = Path(args.enrichment).resolve() if args.enrichment else None
    generate(analysis_path, output_path, args.title, args.project_name, enrichment_path)
    size_kb = output_path.stat().st_size // 1024
    print(f"generated {output_path} ({size_kb} KB)")
    if not args.no_open:
        _open_generated_html(output_path)


if __name__ == "__main__":
    main()
