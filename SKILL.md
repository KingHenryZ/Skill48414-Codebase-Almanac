---
name: code-visualizer
description: Generate interactive HTML visualizations of any codebase. Use when the user wants to understand a project's architecture, visualize dependencies, audit security, or create a navigable code map. Works with any language — JS/TS, Python, Go, Rust, Java, and more.
---

# Code Visualizer

Generate a single interactive HTML file that visualizes a codebase from product and technical perspectives.

## Core Principles

1. **Hybrid Analysis** — A script extracts structure; the AI enriches with product and security insights.
2. **Single HTML Output** — One self-contained file with inline CSS/JS. Mermaid.js via CDN is the only external dependency.
3. **Dual Perspective** — Product view (features, workflows, API surface) and Technical view (modules, dependencies, security).
4. **Language Agnostic** — Works on JS/TS, Python, Go, Rust, Java, and mixed-language projects.

## Non-Negotiable Rules

- Output MUST be a single `.html` file (plus Mermaid CDN)
- Every visualization MUST include the full contents of `visualization-base.css`
- All diagrams use Mermaid.js syntax rendered client-side
- CSS variables for theming — never hardcoded colors in component styles
- Responsive down to 768px width
- `prefers-reduced-motion` support on all animations
- Print-friendly mode via `@media print`

---

## Phase 0: Detect Mode

Determine what the user wants:

- **Mode A: New Analysis** — User points to a codebase directory. Go to Phase 1.
- **Mode B: Demo** — User wants to try it out. Use the built-in `example/` directory. Go to Phase 1.
- **Mode C: Enhancement** — User has an existing visualization HTML and wants to improve it. Read it, understand its current state, then enhance.

### Mode C: Enhancement Rules

When enhancing an existing visualization:

1. **Read the existing HTML first** — understand what tabs, diagrams, and data are already present
2. **Do not regenerate from scratch** — modify the existing file
3. **Preserve the user's theme choice** — do not change CSS variables unless asked
4. **After any modification:** verify all tabs still render, Mermaid diagrams still parse, and search still works

---

## Phase 1: Codebase Extraction

Run the extraction script to produce structured JSON:

```bash
python scripts/extract-codebase.py <target_dir> <output_dir>
```

If Python is not available, install it first. The script has zero dependencies — standard library only.

The script outputs `codebase-analysis.json` containing:
- **File tree** — nested directory structure with types, sizes, line counts
- **Dependency graph** — import/export edges between modules
- **Symbol catalog** — functions, classes, interfaces, types with file locations
- **Package metadata** — from package.json, requirements.txt, go.mod, Cargo.toml, etc.
- **Framework detection** — React, Express, Django, FastAPI, etc.
- **Metrics** — file count, total LOC, language breakdown

**Present the extraction summary to the user** before proceeding:
- File count, line count, detected languages
- Detected frameworks
- Number of symbols found
- Ask: "Does this look right? Should I exclude any directories?"

---

## Phase 2: Perspective Selection + Style Discovery

**Ask ALL questions in a single batch** so the user fills everything out at once:

**Question 1 — Perspectives** (header: "Perspectives"):
Which views do you want? Options:
- "Both (recommended)" — Product + Technical perspectives
- "Product only" — Features, workflows, API surface
- "Technical only" — Modules, dependencies, security

**Question 2 — Detail Level** (header: "Detail"):
How detailed should the visualization be? Options:
- "Overview" — High-level architecture, key metrics, main diagrams
- "Detailed" — Full module graph, all symbols, security audit
- "Comprehensive" — Everything, including per-file analysis

**Question 3 — Style** (header: "Style"):
How do you want to choose the visual theme? Options:
- "Show me options" (recommended) — Generate 3 previews
- "I know what I want" — Pick from preset list

### Step 2.1: Style Discovery (if "Show me options")

Read [STYLE_PRESETS.md](STYLE_PRESETS.md) for available themes.

Generate 3 single-page HTML previews under `.code-visualizer/previews/` (style-a.html, style-b.html, style-c.html). Each preview should show:
- The project name and a summary card
- A sample Mermaid diagram
- A sample file tree section
- The color palette and typography in action

Open each preview for the user automatically.

Ask (header: "Theme"):
Which style do you prefer? Options: Style A: [Name] / Style B: [Name] / Style C: [Name] / Mix elements

### Step 2.2: Direct Selection (if "I know what I want")

Show the available presets from [STYLE_PRESETS.md](STYLE_PRESETS.md) and let the user pick.

---

## Phase 3: AI Enrichment

The extraction script provides structure. Now the agent reads key files to add semantic understanding.

### Step 3.1: Deep Read

Read these files from the codebase (identified by the extraction JSON):
- **Entry points** — server.js, main.py, index.ts, etc.
- **Route/API definitions** — route files, controller files, API handlers
- **Configuration** — .env.example, config files, middleware setup
- **Models/Schema** — database models, type definitions, interfaces
- **Security-relevant** — auth middleware, validation, sanitization utilities

### Step 3.2: Product Enrichment

From the deep read, produce:
- **Feature map** — what the application does, grouped by domain
- **API surface** — routes/endpoints with methods, parameters, descriptions
- **Workflow descriptions** — how data flows through the system (request lifecycle, processing pipelines)
- **User-facing capabilities** — what an end-user or API consumer can do

### Step 3.3: Technical Enrichment

From the deep read, produce:
- **Architecture pattern** — MVC, microservices, serverless, monolith, etc.
- **Data flow** — how data moves from input to storage to output
- **Key design decisions** — patterns, trade-offs visible in the code
- **Security findings** organized by severity:
  - **High:** Hardcoded secrets, SQL injection vectors, missing authentication
  - **Medium:** Missing input validation, overly permissive CORS, no rate limiting
  - **Low:** Missing security headers, no request size limits, verbose error messages in production

---

## Phase 4: HTML Generation

Generate the full visualization HTML. **Before generating, read these supporting files:**

- [html-template.md](html-template.md) — HTML skeleton and JS contracts
- [visualization-base.css](visualization-base.css) — Mandatory CSS (include in full)
- [animation-patterns.md](animation-patterns.md) — Interaction patterns

### Output Structure

The HTML must contain these navigable sections:

**Tab: Overview**
- Project name, description, tech stack badges
- Language breakdown bar chart (CSS-only, no JS charting library)
- Key metrics cards: files, LOC, dependencies, symbols
- Detected frameworks with icons

**Tab: Product** (if selected)
- Feature cards grouped by domain
- Mermaid flowchart: request/data workflow
- API route table (method, path, description, controller)
- Entry points list

**Tab: Technical** (if selected)
- Mermaid graph: module dependency diagram
- Collapsible file tree with language icons
- Symbol catalog: searchable table of functions, classes, types
- Architecture diagram (Mermaid)

**Tab: Security** (if selected with Technical)
- Risk summary: high/medium/low count cards
- Findings list with severity badge, description, file location, recommendation
- Security checklist (what's present vs. missing)

**Sidebar:**
- Collapsible file tree (mirrors the codebase structure)
- Click a file to highlight it in diagrams and scroll to its symbols

**Navigation:**
- Tab bar at top
- Search/filter bar that searches across all tabs
- Breadcrumb showing current context
- Keyboard shortcuts: 1-4 for tabs, / for search, Esc to clear

### Key Requirements

- Single self-contained HTML file
- Include the FULL contents of `visualization-base.css` in the `<style>` block
- Mermaid.js loaded via: `<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>`
- Use fonts from Google Fonts — never system fonts alone
- CSS variables defined in `:root` for full theme customization
- All Mermaid diagram code embedded as `<pre class="mermaid">` blocks
- Add `<!-- === SECTION NAME === -->` comment blocks for every major section
- Detailed comments explaining non-obvious logic

---

## Phase 5: Delivery

1. **Clean up** — Delete `.code-visualizer/previews/` if it exists
2. **Open** — Use `open [filename].html` to launch in browser
3. **Summarize** — Tell the user:
   - File location, file size, visualization scope
   - Navigation: Tab bar, sidebar file tree, search (/ key), keyboard shortcuts 1-4
   - How to customize: `:root` CSS variables for colors, font link for typography
   - How to regenerate: re-run the skill with different options

---

## Phase 6: Share & Export (Optional)

After delivery, ask: _"Would you like to share this visualization? I can deploy it to a live URL or export it as a PDF."_

Options:
- **Deploy to URL** — Shareable link via Vercel
- **Export to PDF** — Static snapshot for documentation
- **Both**
- **No thanks**

### 6A: Deploy to Vercel

Run `bash scripts/deploy.sh <path-to-html>`. See the script for full Vercel setup and login guidance.

### 6B: Export to PDF

Run `bash scripts/export-pdf.sh <path-to-html> [output.pdf]`. The script screenshots each tab view and combines into a PDF.

**Note for PDF export:** The visualization uses tabs, so the export script captures each tab's content as a separate page. Mermaid diagrams render as SVG and are captured correctly. Interactive features (search, tree expand) are not preserved.

---

## Supporting Files

| File | Purpose | When to Read |
| --- | --- | --- |
| [STYLE_PRESETS.md](STYLE_PRESETS.md) | Visual themes with CSS variables, fonts, and diagram config | Phase 2 (style selection) |
| [visualization-base.css](visualization-base.css) | Mandatory responsive CSS — include in every output | Phase 4 (generation) |
| [html-template.md](html-template.md) | HTML skeleton, JS contracts, accessibility requirements | Phase 4 (generation) |
| [animation-patterns.md](animation-patterns.md) | Subtle interaction patterns for tree, tabs, cards | Phase 4 (generation) |
| [scripts/extract-codebase.py](scripts/extract-codebase.py) | Python script for codebase structure extraction | Phase 1 (extraction) |
| [scripts/deploy.sh](scripts/deploy.sh) | Deploy visualization to Vercel | Phase 6 (sharing) |
| [scripts/export-pdf.sh](scripts/export-pdf.sh) | Export visualization to PDF | Phase 6 (sharing) |
