# Style Presets

Six curated themes for code visualization output. Each defines CSS variables, fonts, Mermaid theme, and a signature aesthetic.

When generating style previews in Phase 2, use these exact CSS variable names and values. The visualization-base.css expects these variables to exist in `:root`.

---

## Dark Themes

### 1. Blueprint Dark

An engineering-focused theme inspired by technical blueprints and schematics.

**Feeling:** Precise, technical, authoritative

**Fonts:**
- Headings: `JetBrains Mono` (weight 700)
- Body: `IBM Plex Sans` (weight 400, 500)
- Code: `JetBrains Mono` (weight 400)
- Google Fonts import: `https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;700&display=swap`

**CSS Variables:**
```css
:root {
  --bg-primary: #0a1628;
  --bg-secondary: #111d33;
  --bg-surface: #162036;
  --bg-hover: #1c2a45;
  --text-primary: #c8d6e5;
  --text-secondary: #8395a7;
  --text-muted: #576574;
  --accent-primary: #54a0ff;
  --accent-secondary: #48dbfb;
  --accent-tertiary: #ff6b6b;
  --border-color: #1e3050;
  --border-active: #54a0ff;
  --severity-high: #ff6b6b;
  --severity-medium: #feca57;
  --severity-low: #48dbfb;
  --success: #1dd1a1;
  --shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  --radius: 6px;
  --font-heading: "JetBrains Mono", monospace;
  --font-body: "IBM Plex Sans", sans-serif;
  --font-code: "JetBrains Mono", monospace;
}
```

**Mermaid Theme:**
```javascript
mermaid.initialize({
  theme: "dark",
  themeVariables: {
    primaryColor: "#162036",
    primaryTextColor: "#c8d6e5",
    primaryBorderColor: "#54a0ff",
    lineColor: "#54a0ff",
    secondaryColor: "#1c2a45",
    tertiaryColor: "#111d33",
    edgeLabelBackground: "#111d33",
    fontSize: "14px",
  }
});
```

**Signature Elements:**
- Grid overlay on the background (subtle CSS grid pattern)
- Monospace headings give it a schematic feel
- Sharp 6px radius everywhere — no soft rounding

---

### 2. Obsidian Graph

Inspired by knowledge-graph tools and dark IDE themes. Nodes and connections are the visual metaphor.

**Feeling:** Connected, explorable, deep

**Fonts:**
- Headings: `Space Grotesk` (weight 600, 700)
- Body: `Inter` (weight 400, 500)
- Code: `Fira Code` (weight 400)
- Google Fonts import: `https://fonts.googleapis.com/css2?family=Fira+Code:wght@400&family=Inter:wght@400;500&family=Space+Grotesk:wght@600;700&display=swap`

**CSS Variables:**
```css
:root {
  --bg-primary: #1a1a2e;
  --bg-secondary: #16213e;
  --bg-surface: #1f2b47;
  --bg-hover: #263554;
  --text-primary: #e0e0e0;
  --text-secondary: #a0a0b8;
  --text-muted: #6c6c85;
  --accent-primary: #a855f7;
  --accent-secondary: #6366f1;
  --accent-tertiary: #f59e0b;
  --border-color: #2a2a4a;
  --border-active: #a855f7;
  --severity-high: #ef4444;
  --severity-medium: #f59e0b;
  --severity-low: #6366f1;
  --success: #22c55e;
  --shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
  --radius: 8px;
  --font-heading: "Space Grotesk", sans-serif;
  --font-body: "Inter", sans-serif;
  --font-code: "Fira Code", monospace;
}
```

**Mermaid Theme:**
```javascript
mermaid.initialize({
  theme: "dark",
  themeVariables: {
    primaryColor: "#1f2b47",
    primaryTextColor: "#e0e0e0",
    primaryBorderColor: "#a855f7",
    lineColor: "#6366f1",
    secondaryColor: "#263554",
    tertiaryColor: "#16213e",
    edgeLabelBackground: "#16213e",
    fontSize: "14px",
  }
});
```

**Signature Elements:**
- Glow effect on active elements (`box-shadow` with accent color at low opacity)
- Node-like cards with circular connection indicators
- Softer 8px radius for a graph-node feel

---

### 3. Neon Terminal

A cyberpunk-inspired terminal aesthetic. For developers who live in the command line.

**Feeling:** Hacker, futuristic, high-contrast

**Fonts:**
- Headings: `Orbitron` (weight 600, 700)
- Body: `Source Code Pro` (weight 400, 500)
- Code: `Source Code Pro` (weight 400)
- Google Fonts import: `https://fonts.googleapis.com/css2?family=Orbitron:wght@600;700&family=Source+Code+Pro:wght@400;500&display=swap`

**CSS Variables:**
```css
:root {
  --bg-primary: #0d0d0d;
  --bg-secondary: #141414;
  --bg-surface: #1a1a1a;
  --bg-hover: #242424;
  --text-primary: #00ff88;
  --text-secondary: #00cc6a;
  --text-muted: #336644;
  --accent-primary: #00ff88;
  --accent-secondary: #ff0055;
  --accent-tertiary: #ffcc00;
  --border-color: #1a3328;
  --border-active: #00ff88;
  --severity-high: #ff0055;
  --severity-medium: #ffcc00;
  --severity-low: #00aaff;
  --success: #00ff88;
  --shadow: 0 0 12px rgba(0, 255, 136, 0.15);
  --radius: 2px;
  --font-heading: "Orbitron", sans-serif;
  --font-body: "Source Code Pro", monospace;
  --font-code: "Source Code Pro", monospace;
}
```

**Mermaid Theme:**
```javascript
mermaid.initialize({
  theme: "dark",
  themeVariables: {
    primaryColor: "#1a1a1a",
    primaryTextColor: "#00ff88",
    primaryBorderColor: "#00ff88",
    lineColor: "#00ff88",
    secondaryColor: "#242424",
    tertiaryColor: "#141414",
    edgeLabelBackground: "#141414",
    fontSize: "13px",
  }
});
```

**Signature Elements:**
- Scanline overlay effect on the background (CSS repeating gradient)
- Neon glow on borders and headings (`text-shadow` with accent color)
- Razor-sharp 2px radius — almost no rounding
- All-monospace typography

---

## Light Themes

### 4. Paper White

A clean, documentation-inspired theme. Feels like reading well-typeset technical docs.

**Feeling:** Clear, professional, readable

**Fonts:**
- Headings: `Fraunces` (weight 600, 700)
- Body: `Literata` (weight 400, 500)
- Code: `JetBrains Mono` (weight 400)
- Google Fonts import: `https://fonts.googleapis.com/css2?family=Fraunces:wght@600;700&family=JetBrains+Mono:wght@400&family=Literata:wght@400;500&display=swap`

**CSS Variables:**
```css
:root {
  --bg-primary: #fafaf8;
  --bg-secondary: #f0efe8;
  --bg-surface: #ffffff;
  --bg-hover: #eeedea;
  --text-primary: #1a1a1a;
  --text-secondary: #555555;
  --text-muted: #999999;
  --accent-primary: #c0392b;
  --accent-secondary: #2c3e50;
  --accent-tertiary: #27ae60;
  --border-color: #ddd8cc;
  --border-active: #c0392b;
  --severity-high: #c0392b;
  --severity-medium: #e67e22;
  --severity-low: #2980b9;
  --success: #27ae60;
  --shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  --radius: 4px;
  --font-heading: "Fraunces", serif;
  --font-body: "Literata", serif;
  --font-code: "JetBrains Mono", monospace;
}
```

**Mermaid Theme:**
```javascript
mermaid.initialize({
  theme: "default",
  themeVariables: {
    primaryColor: "#ffffff",
    primaryTextColor: "#1a1a1a",
    primaryBorderColor: "#c0392b",
    lineColor: "#2c3e50",
    secondaryColor: "#f0efe8",
    tertiaryColor: "#fafaf8",
    edgeLabelBackground: "#fafaf8",
    fontSize: "14px",
  }
});
```

**Signature Elements:**
- Serif typography gives it a book/documentation quality
- Subtle warm tint to the background (not pure white)
- Red accent for primary actions — editorial feel
- 4px radius — understated and classic

---

### 5. Arctic Light

A cool, minimal Scandinavian-inspired theme. Ice blue accents on crisp white.

**Feeling:** Clean, minimal, focused

**Fonts:**
- Headings: `DM Sans` (weight 600, 700)
- Body: `DM Sans` (weight 400, 500)
- Code: `DM Mono` (weight 400)
- Google Fonts import: `https://fonts.googleapis.com/css2?family=DM+Mono:wght@400&family=DM+Sans:wght@400;500;600;700&display=swap`

**CSS Variables:**
```css
:root {
  --bg-primary: #f8fafc;
  --bg-secondary: #eef2f7;
  --bg-surface: #ffffff;
  --bg-hover: #e8edf4;
  --text-primary: #0f172a;
  --text-secondary: #475569;
  --text-muted: #94a3b8;
  --accent-primary: #0284c7;
  --accent-secondary: #0ea5e9;
  --accent-tertiary: #f97316;
  --border-color: #e2e8f0;
  --border-active: #0284c7;
  --severity-high: #dc2626;
  --severity-medium: #f97316;
  --severity-low: #0ea5e9;
  --success: #16a34a;
  --shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  --radius: 8px;
  --font-heading: "DM Sans", sans-serif;
  --font-body: "DM Sans", sans-serif;
  --font-code: "DM Mono", monospace;
}
```

**Mermaid Theme:**
```javascript
mermaid.initialize({
  theme: "default",
  themeVariables: {
    primaryColor: "#ffffff",
    primaryTextColor: "#0f172a",
    primaryBorderColor: "#0284c7",
    lineColor: "#0284c7",
    secondaryColor: "#eef2f7",
    tertiaryColor: "#f8fafc",
    edgeLabelBackground: "#f8fafc",
    fontSize: "14px",
  }
});
```

**Signature Elements:**
- Single font family (DM Sans) for visual unity
- Cool blue tones throughout — no warm colors except severity indicators
- Generous whitespace, airy layout
- Soft 8px radius — friendly but professional

---

### 6. Warm Slate

A balanced dark-light theme with warm gray tones. Easy on the eyes for long reading sessions.

**Feeling:** Balanced, comfortable, trustworthy

**Fonts:**
- Headings: `Outfit` (weight 600, 700)
- Body: `Outfit` (weight 400, 500)
- Code: `Cascadia Code` (weight 400) — falls back to Fira Code
- Google Fonts import: `https://fonts.googleapis.com/css2?family=Fira+Code:wght@400&family=Outfit:wght@400;500;600;700&display=swap`

**CSS Variables:**
```css
:root {
  --bg-primary: #f5f0eb;
  --bg-secondary: #ece5dc;
  --bg-surface: #faf7f3;
  --bg-hover: #e6dfd6;
  --text-primary: #2d2a26;
  --text-secondary: #5c5650;
  --text-muted: #9c9490;
  --accent-primary: #d97706;
  --accent-secondary: #4a7c59;
  --accent-tertiary: #9333ea;
  --border-color: #d6cfc6;
  --border-active: #d97706;
  --severity-high: #dc2626;
  --severity-medium: #d97706;
  --severity-low: #4a7c59;
  --success: #4a7c59;
  --shadow: 0 2px 6px rgba(45, 42, 38, 0.08);
  --radius: 10px;
  --font-heading: "Outfit", sans-serif;
  --font-body: "Outfit", sans-serif;
  --font-code: "Fira Code", monospace;
}
```

**Mermaid Theme:**
```javascript
mermaid.initialize({
  theme: "default",
  themeVariables: {
    primaryColor: "#faf7f3",
    primaryTextColor: "#2d2a26",
    primaryBorderColor: "#d97706",
    lineColor: "#5c5650",
    secondaryColor: "#ece5dc",
    tertiaryColor: "#f5f0eb",
    edgeLabelBackground: "#f5f0eb",
    fontSize: "14px",
  }
});
```

**Signature Elements:**
- Warm gray palette — feels cozy, not clinical
- Amber primary accent with green secondary — earthy and natural
- Generous 10px radius — soft and approachable
- Single font family (Outfit) for streamlined feel

---

## Font Pairing Summary

| Preset | Headings | Body | Code |
| --- | --- | --- | --- |
| Blueprint Dark | JetBrains Mono | IBM Plex Sans | JetBrains Mono |
| Obsidian Graph | Space Grotesk | Inter | Fira Code |
| Neon Terminal | Orbitron | Source Code Pro | Source Code Pro |
| Paper White | Fraunces | Literata | JetBrains Mono |
| Arctic Light | DM Sans | DM Sans | DM Mono |
| Warm Slate | Outfit | Outfit | Fira Code |

## DO NOT USE

These are overused in AI-generated output and make visualizations look generic:

- **Fonts:** Arial, Helvetica, Roboto as the sole typeface, system-ui alone
- **Colors:** Purple-gradient-on-white, teal-and-coral combos, rainbow gradients
- **Patterns:** Gratuitous glassmorphism, excessive gradients, drop shadows everywhere

## CSS Variable Contract

Every preset MUST define all of these variables in `:root`. The `visualization-base.css` and `html-template.md` reference them:

```
--bg-primary, --bg-secondary, --bg-surface, --bg-hover
--text-primary, --text-secondary, --text-muted
--accent-primary, --accent-secondary, --accent-tertiary
--border-color, --border-active
--severity-high, --severity-medium, --severity-low
--success, --shadow, --radius
--font-heading, --font-body, --font-code
```
