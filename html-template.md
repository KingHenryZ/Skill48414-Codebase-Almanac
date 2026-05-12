# HTML Template Specification

This document defines the HTML skeleton, JavaScript contracts, and accessibility requirements for every code visualization output.

## HTML Skeleton

Every generated visualization must follow this structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Project Name] — Code Visualization</title>

  <!-- Google Fonts (from chosen preset) -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="[FONT_URL]" rel="stylesheet">

  <!-- Mermaid.js for diagrams -->
  <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>

  <style>
    /* === THEME VARIABLES === */
    :root {
      /* All CSS variables from chosen STYLE_PRESET */
    }

    /* === VISUALIZATION BASE CSS === */
    /* Paste the FULL contents of visualization-base.css here */

    /* === THEME-SPECIFIC OVERRIDES === */
    /* Signature elements from the chosen preset (grid overlay, glow, etc.) */
  </style>
</head>
<body>

  <!-- Sidebar toggle (mobile) -->
  <button class="sidebar-toggle" onclick="toggleSidebar()" aria-label="Toggle sidebar">&#9776;</button>

  <div class="app-layout">

    <!-- === SIDEBAR === -->
    <aside class="sidebar" id="sidebar">
      <div class="sidebar-header">
        <span>[PROJECT_ICON]</span>
        <span>[Project Name]</span>
      </div>
      <div class="sidebar-content">
        <div class="file-tree" id="fileTree">
          <!-- Generated file tree HTML -->
        </div>
      </div>
    </aside>

    <!-- === MAIN CONTENT === -->
    <main class="main-content">

      <!-- === TOP BAR === -->
      <div class="top-bar">
        <div class="tab-bar" role="tablist">
          <button class="tab-btn active" role="tab" data-tab="overview" onclick="switchTab('overview')">
            Overview
          </button>
          <button class="tab-btn" role="tab" data-tab="product" onclick="switchTab('product')">
            Product
          </button>
          <button class="tab-btn" role="tab" data-tab="technical" onclick="switchTab('technical')">
            Technical
          </button>
          <button class="tab-btn" role="tab" data-tab="security" onclick="switchTab('security')">
            Security
          </button>
        </div>
        <!-- NOTE: No search input. By design — tabs and the file tree are the only navigation surfaces. -->
      </div>

      <!-- === BREADCRUMB (Overview tab only) === -->
      <!-- The Overview tab keeps a static breadcrumb so the project name stays anchored. -->
      <!-- Every OTHER tab replaces the breadcrumb with an in-panel `.panel-header` -->
      <!-- containing the Developer View / General View toggle (see PRODUCT tab below). -->
      <div class="breadcrumb" id="breadcrumb">
        <span>[Project Name]</span>
        <span class="breadcrumb-sep">/</span>
        <span>Overview</span>
      </div>

      <!-- === TAB: OVERVIEW === -->
      <div class="tab-panel active" id="panel-overview" role="tabpanel">
        <!-- Project summary, metrics cards, language breakdown -->
      </div>

      <!-- === TAB: PRODUCT === -->
      <div class="tab-panel" id="panel-product" role="tabpanel">
        <!-- Per-tab mode toggle replaces the breadcrumb on non-Overview tabs.
             Required on EVERY non-Overview tab. Both buttons must use
             data-mode="dev" / data-mode="easy" so setMode() can sync all
             toggle instances at once. -->
        <div class="panel-header">
          <div class="mode-toggle" role="group" aria-label="Audience view">
            <button data-mode="dev" class="active" onclick="setMode('dev')">Developer View</button>
            <button data-mode="easy" onclick="setMode('easy')">General View</button>
          </div>
        </div>
        <!-- Feature cards, workflow diagrams, API surface -->
      </div>

      <!-- === TAB: TECHNICAL === -->
      <div class="tab-panel" id="panel-technical" role="tabpanel">
        <!-- Same .panel-header / .mode-toggle block as Product tab. -->
        <!-- Dependency graph, file tree explorer, symbol catalog -->
      </div>

      <!-- === TAB: SECURITY === -->
      <div class="tab-panel" id="panel-security" role="tabpanel">
        <!-- Same .panel-header / .mode-toggle block as Product tab. -->
        <!-- Risk summary, findings, recommendations -->
      </div>

    </main>
  </div>

  <script>
    /* === MERMAID INIT === */
    /* === TAB SWITCHING === */
    /* === FILE TREE INTERACTION === */
    /* === SIDEBAR TOGGLE === */
    /* === KEYBOARD SHORTCUTS === */
    /* (No search code. Search has been removed from the contract.) */
  </script>

  <!-- Persistent bottom-left credits — required, do not remove -->
  <aside class="credits" aria-label="Credits">
    <div class="credits-line credits-team">designed by the <strong>PineApple Team</strong></div>
    <div class="credits-line"><span class="credits-handle">@HenryZou</span></div>
    <div class="credits-line"><span class="credits-handle">@JennyZhang</span></div>
    <div class="credits-line credits-year">2026</div>
  </aside>

</body>
</html>
```

## JavaScript Contracts

Every generated visualization MUST implement these functions. The names and behaviors are fixed — the visualization-base.css and HTML structure depend on them.

### 1. Mermaid Initialization

```javascript
mermaid.initialize({
  startOnLoad: true,
  theme: "[dark or default — from preset]",
  themeVariables: { /* from chosen STYLE_PRESET */ },
  securityLevel: "loose",
  flowchart: { useMaxWidth: true, htmlLabels: true, curve: "basis" },
});
```

**Rules:**
- `securityLevel: "loose"` is required for click handlers in diagrams
- `useMaxWidth: true` ensures diagrams scale to container width
- Always set `startOnLoad: true` — diagrams render on page load

### 2. Tab Switching

```javascript
function switchTab(tabId) {
  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.tab === tabId);
  });
  document.querySelectorAll(".tab-panel").forEach(panel => {
    panel.classList.toggle("active", panel.id === `panel-${tabId}`);
  });
  updateBreadcrumb(tabId);

  // Re-render Mermaid diagrams in the newly visible panel
  // (Mermaid can't measure hidden elements)
  const panel = document.getElementById(`panel-${tabId}`);
  panel.querySelectorAll(".mermaid[data-processed]").forEach(el => {
    el.removeAttribute("data-processed");
    el.innerHTML = el.getAttribute("data-original") || el.textContent;
  });
  mermaid.run();
}
```

**Rules:**
- Store original Mermaid source in `data-original` attribute on each `.mermaid` element
- After switching tabs, re-render Mermaid in the visible panel (hidden panels have zero dimensions)
- Update the breadcrumb to reflect current tab

### 3. (Search removed)

The visualization MUST NOT include a search input or any search JS. The
`data-searchable` attribute may stay on elements that previously powered
search — it is now a harmless data-attribute (used only by the
`scrollToSymbol` flash animation in the file tree).

### 4. File Tree Interaction

```javascript
function toggleTreeNode(element) {
  const children = element.nextElementSibling;
  const toggle = element.querySelector(".tree-toggle");

  if (children && children.classList.contains("tree-children")) {
    children.classList.toggle("collapsed");
    toggle?.classList.toggle("open");
  }
}
```

**Rules:**
- Directories are clickable and toggle their children
- Files are clickable and scroll to their symbol catalog entry
- Active file is highlighted with `.active` class
- Tree starts with root expanded, first-level children expanded, deeper levels collapsed

### 5. Sidebar Toggle (Mobile)

```javascript
function toggleSidebar() {
  document.getElementById("sidebar").classList.toggle("open");
}
```

**Rules:**
- Click outside sidebar closes it on mobile
- Sidebar toggle button only visible at <=768px (handled by CSS)

### 6. Keyboard Shortcuts

```javascript
document.addEventListener("keydown", (e) => {
  if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;

  switch (e.key) {
    case "1": switchTab("overview"); break;
    case "2": switchTab("product"); break;
    case "3": switchTab("technical"); break;
    case "4": switchTab("security"); break;
    // No `/` or `Escape` mapping — search has been removed by the SKILL.
  }
});
```

## Mermaid Diagram Patterns

### Module Dependency Graph (Technical Tab)

```
graph LR
  server["server.js"] --> routes["routes/tasks.js"]
  routes --> controller["controllers/taskController.js"]
  controller --> model["models/task.js"]
  server --> errorHandler["middleware/errorHandler.js"]
  server --> requestLogger["middleware/requestLogger.js"]
  routes --> validation["middleware/validation.js"]
```

**Rules:**
- Use `graph LR` (left-to-right) for dependency graphs
- Node IDs should be the relative file path (sanitized — no dots or slashes in IDs)
- Node labels should be the filename only
- Edge direction follows the import direction: A imports B means `A --> B`
- Only show internal dependencies (not node_modules / external packages)
- Group related files visually with Mermaid subgraphs when the project has clear layers

### Request/Data Flow (Product Tab)

```
flowchart TD
  Client[Client Request] --> Server[Express Server]
  Server --> Middleware[Middleware Stack]
  Middleware --> Router[Route Matching]
  Router --> Controller[Controller Logic]
  Controller --> Model[Data Model]
  Model --> Response[JSON Response]
```

**Rules:**
- Use `flowchart TD` (top-down) for data/request flows
- Keep node count under 12 — summarize complex flows
- Label edges when the connection type matters (e.g., `-->|"validates"| next`)

### Architecture Overview (Technical Tab)

```
graph TB
  subgraph presentation [Presentation Layer]
    Routes[Routes]
    Middleware[Middleware]
  end
  subgraph business [Business Layer]
    Controllers[Controllers]
    Validation[Validation]
  end
  subgraph data [Data Layer]
    Models[Models]
    Storage[Storage]
  end
  presentation --> business --> data
```

## Accessibility Requirements

1. **Semantic HTML:** Use `role="tablist"`, `role="tab"`, `role="tabpanel"` for tab navigation
2. **ARIA labels:** All interactive elements must have `aria-label` attributes
3. **Keyboard navigation:** All tabs and tree nodes must be reachable via keyboard
4. **Color contrast:** Text must meet WCAG AA contrast ratio (4.5:1 for normal text, 3:1 for large text)
5. **Focus indicators:** Visible focus ring on all interactive elements (use `outline` with accent color)
6. **Screen reader:** All icons must have `aria-hidden="true"` with adjacent text labels

## Code Quality

1. **Comment every section** with `<!-- === SECTION NAME === -->` in HTML
2. **Comment every function** in the `<script>` block with a one-line description
3. **CSS variables only** for colors — never hardcode hex values in component styles
4. **No inline styles** except for dynamically computed values (e.g., language bar widths)
5. **No external dependencies** beyond Mermaid CDN and Google Fonts
