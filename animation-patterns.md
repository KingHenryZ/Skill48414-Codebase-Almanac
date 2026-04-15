# Animation Patterns

Subtle interaction patterns for code visualization output. This is a reference tool, not a presentation — animations should feel responsive and informative, never decorative or distracting.

## Philosophy

- **Functional first:** Every animation must serve a purpose (indicate state change, guide attention, show hierarchy)
- **Fast:** Max 250ms for micro-interactions, 400ms for layout changes
- **Subtle:** Prefer opacity and small transforms over large movements
- **Respectful:** All animations disabled under `prefers-reduced-motion: reduce`

---

## Interaction-to-Animation Map

| Interaction | Animation | Duration | Purpose |
| --- | --- | --- | --- |
| Tab switch | Fade in + slight upward slide | 250ms | Show new content is loaded |
| File tree expand | Height reveal (max-height transition) | 250ms | Show hierarchy opening |
| File tree collapse | Height shrink | 200ms | Show hierarchy closing |
| Card hover | Border color shift + subtle lift | 200ms | Indicate interactivity |
| Search match | Background highlight pulse | 300ms | Draw attention to match |
| Sidebar open (mobile) | Slide in from left | 250ms | Show panel appearing |
| Sidebar close (mobile) | Slide out to left | 200ms | Show panel dismissing |
| Mermaid diagram load | Fade in from 0 opacity | 400ms | Prevent layout flash |
| Badge/tag appear | Scale from 0.9 to 1 + fade | 200ms | Subtle pop-in |
| Table row hover | Background color shift | 150ms | Indicate focus row |

---

## CSS Patterns

### Tab Panel Transition

Already defined in `visualization-base.css` as `fadeIn` keyframe. Use it via the `.tab-panel.active` rule.

```css
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}

.tab-panel {
  display: none;
  animation: fadeIn 0.25s ease;
}

.tab-panel.active {
  display: block;
}
```

### File Tree Expand/Collapse

Use `max-height` transitions with a reasonable cap. Avoid `height: auto` transitions (they don't work in CSS).

```css
.tree-children {
  overflow: hidden;
  max-height: 2000px;
  transition: max-height 0.25s ease;
}

.tree-children.collapsed {
  max-height: 0 !important;
}

.tree-toggle {
  transition: transform 0.2s ease;
}

.tree-toggle.open {
  transform: rotate(90deg);
}
```

### Card Hover

```css
.card {
  transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}

.card:hover {
  border-color: var(--border-active);
  transform: translateY(-1px);
  box-shadow: var(--shadow), 0 4px 12px rgba(0, 0, 0, 0.08);
}
```

**Important:** The `translateY(-1px)` is tiny and intentional. Do not increase it — this is a data tool, not a marketing page.

### Search Highlight Pulse

```css
@keyframes highlightPulse {
  0% { background: var(--accent-primary); }
  70% { background: var(--accent-primary); }
  100% { background: transparent; }
}

.search-highlight-flash {
  animation: highlightPulse 0.3s ease forwards;
}
```

Use this class temporarily when a search match first appears. Remove it after the animation completes.

### Diagram Fade-In

```css
.diagram-container .mermaid svg {
  animation: fadeIn 0.4s ease;
}
```

### Sidebar Slide (Mobile)

```css
.sidebar {
  transition: transform 0.25s ease;
}

/* Default state on mobile: hidden */
@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);
  }

  .sidebar.open {
    transform: translateX(0);
    box-shadow: 4px 0 20px rgba(0, 0, 0, 0.2);
  }
}
```

### Staggered Card Entrance

When a tab panel first becomes visible, cards can stagger in:

```css
.card-grid .card {
  opacity: 0;
  transform: translateY(8px);
  animation: fadeIn 0.25s ease forwards;
}

.card-grid .card:nth-child(1) { animation-delay: 0ms; }
.card-grid .card:nth-child(2) { animation-delay: 40ms; }
.card-grid .card:nth-child(3) { animation-delay: 80ms; }
.card-grid .card:nth-child(4) { animation-delay: 120ms; }
.card-grid .card:nth-child(5) { animation-delay: 160ms; }
.card-grid .card:nth-child(6) { animation-delay: 200ms; }
```

**Cap at 6 items.** Beyond that, render them all at once — nobody notices stagger after 200ms.

---

## JavaScript Patterns

### Click-Outside-to-Close (Sidebar)

```javascript
document.addEventListener("click", (e) => {
  const sidebar = document.getElementById("sidebar");
  const toggle = document.querySelector(".sidebar-toggle");

  if (window.innerWidth <= 768 &&
      sidebar.classList.contains("open") &&
      !sidebar.contains(e.target) &&
      !toggle.contains(e.target)) {
    sidebar.classList.remove("open");
  }
});
```

### Smooth Scroll to Element

When clicking a file in the sidebar tree, scroll to its entry in the symbol catalog:

```javascript
function scrollToSymbol(filePath) {
  const row = document.querySelector(`[data-file="${filePath}"]`);
  if (row) {
    switchTab("technical");
    row.scrollIntoView({ behavior: "smooth", block: "center" });
    row.classList.add("search-highlight-flash");
    setTimeout(() => row.classList.remove("search-highlight-flash"), 300);
  }
}
```

---

## What NOT to Do

- **No parallax** — this is a data tool
- **No bounce effects** — feels unserious
- **No loading spinners** — the HTML is static, nothing is loading
- **No confetti or particle effects** — save those for presentations
- **No hover-triggered tooltips that move** — tooltips should fade in, not slide
- **No animation longer than 400ms** — if it takes longer, it's blocking interaction
- **No transform: scale() on hover for cards** — scale looks wrong on rectangular data cards; use `translateY(-1px)` instead
