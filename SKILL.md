---
name: codebase-almanac
description: Skill48414 — Codebase Almanac. Generate a single interactive HTML almanac of any codebase that explains, analyzes, and recommends in one navigable artifact. Use when the user wants to understand a project's architecture, visualize dependencies, audit security, or produce a stakeholder-ready code map. Works with any language — JS/TS, Python, Go, Rust, Java, and more.
---

# Skill48414: Codebase Almanac

Generate a single interactive HTML file that visualizes a codebase from product and technical perspectives.

## Core Principles

1. **Hybrid Analysis** — A script extracts structure; the AI enriches with product and security insights.
2. **Single HTML Output** — One self-contained file with inline CSS/JS. Mermaid.js via CDN is the only external dependency.
3. **Dual Perspective** — Product view (features, workflows, API surface) and Technical view (modules, dependencies, security).
4. **Language Agnostic** — Works on JS/TS, Python, Go, Rust, Java, and mixed-language projects.
5. **Educational Transparency** — Position output as an informational and educational layer for understanding AI-generated code and human-written code.
6. **Cross-Functional Communication** — Optimize collaboration across Product, Engineering, and stakeholders using shared visuals and plain-language explanations.

## Product Positioning

The skill should consistently position itself as:
- A transparency tool for codebases
- A collaboration accelerator between Product and Engineering
- A communication aid for multiple stakeholders (technical and non-technical)
- An adaptation tool for AI-generated code ("vibe code") so teams can understand before they improve
- A learning experience that delivers practical value: business framing, tech stack clarity, professional development, and rapid prototyping insights

## Non-Negotiable Rules

- **MUST NOT ask the user any setup questions.** Phase 2 has fixed defaults (Audience Mode = Both, Perspectives = Both, Detail Level = Comprehensive, Theme = Pineapple Tropical). Proceed directly from extraction to generation. Only honor an override if the user explicitly volunteers one in their prompt (e.g. "skip the technical tab"); never solicit one.
- Output MUST be a single `.html` file (plus Mermaid CDN)
- Every visualization MUST include the full contents of `visualization-base.css`
- All diagrams use Mermaid.js syntax rendered client-side and **MUST parse without "Syntax error in text"** (see the Mermaid rules in Phase 3 / Phase 4)
- CSS variables for theming — never hardcoded colors in component styles
- Responsive down to 768px width — diagram containers, finding cards, and the Overview summary grid all flow on narrow viewports without clipping
- `prefers-reduced-motion` support on all animations
- Print-friendly mode via `@media print`
- MUST include glossary tooltips for technical terms and architecture jargon
- MUST support two audience modes inside the same visualization:
  - **Developer/Programmer Mode** (deeper technical detail)
  - **General View** (plain-language simplification — formerly "Easy mode")
- MUST include simulation views so users can explore "what happens if..." scenarios for architecture, scale, and risk
- **MUST NOT include a search input.** No `Search…` box, no `/`-key shortcut, no in-page text-search UI. Tabs and the file tree are the navigation surfaces.
- **Summary prose uses `**inline emphasis**` markers.** Authors mark important words/phrases with double asterisks in the JSON; the generator renders them as highlighted keywords. Numbers (counts, sizes, time spans like `7-day`, `100×`) are auto-emphasized and need no markers.
- **All "Developer View" prose fields MUST be authored as bullet arrays** (`backend_analysis`, `frontend_analysis`, `index_analysis`, `query_patterns`, `backend_integration`, `product_architecture`). The script accepts a string for backward compatibility but new enrichment MUST use arrays. The generator renders them as the `prose-bullets` list, NOT a paragraph.
- **All "General View" prose fields MUST contain `**bold**` highlights** (`what_it_does`, `organization`, `how_built`, `main_parts`, `connections`, `what_data`, `how_talks`, `data_safety`, `is_safe`, `needs_attention`, `who_can_access`, `growth_assessment`). Plain-text General View prose is a regression — at least 3 highlight markers per paragraph.
- **All Mermaid diagrams render at NATURAL pixel size.** The generator initializes Mermaid with `useMaxWidth: false` for `flowchart`, `er`, `sequence`, and `gantt`. CSS clamps over-wide diagrams to the container with horizontal scroll, but small diagrams (dependency graph, easy-mode "main parts", ER tables) DO NOT stretch up. Themes / forks MUST keep this — otherwise small diagrams render with oversized text relative to larger ones.
- **Code Health Check uses a 4-tier scale**, not the legacy 3-tier traffic light: **Health → Sick → Severe Sick → Death** with the warm pineapple palette (leaf-green / gold / rind-orange / chili-black). Color tokens in enrichment JSON are `health` / `sick` / `severe` / `death`. Legacy `green` / `yellow` / `red` are mapped to the first three tiers but new enrichment MUST use the new tokens. The script always renders a legend strip above the items so all four tiers are visible.
- **Top tab bar must have PERFECTLY symmetric vertical padding** so the active tab pill has equal breathing room above and below. The base CSS sets a fixed height with zero vertical padding; the Pineapple theme overrides this with `padding-top/bottom: 16px`, `height: auto`, **`min-height: 0`**, and `align-items: center`. The previous `min-height: clamp(56px, 6vh, 72px)` rule was removed because flex items center inside that floor while padding stays fixed at 14px — the bottom always picked up the extra slack and rendered visibly taller than the top. Forks / themes MUST keep this `min-height: 0` invariant or the asymmetry returns.
- **Top tab bar pills are TEXT ONLY.** Each `.tab-btn` renders only the tab label (`Overview`, `Product`, …). Forks MUST NOT prepend pineapple emojis (🍍) or any other glyph before the label, neither in the markup nor via `::before` pseudo-elements. The Overview "Explore by Tab" cards carry the per-tab icons; the top nav stays clean.
- **Codebase display name is auto-derived, marketing-style.** The generator runs `display_name()` over the raw `project_name` from the analysis JSON to produce a concise, branded title (e.g. `spendwise-monorepo` → `Spendwise`, `auth-service` → `Auth`, `acme-platform-v2` → `Acme`). Trailing noise (`-monorepo`, `-mono`, `-app`, `-repo`, `-service`, `-platform`, `-frontend`, `-backend`, `-api`, `-web`, `-ui`, `-client`, `-example`, `-demo`, `-template`, `-vN`, `-N.M.K`, `.git`) is stripped, kebab/snake-case is PascalCased, npm scope prefixes are dropped, and already-CamelCased brands are preserved. The auto-built page `<title>` is `"<DisplayName> — Code Visualization"`, the **`.codebase-card`** + sidebar header use the same display name, and the analysis JSON keeps the raw slug for tooling that needs it. No author override is needed.
- **Hero (Overview tab) layout contract.** The hero has TWO regions:
  1. Top half — pineapple SVG on the right plus an evergreen left column. The left column has a single, **un-boxed** evergreen block (`.hero-evergreen`) containing the `<h1>` "Pineapple Code Cartography" title (with its `?` tooltip) and a one-paragraph evergreen tagline. There MUST NOT be a second evergreen block, dashed boxes, breadcrumbs, eyebrow text, metric chips, or stray leaf decorations next to the codebase name.
  2. Bottom half — the **`.codebase-card`** (auto-derived display name + project summary), then the **"Explore by Tab"** lede + summary card grid.
- **`.codebase-card` styling** (Pineapple theme):
  - Title: solid `var(--leaf-deep)` color (NOT a gradient-text fill — that renders nearly white on the cream card background and is unreadable). The global `h2::before` pineapple emoji and the `h2::after` connector line are explicitly suppressed for `.codebase-card-name` so no decoration leaks onto the title.
  - Description: same `var(--font-heading)` (Fraunces) as the rest of the section h2s, NO italic, weight 500, larger than body copy but smaller than the title. Inherits `**inline emphasis**` markers.
- **Overview "Explore by Tab" card layout contract.** Each card uses a header row (`.summary-link-head`) with the tab icon on the **left** and the tab name on the **right** of the same row, separated by a dashed divider, then the description below. The tab name uses the same `var(--font-heading)` display font as `.codebase-card-name` so the Overview grid feels like a curated index. Cards are keyboard-activatable (`role="link" tabindex="0"`, Enter/Space triggers click).
- **Tab switching always defaults to "Developer View".** Whenever a non-Overview tab becomes active — via the tab bar, an Overview summary-card click, or a keyboard shortcut — the JS calls `setMode('dev')` so the technical content is shown first. Switching to the Overview tab does NOT touch mode. The mode toggle in each panel-header reflects the active state (sync handled by `[data-mode]` query in `setMode`).
- **Overview summary cards behave as cross-tab navigation.** Their `onclick` calls `goToTab(tabId)` which: (a) switches to that tab, (b) resets to Developer View per the rule above, and (c) smooth-scrolls the main content area back to the top so the destination panel-header / first heading is in view.
- **Security tab visual contract.**
  - Developer View "Risk Summary" renders a `.risk-summary` grid of three `.risk-card`s with severity-tinted top bar + halo (`.risk-high` red, `.risk-medium` gold, `.risk-low` leaf-green), a glyph (🚨 / ⚠️ / 🔍), an UPPERCASE tier label, the count number rendered LARGE (`clamp(2.6rem, 4.8vw, 3.8rem)` Fraunces 900), and a sub-label. The legacy `metric-card` row is no longer used here.
  - Developer View Findings: the recommendation block is a **highlighted callout** (gold/leaf gradient, leaf-deep left border, `💡 Recommendation` label) with the body text rendered LARGER than the rest of the finding (`clamp(1.02rem, 1.25vw, 1.18rem)` weight 500). The recommendation body inherits `**bold**` markers and renders them with a yellow highlight underline.
  - Developer View "Authentication & Authorization", "Input Validation Audit", "Dependency Risk", and "Scalability Analysis" sections are authored as **bullet arrays** with `**bold**` highlights and rendered through `prose_or_bullets()`. Strings are accepted for backward compat but new enrichment MUST use arrays.
  - General View "Is the app safe?" renders the same 4-tier scale as the Code Health Check (Health / Sick / Severe Sick / Death) — same legend strip, same color tokens — but with a slightly larger pill + verdict text (`.safety-verdict`). The single yellow-light pill is no longer used.
  - General View "What needs attention?", "Who can access what?", and "Can the app handle growth?" MUST contain at least 3 `**bold**` highlight markers each.
- **Suggestions tab — "Pineapple Seasoning Score".** The legacy Small / Medium / Large effort badge is replaced by a 1–3 pineapple-emoji rating chip (`.seasoning-chip.seasoning-{1,2,3}`):
  - 🍍 **Quick Win** — small effort
  - 🍍🍍 **Medium Effort**
  - 🍍🍍🍍 **Big Bake** — large effort
  - The script accepts every legacy and new effort token: `small`/`medium`/`large`, `mild`/`spicy`, `quick-win`/`medium-effort`/`big-bake`, or numeric `1`/`2`/`3`. A `SEASONING_LEGEND_HTML` strip MUST appear ABOVE every Suggestions grid (Product / Technical / Security / Priority Matrix) so the chip vocabulary is always self-documenting.
- **Suggestions Developer-View card contract.** Cards use `.card-grid.suggestions-grid` so titles render LARGER (`clamp(1.18rem, 1.6vw, 1.42rem)` Fraunces 700) than the default. Card BODIES MUST be authored as `bullets: string[]` (with `**bold**` highlights), not paragraph descriptions. The seasoning chip lives next to the title.
- **Scalability Roadmap is a horizontal stepper**, not an ordered list. Each step is a `.roadmap-node` with a numbered medallion, a "when" pill (Now / Next / Later / Future, author can override), the step title, and an optional seasoning chip. Nodes are connected by gold arrow connectors (`::after` line + `::before` arrowhead). On viewports ≤600px the row reflows to vertical. Authors pass either a string list (auto-numbered) or `[{ title, text?, when?, effort? }]`.
- **Priority Matrix uses Pineapple Seasoning visuals.** Each row in `.priority-matrix` shows a "when" seasoning chip (`Do now` → 🍍🍍🍍, `Do soon` → 🍍🍍, `Do later` → 🍍), an optional effort chip, and the recommendation text — sharing the exact chip styling with the suggestion cards so the visual language is consistent across the Suggestions tab.
- **Suggestions General View MUST be enriched bullet content.** All five general-view fields (`product`, `code`, `security`, `growth`, `priorities`) accept a string OR a bullet array, and MUST contain `**bold**` highlights throughout. A one-line summary is no longer acceptable — each section needs at least 3–5 substantive bullets.
- **Hero pineapple SVG MUST render in full AND own ~the entire right side of the hero.** The `.hero-art` container is anchored to the right edge with very small safe gutters and a width of `clamp(420px, 56%, 760px)` so the pineapple fills roughly two-thirds of the hero box (the iconic "pineapple-as-hero" iteration). The SVG itself uses `object-fit: contain` + `object-position: right center` so the entire fruit (crown leaves + body) stays visible at every viewport — no clipping. Rotation stays tame (≤2deg) so the crown doesn't poke above the hero's `overflow: hidden` boundary. Forks that resize the pineapple MUST keep it both LARGE (≥half the hero width on desktop) and FULLY VISIBLE.
- **`.codebase-card` description MUST be in product / marketing language** — what the app DOES, who it's FOR, key features, objectives. **Strictly NO technical jargon** in this field (no framework names, no library names, no DB engines, no protocol acronyms). The technical detail belongs in the Technical / Database / Security tabs, not in the codebase intro card. The description should read like a homepage headline paragraph, not a README.
- **Sidebar header & codebase title font are unified — sidebar gets fancier display treatment.** Both the `.sidebar-header` (top of left sidebar) and the `.codebase-card-name` use **the same Fraunces (`var(--font-heading)`) display font, non-italic**, so the project name reads consistently above and below the hero. On the sidebar, the word is rendered with a gold→cream `background-clip: text` gradient on the letterforms, a subtle radial gold spotlight in the green panel backdrop, a soft drop-shadow, and a small gold accent bar (`::before`) tucked under the word — making "Spendwise" / the project name read as a brandmark, not just a heading. The legacy 🍍 / 🌿 decorations flanking the sidebar header are removed.
- **Findings recommendation body font matches the rest of the finding card** (~`0.95rem`, same as `.finding-detail`). The callout chrome (gold/leaf gradient bg, leaf-deep left border, `💡 Recommendation` label) still draws attention, but the body text no longer dominates the row.
- **Pineapple Seasoning visibility rules:**
  - The seasoning **legend strip** appears EXACTLY ONCE on the Suggestions tab — under the **Product Suggestions** heading. Never duplicate it under Technical / Security / Roadmap / Priority Matrix.
  - Seasoning chips inside cards / roadmap nodes / anywhere except the legend render the **pineapple emoji ONLY** (`.seasoning-chip.seasoning-glyph-only`). Drop the descriptive text label — it stays in the legend.
  - The **Priority Matrix** (Developer View) and **"What to do first"** (General View) are now plain bullet rows — NO Do-now / Do-soon / Do-later tag, NO seasoning chip. Just text + `**bold**` highlights, prefixed by the standard 🍍 bullet glyph.
  - The **Scalability Roadmap** does NOT render an effort chip per node. Numbered medallions sit fully INSIDE each node (no negative `top`) so the top of each circle is never clipped by the parent's `overflow-x: auto` context.
- **Pitch & Simulation tabs are single-view ("Boss View"), not dev/general split.** The script does NOT emit a real panel-mode toggle on these tabs. Each tab shows one curated audience view authored under `pitch.boss.*` / `simulation.boss.*`. The panel-header on both tabs renders **the same `.panel-header > .mode-toggle` pill chrome as the rest of the tabs**, with a single non-toggleable button labelled `Boss View` and the `.active` class. The DOM uses `<button class="active" disabled aria-pressed="true">Boss View</button>` plus a `.boss-view-toggle` modifier that strips the browser's disabled grey-out so the pill reads identical to an active Developer/General chip on other tabs. Forks MUST NOT re-introduce the legacy gold `.boss-view-badge` pill, MUST NOT re-introduce a dev/general split, and MUST NOT special-case the chip styling — only the label inside the pill differs.
- **Pitch & Simulation page backgrounds match every other tab.** The previous "fancy" page backgrounds (gold spotlight gradient + pinstripe for Pitch, leaf-tinted gradient for Simulation) and their pseudo-element halos have been removed. Custom flair lives at the SECTION level — the gold-haloed `.pitch-oneliner` callout, the leaf-bordered `.pitch-story` card, the giant rocket-watermark `.sim-takeoff-card`, the `.sim-next-grid` feature cards, and the `.big-picture-stepper` — but the panels themselves use the standard tab background. Forks MUST NOT re-add a page-level background tint to either tab.
- **Pitch one-liner is a flashy display headline, NOT highlighted body copy.** The one-liner sentence is rendered through `.pitch-oneliner-text` with the `var(--font-heading)` Fraunces display font at `clamp(1.55rem, 2.6vw, 2.35rem)`, weight 800, non-italic, and a gold→amber `background-clip: text` gradient fill plus a soft `drop-shadow` glow — the WHOLE sentence reads as the deck's hero line. The wrapping `.pitch-oneliner` card still provides the gold halo / rind border. Authors MUST author the one-liner as a single sentence in `pitch.boss.one_liner`. **`**bold**` highlight markers in `one_liner` and `story` are stripped at render time** — both sections render as plain text with NO `.kw` chips and NO auto-numeric `.num` chips, so the headline styling stays the focal point. Authors should still write good copy without `**` markers; if they leak through they'll be silently removed.
- **Pitch "Tell your story" is plain narrative prose.** Body font, non-italic, leaf-bordered card. Same rule as the one-liner: NO `.kw` highlight chips, NO `.num` chips. The story sets up *why this exists* in human language and reads as one continuous paragraph.
- **Pitch tab section list and widths.** The Pitch tab renders, in order: `The one-liner`, `Tell your story`, `Who is this for?`, `Why does this matter?`, `What makes it special?`, `Architecture Strengths`, `Tech Stack Justification`, `Integration Narrative`. The legacy **"By the Numbers"** metric-card row at the bottom of Pitch is **removed** — counts (files / LOC / symbols) belong to the Overview tab, not Pitch. Every prose / bullet block on Pitch (and Simulation) MUST span the **full content width** (`width: 100%`, `max-width: none`) — the generic `.prose-bullets { max-width: 78ch }` constraint is overridden inside `#panel-pitch` and `#panel-simulation` so the boxes extend to the right edge of the column.
- **Simulation "What if it takes off" rocket is a watermark, not a glyph.** The 🚀 inside `.sim-takeoff-card` renders as a very large (`clamp(220px, 28vw, 360px)`), low-opacity (~0.08) `::before` watermark anchored to the LEFT side of the card and rotated slightly. Card content sits on top with `position: relative; z-index: 1;`. The card's left padding stays at the same value as the right padding (`26px 28px`) so paragraphs and bullets start from the left edge and span the full width. Forks MUST NOT re-introduce extra left padding for a small corner-rocket glyph.
- **Simulation "What comes next?" cards do NOT show pineapple seasoning chips.** Effort chips (🍍 / 🍍🍍 / 🍍🍍🍍) are reserved for the Suggestions tab. The Simulation tab calls `render_cards(..., suppress_effort=True)` so even if an `effort` field leaks through `simulation.boss.whats_next_cards` (or any future enrichment), the chip is silently dropped. Authors SHOULD omit `effort` from these cards entirely; the script just guards against drift.
- **Simulation "The big picture" highlight rule.** Inside `.simulation-panel .big-picture-stepper`, `**bold**` keyword highlights render as **plain underlined text** — `font-weight: 400`, no yellow highlight bar, no `.kw` background — so the stepper reads as a quiet roadmap rather than a loud emphasized list. This override is scoped to the big-picture stepper only; everywhere else in the visualization `.kw` keeps its default gold-highlight treatment.
- **MUST include the persistent bottom-left credits block** with this exact content (rendered by the script, never hand-edited into HTML):

  > designed by the **PineApple Team**  ·  @HenryZou (LinkedIn)  ·  @JennyZheng (LinkedIn)  ·  2026

  - Each handle MUST be followed by a **LinkedIn icon button** (square, brand-blue, 18×18 px, `aria-label`-ed). Henry's button links to `https://www.linkedin.com/in/cunhanzou/`. Jenny's button links to `https://www.linkedin.com/in/jenzheny/`.
  - The credits box uses a **dark, semi-transparent background** (`rgba(33, 22, 8, 0.42)`) with backdrop-blur so the page shows through. Body text is light cream, accents are gold. Forks MUST NOT revert to an opaque cream background.

---

## Phase 0: Detect Mode

Determine what the user wants:

- **Mode A: New Analysis** — User points to a codebase directory. Go to Phase 1.
- **Mode B: Demo** — User wants to try it out. Use the built-in `example/` directory. Go to Phase 1.

### Fresh Generation Rule (mandatory, every invocation)

**Every run of this skill executes Phase 1 → 4.5 from scratch.** No caching, no resume, no partial reuse. Specifically:

1. **Re-run extraction.** Always invoke `scripts/extract-codebase.py` against the target directory and write a fresh `codebase-analysis.json`. **Never** read a pre-existing `codebase-analysis.json` — its contents may be stale (the codebase may have changed) or partial (a prior run may have crashed mid-write).
2. **Re-run enrichment.** Always perform Phase 3 in full and write a fresh `enrichment.json`. **Never** read a pre-existing `enrichment.json` to "save time" or to "fill in the gaps." Stale or partial enrichment is the most common cause of mismatched / generic-looking output.
3. **Re-run generation.** Always invoke `scripts/generate-visualization.py` to write a fresh, uniquely-named output file. **Never** patch, edit, or append to a previously generated HTML.
4. **Verify completeness.** Phase 4.5 MUST run before Phase 5. The `[AI_FILL` count in the output HTML MUST be zero. If it is not, re-author the missing enrichment keys and re-generate — do not deliver a half-filled HTML to the user.

Output filenames MUST be timestamped so prior runs are preserved for comparison and never silently overwritten:

```
.codebase-almanac/visualization-YYYYMMDD-HHMMSS.html
```

The same applies to the intermediate JSON: write each run's analysis + enrichment to `.codebase-almanac/codebase-analysis.json` and `.codebase-almanac/enrichment.json` respectively, **overwriting** the previous-run versions in place (the timestamped HTML keeps the historical artifact). At no point should the agent skip a phase because a file from a prior run already exists on disk.

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

## Phase 2: Configuration (no questions, fixed defaults)

**Do NOT ask the user any setup questions.** The skill ships with one fixed configuration. Proceed directly to Phase 3.

| Setting | Value | Notes |
| --- | --- | --- |
| Audience Mode | **Both** | Developer View loads first; the in-page toggle still lets the reader switch to General View. |
| Perspectives | **Both** | Product and Technical tabs are both generated. |
| Detail Level | **Comprehensive** | Full module graph, all symbols, per-file analysis where appropriate. |
| Visual Theme | **Pineapple Tropical** | The only theme `generate-visualization.py` supports. |

The only time these defaults bend is when the user **volunteers** an override in their prompt — e.g. "visualize this codebase but skip the security tab" or "use general view as the default." Never solicit such overrides.

---

## Phase 3: AI Enrichment

The extraction script provides structure. Now the agent reads key files to add semantic understanding. Every tab (except Overview) requires **two versions** of its prose content: one for **Developer View** (precise, technical, references file paths) and one for **General View** (plain-language, no jargon, targets non-coders). The two views are kept in the enrichment JSON under `dev` and `easy` keys respectively — the `easy` key is the historical name for the General View payload and is preserved for backward compatibility.

### Step 3.1: Deep Read

Read these files from the codebase (identified by the extraction JSON):
- **Entry points** — server.js, main.py, index.ts, etc.
- **Route/API definitions** — route files, controller files, API handlers
- **Configuration** — .env.example, config files, middleware setup
- **Models/Schema** — database models, type definitions, interfaces, migration files
- **Database layer** — ORM setup, raw SQL, connection config, seed files
- **Security-relevant** — auth middleware, validation, sanitization utilities
- **Frontend** — components, pages, state management, routing

### Step 3.2: Overview Enrichment

Produce content for the Overview tab (same for both modes):
- **Project summary** — 2-4 sentences in **product / marketing language ONLY**. This is the codebase intro card that sits below the pineapple hero, so it must read like a homepage headline paragraph: **what the app does**, **who it's for**, **what it includes** (key features, product design), and **what its objectives are**. **DO NOT use technical jargon here** — no framework names (Express, React), no library names (better-sqlite3, helmet), no protocol acronyms (JWT, JSON, REST), no infrastructure terms (monorepo, npm workspace). The technical detail belongs in the Technical / Database / Security tabs, not in the codebase intro card. Use `**bold**` markers to highlight ~3–6 product-side terms (the domain, the audience, the headline benefit).
- **Tab summaries** — for each of the other 7 tabs, write a 1-2 sentence "highlight finding" (the single most important takeaway from the actual analysis). These become clickable cards linking to each tab. **Each card description must be specific to the codebase** — never use generic text like "Explore the X analysis." Example: `**6** feature domains across **4 packages** with **19 API endpoints**` not "Explore the Product analysis." Counts/numbers are auto-emphasized; mark important nouns with `**`. **Each summary MUST contain at least 3 `**bold**` markers** so the Overview cards never read as a wall of plain text.

**Overview hero structure (batch 3 lockdown):**
- The Overview tab **does NOT** render: the project breadcrumb (`Project / Overview`), the "TROPICAL CODE CARTOGRAPHY" eyebrow, the four metric chips next to the pineapple (files / LOC / deps / symbols), or the two stray crown-leaf SVGs. Authors and downstream themes MUST NOT re-introduce them — they duplicate the metric cards immediately below and clutter the hero.
- **Left of the pineapple** is the **single evergreen block** (`.hero-evergreen`) — title (`Pineapple Code Cartography`) plus a one-paragraph tagline. It renders the SAME on every codebase. It is NOT templated against the analysis JSON. The tagline currently shipped is the AGI / Fibonacci-spirals manifesto in `scripts/generate-visualization.py`. Forks may rewrite it but MUST keep it as one paragraph and MUST NOT re-introduce a second evergreen block.
- Codebase-specific name + AI-generated `project_summary` live exclusively in the `.codebase-card` section below the hero (gradient-bordered, gold-rind glow, gradient-text title).
- The "Codebase at a Glance" duplicate paragraph above the summary cards has been replaced with a short navigation lede ("Explore by Tab") since the codebase-card now owns the summary role.
- The language bar, metrics row, codebase-card, summary-grid, and the persistent bottom-left credits block are the only chrome on the Overview tab. **No** search bar, **no** Frameworks section, **no** Navigation section.

### Step 3.3: Product Enrichment

Produce content for the Product tab in **both** Developer View and General View:

**Developer View content:**
- **Feature map** — card grid of detected feature domains. Each entry MUST be an object with a `title` and a `bullets: string[]` field (3–5 short bullets). Each bullet should call out the implementing module/file, key endpoints, or scope. A legacy `description` paragraph is still rendered as a lead-in if both are present, but new enrichment SHOULD use bullets only — paragraph-only feature cards are discouraged because the Feature Map is meant to be scannable.
- **User workflow diagrams** — Mermaid flowcharts of primary user journeys derived from route analysis and controller logic. Use technical labels (HTTP methods, endpoint paths).
- **API surface table** — every route/endpoint with columns: Method, Path, Auth Required, Description.
- **Product architecture** — how features are distributed across packages/modules; which package owns which domain. **Provide this as `product_architecture: string[]` (a bullet list).** A single string is still accepted for backward compatibility but new enrichment MUST use the array form so it renders as the polished `prose-bullets` list, not a wall of text.
- **Design patterns identified** — product patterns visible in the code (RBAC, pagination, rate limiting, input sanitization, error messaging strategy). Use the same `title` + `bullets` (or fallback `description`) card shape as the feature map.

**General View content:**
- **"What does this app do?"** — plain-language feature paragraph. **Mark 3–6 important nouns/phrases with `**double-asterisks**`** so they render as warm highlights via `emphasize()`. Numbers are auto-highlighted; do not wrap them.
- **"How do people use it?"** — simplified workflow diagrams with friendly labels (e.g., "Sign up" instead of "POST /auth/register").
- **"What can users do?"** — capability checklist with checkmarks.
- **"How is the app organized?"** — plain-language paragraph that names the main parts and their roles. **Apply the same `**bold**` highlight markers** to the package/folder names and the role each one plays (e.g., `**API package**`, `**database**`).

### Step 3.4: Technical Enrichment

Produce content for the Technical tab in **both** Developer View and General View:

**Developer View content:**
- **Architecture diagram** — Mermaid diagram of system layers annotated with actual module names.
- **Backend analysis** — **MUST be `backend_analysis: string[]`** (a bullet list, 4–8 bullets covering the middleware pipeline, route structure, controller patterns, error handling, startup side effects). Use `**bold**` markers liberally to highlight middleware names, file paths, and configuration keys. A single string is still rendered (legacy fallback) but new enrichment MUST use the array form.
- **Frontend analysis** (if applicable) — **MUST be `frontend_analysis: string[]`** (bullets covering component tree, state management, routing, build tooling, key globals). If no frontend exists, return a single-bullet array stating that explicitly. Same `**bold**` highlight rules.
- **Module dependency graph** — Mermaid graph of internal import/export relationships.
- **Symbol catalog** — searchable table: name, kind, file, exported status (generated by the script from extraction JSON).
- **Code quality signals** — `code_quality: { title, description }[]` cards. **`description` MUST contain `**bold**` highlights** for the named entities (file names, library names, sizing nouns) — the cards should NEVER render as plain text. Long card content MAY use the `bullets` field instead of `description` for the same scannable layout used in Feature Map cards.

**General View content:**
- **"How is the code built?"** — building-blocks analogy explaining the layers. **MUST contain at least 3 `**bold**` highlights** (the layer names + the analogy nouns).
- **"The main parts"** — simplified architecture diagram with plain labels. The accompanying `main_parts` paragraph MUST contain `**bold**` highlights for each named package/folder.
- **"How the parts connect"** — simplified dependency view in plain sentences. **MUST contain `**bold**` highlights** for each connection actor (e.g. `**browser**`, `**Express routes**`, `**AuthService**`).
- **"Code health check"** — **four-tier health scale** (NOT the old traffic-light trio). Each item is `{ label, description, color }` where `color` is one of `health` / `sick` / `severe` / `death`. Legacy `green` / `yellow` / `red` are still accepted and mapped (`green→health`, `yellow→sick`, `red→severe`) for backward compatibility, but new enrichment MUST use the new tokens. The `description` field MUST contain `**bold**` highlights, and the `label` is the dimension being assessed (e.g. `Organization`, `Test coverage`) — NOT a verdict suffix like `: Good`. The script renders a legend strip above the items so readers see the full scale.

### Step 3.5: Database Enrichment (conditional)

Only produce this content if the codebase has a database. Detection criteria: SQL files, ORM models, migration folders, database drivers in dependencies (e.g., `better-sqlite3`, `pg`, `mongoose`, `prisma`, `drizzle`, `sequelize`, `typeorm`). If no database is detected, set `has_database: false` and skip this step.

**Developer View content:**
- **Schema design** — ER diagram (Mermaid `erDiagram`) with tables, columns, types, relationships (FK, unique constraints).
- **Index analysis** — **MUST be `index_analysis: string[]`** (a bullet list). Each bullet names ONE index and what it covers. Use `**bold**` for index names, table.column references, and operations.
- **Query patterns** — **MUST be `query_patterns: string[]`** (bullets). Each bullet calls out a pattern (synchronous vs async, ORM vs raw, transactions, bulk ops, dynamic SQL safety).
- **Backend integration** — **MUST be `backend_integration: string[]`** (bullets). Cover connection management (pooling, WAL mode), where DB calls live (repository pattern vs inline), error handling, and any startup side effects.
- **Data flow** — Mermaid sequence diagram: request → controller → database → response.

**General View content:**
- **"What data does the app store?"** — plain-language description with **`**bold**` highlights** on every named entity (each table / data type, each notable column).
- **"How is data organized?"** — simplified ER diagram with friendly labels and plain relationship words.
- **"How does the app talk to the database?"** — simple read/write explanation. **MUST contain `**bold**` highlights** for the verbs and named actors (`**server**`, `**JSON**`, `**lists**`, `**add / update / delete**`).
- **"Is the data safe?"** — plain-language data integrity explanation. **MUST contain `**bold**` highlights** for the integrity primitives (`**foreign keys**`, `**users**`, `**categories**`, `**history**`).

### Step 3.6: Security Enrichment

Produce content for the Security tab in **both** Developer View and General View:

**Developer View content:**
- **Risk summary** — counts of High / Medium / Low severity findings. The script renders these as `.risk-card` cells (severity-tinted, big count number, glyph). Provide `high_count`, `medium_count`, `low_count` integers.
- **Detailed findings** — each finding with: `severity`, `title`, `location`, code context (`detail`), and specific remediation in **`remediation`** (optional alias **`recommendation`** — both render under the highlighted **💡 Recommendation** callout in the HTML; if both are set, `remediation` wins). The recommendation body renders LARGER than the rest of the finding and inherits `**bold**` markers, so include 1-2 highlight markers per remediation.
- **Authentication & Authorization** (`auth_analysis`) — **bullet array, with `**bold**` highlights** on JWT/session primitives, secret-management calls, token-expiry config, role-check sites.
- **Input Validation Audit** (`input_validation`) — **bullet array, with `**bold**` highlights** on validated vs unvalidated inputs and injection-risk surfaces.
- **Dependency Risk** (`dependency_risk`) — **bullet array, with `**bold**` highlights** on package names, CVEs, and risky transitive patterns.
- **Scalability Analysis** (`scalability`) — **bullet array, with `**bold**` highlights** on bottlenecks (in-memory state, single-process, no caching, no queue), horizontal vs vertical readiness, connection pooling, rate-limit capacity.

> All four developer-view sections accept a string for backward compat but new enrichment MUST use bullet arrays. The script renders them through `prose_or_bullets()` — strings become a `<p>`, lists become `<ul class="prose-bullets">`.

**General View content:**
- **"Is the app safe?"** (`is_safe` + `safety_color`) — 4-tier verdict using the SAME color tokens as the Code Health Check: `health` / `sick` / `severe` / `death`. The script emits the legend strip, the colored pill, and the verdict text. Legacy `green/yellow/red` are still mapped (yellow → sick, red → severe) but new enrichment MUST use the 4-tier tokens. The verdict text MUST contain at least 3 `**bold**` highlights.
- **"What needs attention?"** (`needs_attention`) — plain-language risk description, **MUST contain at least 3 `**bold**` highlights** on the risk topics.
- **"Who can access what?"** (`access_control`) — simplified auth explanation, **MUST contain at least 3 `**bold**` highlights**.
- **"Can the app handle growth?"** (`growth`) — plain-language scalability assessment, **MUST contain at least 3 `**bold**` highlights**.

### Step 3.7: Suggestion Enrichment

Produce content for the Suggestions tab in **both** Developer View and General View. The Suggestions tab uses the **Pineapple Seasoning Score** vocabulary across the suggestion cards and the roadmap: `effort` values are rendered as a 1-3 pineapple chip (🍍 Quick Win / 🍍🍍 Medium Effort / 🍍🍍🍍 Big Bake).

> **Batch 5 visibility rules** (must follow):
> - The **legend strip** that explains the chip levels appears **EXACTLY ONCE** on the tab — directly under the **Product Suggestions** heading. The legend MUST NOT be repeated above Technical Suggestions, Security Hardening, the Scalability Roadmap, or the Priority Matrix.
> - Inside cards / roadmap nodes / anywhere else the chip appears, render the **pineapple emojis ONLY** (🍍 / 🍍🍍 / 🍍🍍🍍). Drop the descriptive text label ("Quick Win" / "Medium Effort" / "Big Bake") — it stays in the legend, not on the chip itself. Hovering surfaces the label via the chip's `title` attribute.
> - The **Priority Matrix** (Developer View) and **"What to do first"** (General View) are now plain bullet rows — **NO** "Do now / Do soon / Do later" tag, **NO** seasoning chip. Just the recommendation text with `**bold**` highlights, prefixed by the standard 🍍 bullet glyph.
> - The **Scalability Roadmap** stepper renders the medallion + when-pill + title + text. It does **NOT** render an effort/seasoning chip per node (kept simple and readable).

**Developer View content:**
- **Product suggestions** (`product`) — feature gaps, missing UX flows, inconsistent API patterns, missing error states. Each item is a dict with: `title`, `bullets: string[]` (3-6 substantive bullets, **with `**bold**` highlights**), optional `location` (file path), and `effort` (any of `small`/`medium`/`large`, `quick-win`/`medium-effort`/`big-bake`, `mild`/`spicy`, or `1`/`2`/`3`). Card titles render LARGER on this tab — keep them concise and noun-first.
- **Technical suggestions** (`technical`) — refactoring, architecture improvements, performance optimizations, test coverage gaps, missing strictness. Same `{title, bullets, location?, effort}` shape as above.
- **Security hardening** (`security`) — specific fixes with file paths and code-level guidance. Same shape.
- **Scalability roadmap** (`scalability_roadmap`) — ordered steps rendered as a horizontal stepper (`.scalability-roadmap` UI). Items can be plain strings (auto-numbered, `when` defaults to Now/Next/Later/Future by index) or dicts: `{ title, text?, when? }` (no `effort` chip per node — see batch 5 rules above). Always provide AT LEAST 3 nodes and PREFER 4–5. Numbered medallions sit FULLY INSIDE each node so the top of the circle is never clipped.
- **Priority matrix** (`priority_matrix`) — `[ { text, label?, effort? } ]`. Only `text` is rendered visually (label/effort kept for backward compat). Each row appears as a styled bullet with `**bold**` highlights.

**General View content (each field accepts a string OR a bullet array, must be ENRICHED):**
- **"How to make the product better"** (`product`) — plain-language improvement ideas, ≥4 bullets, **with `**bold**` highlights**.
- **"How to make the code stronger"** (`code`) — simplified technical suggestions, ≥4 bullets, **with `**bold**` highlights**.
- **"How to make it safer"** (`security`) — non-jargon security improvements, ≥4 bullets, **with `**bold**` highlights**.
- **"How to handle more users"** (`growth`) — growth readiness in plain language, ≥4 bullets, **with `**bold**` highlights**.
- **"What to do first"** (`priorities`) — `[ { text } ]` (or `[ { label, text } ]` for backward compat — only `text` is rendered visually). Renders as the same plain-bullet matrix as Developer View. At least 3 prioritized items.

### Step 3.8: Pitch Enrichment (single "Boss View")

The Pitch tab no longer has a Developer / General split. It renders ONE audience view called **"Boss View"** — the elevator pitch you'd hand to an exec, an investor, or a hiring manager. There is no real panel-mode toggle on this tab.

> The script reads enrichment from `pitch.boss.*`. Legacy `pitch.dev.*` and `pitch.easy.*` keys are still accepted as fallback so older enrichment files don't break, but **new enrichment MUST use `pitch.boss`**.

The Pitch panel uses **the standard tab background** (no page-level "fancy" gradient — that was reverted in batch 6). The panel-header on Pitch renders the **same `.panel-header > .mode-toggle` pill chrome as every other tab**, with a single non-toggleable button labelled `Boss View` and the `.active` class. Custom flair lives at the SECTION level (gold-haloed `.pitch-oneliner` callout, leaf-bordered `.pitch-story`, etc.), not at the page level.

**Sections (rendered IN ORDER, no `By the Numbers` row):**
1. **The one-liner** (`one_liner`) — a **self-promotional, marketing-tone** single sentence with an "aha" factor. Copy-pasteable. Renders as a gold-haloed callout where the **whole sentence** is rendered in `var(--font-heading)` (Fraunces) at headline size with a gold→amber gradient text fill — the sentence itself is the flashy headline, NOT individual `**bold**` words. **DO NOT use `**bold**` markers in `one_liner`** — they are stripped at render time. Just write a punchy, complete sales-pitch sentence.
2. **Tell your story** (`story`) — narrative paragraph in **product language** (no tech jargon allowed). Body font, non-italic. Sets up *why this exists* in human terms. Copy-pasteable. Spans full content width. **DO NOT use `**bold**` markers in `story`** — they are stripped at render time. The paragraph reads as plain narrative prose; the leaf-bordered card chrome carries the visual weight.
3. **Who is this for?** (`audience`) — bullet array of target personas, **with `**bold**` highlights** on each persona's defining trait. Spans full content width (`width: 100%`, `max-width: none`).
4. **Why does this matter?** (`why_matters`) — bullet array linking the project to a **real-world problem** with concrete numbers / stakes when possible, **with `**bold**` highlights**. Full width.
5. **What makes it special?** (`what_special`) — bullet array of differentiators, **with `**bold**` highlights** on the differentiator words themselves. Full width.
6. **Architecture Strengths** (`architecture_strengths`) — bullet array of what the codebase does well, **with `**bold**` highlights**. Full width.
7. **Tech Stack Justification** (`tech_stack_justification`) — bullet array explaining why each major dependency was chosen, **with `**bold**` highlights**. Full width.
8. **Integration Narrative** (`integration_narrative`) — bullet array describing how this project plugs into or extends a larger ecosystem, **with `**bold**` highlights**. Full width.

> Sections 1–2 (one-liner + story) are paragraph form. Sections 3–8 are **bullet arrays** with `**bold**` highlights. The legacy `By the Numbers` metric-row at the bottom of Pitch was **removed in batch 6** — counts (files / LOC / symbols) belong on the Overview tab. Authors MUST NOT re-introduce a `by_the_numbers` row on Pitch.

### Step 3.9: Simulation Enrichment (single "Boss View")

The Simulation tab also drops the Developer / General split for a single **"Boss View"**. There is no real panel-mode toggle — the panel-header uses the same `.mode-toggle` pill chrome as the rest of the tabs with a single non-toggleable `Boss View` button. The Simulation panel uses **the standard tab background** (no page-level leaf-tint — reverted in batch 6); flair lives at the section level.

> The script reads enrichment from `simulation.boss.*`. Legacy `simulation.dev.*` and `simulation.easy.*` keys are still accepted as fallback (the script auto-merges legacy `easy.takes_off` + `dev.growth_scenario` into the new "What if it takes off" content if `boss.takes_off` is missing), but **new enrichment MUST use `simulation.boss`**.

**Sections (rendered IN ORDER):**
1. **What if it takes off?** (`takes_off`) — bullet array combining product-view success scenarios with developer-view growth scenarios, **with `**bold**` highlights**. The script renders this section inside `.sim-takeoff-card`. The card has a **giant low-opacity 🚀 watermark** sitting behind the content (left-anchored, `clamp(220px, 28vw, 360px)` font size, ~0.08 opacity, slight rotation) — content sits on top with `position: relative; z-index: 1`. Padding is symmetric (`26px 28px`) so paragraphs/bullets start from the LEFT edge and span the full content width. Wording must be in **product language** even when describing technical scaling.
2. **What comes next?** (`whats_next_cards`) — list of feature cards `[ { title, bullets, effort? } ]`. Each card describes a future capability with: a noun-first **title**, a 2-4 bullet array (**with `**bold**` highlights**), and an optional `effort` (rendered as a Pineapple Seasoning Score chip). Renders as `.card-grid.sim-next-grid`.
3. **Growing pains to watch for** (`growing_pains`) — bullet array of plain-language scaling warnings, **with `**bold**` highlights**. The bullets MUST span the full content width — `.simulation-panel ul.prose-bullets` overrides the generic `78ch` cap.
4. **The big picture** (`big_picture_steps`) — `[ { title, when?, text } ]` rendered as a `.scalability-roadmap.big-picture-stepper` (numbered medallions, when-pills, leaf-tinted palette). Wording must be in **product language**, NOT technical jargon — describes the phased journey from "today" to "long-term vision". 4–5 phases preferred. **Inside this stepper ONLY**, `**bold**` keyword highlights render as **plain underlined text** (no bold weight, no yellow highlight) so the stepper reads as a quiet roadmap rather than a loud emphasized list.

> If `boss.big_picture_steps` is missing, the script auto-builds a fallback stepper from the leftover legacy fields (`dev.architecture_evolution`, `easy.big_picture`, `dev.team_scaling`, `easy.building_team`) so existing enrichment files still produce a stepper.

### Step 3.10: Write Enrichment JSON

After completing all enrichment steps (3.2–3.9), write the content to `.codebase-almanac/enrichment.json`. The generation script reads this file and injects the content into the HTML automatically — no manual HTML editing needed.

The JSON structure must match the keys the script expects:

```json
{
  "overview": {
    "project_summary": "2-3 sentences about the project...",
    "tab_summaries": {
      "product": "1-2 sentence highlight for Product tab",
      "technical": "1-2 sentence highlight for Technical tab",
      "database": "1-2 sentence highlight for Database tab (if applicable)",
      "security": "1-2 sentence highlight for Security tab",
      "suggestions": "1-2 sentence highlight for Suggestions tab",
      "pitch": "1-2 sentence highlight for Pitch tab",
      "simulation": "1-2 sentence highlight for Simulation tab"
    }
  },
  "product": {
    "dev": {
      "feature_map": [
        { "title": "Feature Name", "description": "What it does, key modules, endpoints" }
      ],
      "api_surface": [
        { "method": "GET", "path": "/api/...", "auth": true, "description": "..." }
      ],
      "product_architecture": "How features are distributed across packages...",
      "design_patterns": [
        { "title": "Pattern Name", "description": "How the pattern is used" }
      ],
      "workflow_mermaid": "flowchart TD\n  ..."
    },
    "easy": {
      "what_it_does": "Plain-language feature description...",
      "capabilities": ["Capability 1", "Capability 2"],
      "organization": "How the app is organized in plain language...",
      "workflow_mermaid": "flowchart TD\n  ..."
    }
  },
  "technical": {
    "dev": {
      "backend_analysis": "Middleware pipeline, controllers, storage strategy...",
      "frontend_analysis": "Component structure, state management, routing...",
      "code_quality": [
        { "title": "Finding", "description": "Details" }
      ],
      "architecture_mermaid": "graph TB\n  ..."
    },
    "easy": {
      "how_built": "Plain-language analogy explaining the layers...",
      "main_parts": "Description of the actual packages...",
      "connections": "How the parts connect in plain language...",
      "health_check": [
        { "label": "Organization: Good", "description": "Why", "color": "green" }
      ],
      "architecture_mermaid": "graph TB\n  ..."
    }
  },
  "database": {
    "dev": {
      "index_analysis": "Existing indexes, recommendations...",
      "query_patterns": "ORM vs raw SQL, transactions...",
      "backend_integration": "Connection management, where DB calls live...",
      "er_mermaid": "erDiagram\n  ...",
      "data_flow_mermaid": "sequenceDiagram\n  ..."
    },
    "easy": {
      "what_data": "What data the app stores...",
      "how_talks": "How the app reads and writes data...",
      "data_safety": "Data integrity explanation...",
      "er_mermaid": "erDiagram\n  ..."
    }
  },
  "security": {
    "findings": [
      { "severity": "high", "title": "...", "location": "file.ts", "detail": "...", "remediation": "..." }
    ],
    "dev": {
      "auth_analysis": "JWT patterns, secret management, role checks...",
      "input_validation": "What's validated, what's not, injection risks...",
      "dependency_risk": "Known CVEs, risky patterns...",
      "scalability": "Bottlenecks, horizontal readiness...",
      "high_count": 2, "medium_count": 2, "low_count": 1
    },
    "easy": {
      "is_safe": "Traffic-light verdict...",
      "safety_color": "yellow",
      "needs_attention": "Plain-language risks...",
      "access_control": "Who can access what...",
      "growth": "Can it handle growth..."
    }
  },
  "suggestions": {
    "dev": {
      "product": [{ "title": "...", "description": "...", "location": "file.ts", "effort": "Small" }],
      "technical": [{ "title": "...", "description": "...", "location": "file.ts", "effort": "Medium" }],
      "security": [{ "title": "...", "description": "...", "location": "file.ts", "effort": "Small" }],
      "scalability_roadmap": ["Step 1...", "Step 2..."],
      "priority_matrix": [{ "label": "Do now", "text": "..." }, { "label": "Do soon", "text": "..." }]
    },
    "easy": {
      "product": "Plain-language product improvements...",
      "code": "Plain-language technical suggestions...",
      "security": "Plain-language security improvements...",
      "growth": "Plain-language growth readiness...",
      "priorities": [{ "label": "Do now", "text": "..." }, { "label": "Do soon", "text": "..." }]
    }
  },
  "pitch": {
    "dev": {
      "elevator_pitch": "3-4 sentence technical pitch...",
      "strengths": ["Strength 1", "Strength 2"],
      "tech_stack_justification": "Why these technologies...",
      "integration_narrative": "How it fits into a larger ecosystem...",
      "by_the_numbers": [{ "value": "34", "label": "files" }]
    },
    "easy": {
      "story": "We built X to solve Y...",
      "one_liner": "Single sentence value proposition",
      "audience": "Who this is for...",
      "why_matters": "Why it matters...",
      "differentiators": ["Differentiator 1", "Differentiator 2"]
    }
  },
  "simulation": {
    "dev": {
      "growth_scenario": "10x/100x/1000x projections...",
      "feature_expansion": "What adding features requires...",
      "failure_modes": "What breaks first...",
      "team_scaling": "2/5/10+ developer impact...",
      "architecture_evolution": "Stage-by-stage evolution..."
    },
    "easy": {
      "takes_off": "Success scenario narrative...",
      "whats_next": "Feature expansion opportunities...",
      "growing_pains": "Scaling warnings...",
      "building_team": "Team growth support...",
      "big_picture": "Long-term vision..."
    }
  }
}
```

**Important:** Every string value must be **codebase-specific** — derived from the files read in Steps 3.1–3.9. The generation script uses `[AI_FILL: ...]` markers as fallbacks for any missing keys, so if a key is present in the JSON, the marker is replaced automatically.

### Inline emphasis in summary prose (`**bold**` markers)

Every summary string the AI writes — `project_summary`, every `tab_summaries.*`, every per-tab paragraph (`product_architecture`, `tech.dev.backend_analysis`, `security.dev.scalability`, `pitch.dev.elevator_pitch`, `simulation.easy.takes_off`, etc.) and every card `description` in `*.dev.product / technical / security`, `tech.dev.code_quality`, `prod.dev.features`, `prod.dev.design_patterns` — **may use `**double-asterisks**` to mark important words and phrases**. The generator renders them as highlighted **keyword** tokens.

Rules:

- Mark only **important** words: framework/library names (`**Express**`, `**SQLite**`), file or domain names (`**authService.ts**`, `**categories**`), risk anchors (`**JWT fallback secret**`, `**localStorage**`), pattern names (`**WAL mode**`, `**CASCADE deletes**`).
- Do **not** mark every noun. Aim for ~3–6 keywords per paragraph.
- Numbers do **not** need markers — counts and units like `24`, `~1900`, `12k`, `7-day`, `100×` are auto-emphasized.
- Markers are escape-safe: any text without `**` simply renders as plain HTML.
- Always write in plain language for the `easy` content even when emphasizing — emphasis is purely visual.

The generator wraps `**word**` as `<strong class="kw">word</strong>` and standalone numeric tokens as `<span class="num">…</span>`.

### Security findings: recommendation text (required for the Security tab)

Each object in `security.findings` **must** include actionable guidance in at least one of these fields:

| Field | Purpose |
| --- | --- |
| **`remediation`** | Preferred — specific steps the team should take (rendered under **Recommendation:** in HTML). |
| **`recommendation`** | Optional synonym of `remediation` (used only if `remediation` is missing). |
| **`detail`** | Background context. If `remediation`/`recommendation` are both missing, `detail` is promoted into the **Recommendation:** line so the row is never blank. |

Display order: **`remediation` → `recommendation` → (`detail` promoted)**. If all three are missing, the script renders an italic placeholder so the gap is visible during review (still never blank). When you write `detail`, prefer keeping a separate `remediation` so the user sees both context and action.

### Mermaid syntax for Mermaid.js 10 / 11 (diagrams must parse)

Diagrams are rendered by **Mermaid.js from jsDelivr** (currently v10+ / v11). Invalid syntax shows **“Syntax error in text”** in the browser. Follow these rules when authoring `workflow_mermaid`, `architecture_mermaid`, `er_mermaid`, `data_flow_mermaid`, and similar fields:

1. **Subgraphs (flowchart / graph)** — Put **one space** between the subgraph id and the opening bracket: `subgraph myId [Title with spaces]`. Avoid `subgraph myId["Title"]` (no space before `[`), which breaks newer parsers. The generator also normalizes common `subgraph id["..."]` patterns when present.
2. **Square node labels with a colon (`:`) or other punctuation** — If the text inside `[...]` contains `:`, `/`, `(`, `)`, `&`, etc., wrap the label in double quotes: `U["Browser: app.js"]` instead of `U[Browser: app.js]`. The generator attempts to auto-quote unquoted colon labels, but writing them quoted is safer.
3. **`erDiagram` attribute types** — Use Mermaid-friendly types such as **`string`**, `int`, `boolean`, `date`, etc. Do **not** use SQL-style **`text`** as the first word on an attribute line (it is a syntax error in many Mermaid builds). The generator rewrites `text` → `string` on attribute lines inside entity blocks when possible.
4. **`erDiagram` without entity bodies** — Relationship-only diagrams (just `A ||--o{ B : verb` lines after `erDiagram`) ARE valid; you do not need `{ ... }` blocks if you only want relationships.
5. **Dependency graph** — Internal module labels in the auto-generated dependency diagram are sanitized by the script (never HTML-entity-escaped inside Mermaid source).
6. **Diagram containers are responsive** — The script wraps every `<pre class="mermaid">` in a `.diagram-container` that constrains rendered SVG to `max-width: 100%` with horizontal scroll fallback. Author diagrams as if the canvas were narrow; avoid 12-node-wide flowcharts that force scrolling.

---

## Phase 4: HTML Generation

### Run the Generation Script

Run:

```bash
python scripts/generate-visualization.py <analysis.json> <output.html> [title] [project_name] --enrichment <enrichment.json>
```

Arguments:
- `<analysis.json>` — Path to the `codebase-analysis.json` from Phase 1 (e.g., `.codebase-almanac/codebase-analysis.json`)
- `<output.html>` — Path for the output HTML file. **MUST use a timestamped name** (e.g., `.codebase-almanac/visualization-20260426-134500.html`). Never reuse or overwrite a previous output file.
- `[title]` — (Optional) Custom page title. Defaults to `"{project_name} — Code Visualization"`
- `[project_name]` — (Optional) Override the project name detected in the JSON
- `--enrichment <enrichment.json>` — **(Optional)** Path to the `enrichment.json` written in Phase 3 Step 3.10. **Auto-discovered** when the analysis JSON sits next to it (canonical layout: `.codebase-almanac/codebase-analysis.json` + `.codebase-almanac/enrichment.json`). The script merges this into the analysis data and fills all content sections automatically. Without enrichment (and no auto-discovered sibling), the visualization renders `[AI_FILL]` placeholders in every section — that's the silent-failure mode the auto-discover guards against, so always either keep the canonical layout or pass `--enrichment` explicitly.

The script produces a single self-contained HTML file with the Pineapple Tropical Maximalist theme. It reads `visualization-base.css` from the project root automatically and embeds all CSS, JS, Mermaid diagrams, and an SVG pineapple hero illustration inline. Before embedding, it **normalizes Mermaid source** (subgraph spacing, common `erDiagram` type mistakes, colon-in-label edge cases, and dependency-node labels) so diagrams parse under **Mermaid.js 10+**, and it maps security finding text in order **`remediation` → `recommendation` → `detail`** into the **Recommendation:** row.

**What the script generates:**

The visualization has 8 tabs (7 mandatory + 1 conditional). Every tab except Overview has separate **Developer View** and **General View** content. The toggle does **not** live in the global header — it sits **inside each non-Overview tab panel**, replacing the per-tab breadcrumb (e.g. where `Project / Product` used to be). The Overview tab keeps its breadcrumb because it has no mode split. Buttons are labelled **`Developer View`** and **`General View`** and use `data-mode="dev"` / `data-mode="easy"`; `setMode()` syncs every toggle instance via `document.querySelectorAll('.mode-toggle [data-mode]')`.

| Tab | Developer View | General View |
| --- | --- | --- |
| Overview | Hero + metrics + language bar + clickable summary grid linking to every other tab | (same — no mode split) |
| Product | Feature map, user workflow diagrams, API surface table, product architecture, design patterns | "What does this app do?", "How do people use it?", capability checklist, simple organization |
| Technical | Architecture diagram, backend/frontend analysis (bullets), dependency graph, symbol catalog, code quality (cards w/ highlights) | "How is the code built?", main parts, connections, **4-tier health check** (Health / Sick / Severe Sick / Death) with legend |
| Database *(conditional)* | ER diagram, index analysis, query patterns, backend integration, data flow sequence | "What data?", simplified ER, "How does it talk to the DB?", data safety |
| Security | Risk summary, detailed findings, auth analysis, input validation audit, dependency risk, scalability | "Is it safe?" rating, plain-language risks, "Who can access what?", growth assessment |
| Suggestions | Product / technical / security suggestions with files + effort, scalability roadmap, priority matrix | Plain-language improvements, "What to do first" with Do now / Do soon / Do later |
| Pitch | Technical elevator pitch, architecture strengths, tech stack justification, metrics for pitch deck | "Tell your story" narrative, one-liner, "Who is this for?", differentiators |
| Simulation | Growth at 10×/100×/1000×, feature expansion modeling, failure modes, team scaling, architecture evolution | "What if it takes off?", "What comes next?", growing pains, team growth, big picture |

The Database tab is **conditionally shown**: if the extraction JSON contains no database-related data (`has_database: false` or no schema/models), the tab button and panel are omitted from the output.

**Built-in features:**
- Sidebar with collapsible file tree — click a file to jump to its symbols in the Technical tab
- Tab bar with keyboard shortcuts: `1`–`8` jump between tabs (no search input, no `/` shortcut)
- **Per-tab mode toggle** (Developer View / General View) — rendered inside every non-Overview tab in place of the breadcrumb; one click syncs the active state across all tabs simultaneously
- **Inline emphasis** in summary prose: `**word**` markers + auto-emphasized numbers
- **Bullet-style cards & prose** for dense Developer-View content (`backend_analysis`, `frontend_analysis`, `index_analysis`, `query_patterns`, `backend_integration`, `product_architecture`, plus `bullets` field on Feature Map / Code Quality cards)
- **Mermaid diagrams render at natural size** (`useMaxWidth: false`) so font sizes are consistent across the document
- **4-tier Code Health Check** (Health / Sick / Severe Sick / Death) with a legend strip above the items
- **Codebase intro card** below the pineapple — gradient-bordered, gold-rind glow, gradient-text title — owns the codebase name + AI summary (replaces the old left-of-pineapple eyebrow + headline)
- **Single evergreen block left of the pineapple** (title + AGI / Fibonacci tagline) — same on every codebase, not templated from the analysis JSON
- **Per-tab mode toggle** (Developer View / General View) replaces the breadcrumb on every non-Overview tab; the Overview tab has no breadcrumb either
- **Persistent bottom-left credits block** (PineApple Team / @HenryZou + LinkedIn / @JennyZheng + LinkedIn / 2026), darker semi-transparent background, responsive on small screens
- **3D pineapple hero illustration** with grounded crown leaves (no stray fragments outside the body)
- Accessible tooltips on key terms (keyboard and screen reader friendly)
- Pineapple-skin diamond-lattice dividers between sections
- `prefers-reduced-motion` support, print-friendly mode, responsive down to 768px (and degrades gracefully to 420px)

---

## Phase 4.5: Verification (Mandatory)

The enrichment JSON from Phase 3 feeds the script automatically. After the script finishes, verify the output is complete.

### Step 4.5.1: Check for Remaining Markers

Search the generated HTML for `[AI_FILL`. Count occurrences.

- **If count is zero** — all enrichment content was injected successfully. Proceed to Phase 5.
- **If count is greater than zero** — some enrichment keys were missing from `enrichment.json`. For each remaining marker:
  1. Note the marker text (it describes what content is needed)
  2. Add the missing key to `enrichment.json`
  3. Re-run the generation script
  4. Repeat until the count is **zero**

### Step 4.5.2: Spot-check Quality

Quickly scan the HTML for any section that looks generic or could apply to any project. If the enrichment JSON contained vague content, the script will faithfully render vague content. If you spot any, update the corresponding key in `enrichment.json` and re-run.

**Do not proceed to Phase 5 until `[AI_FILL` count is zero.**

---

## Phase 5: Delivery

1. **Clean up** — Delete `.codebase-almanac/previews/` if it exists
2. **Open in browser (mandatory)** — Always run `open <output.html>` (macOS) or `xdg-open <output.html>` (Linux) immediately after generation. Do not skip this step or ask whether the user wants it opened — just open it.
3. **Summarize** — Tell the user:
   - File location, file size, visualization scope
   - Navigation: Tab bar (8 tabs), sidebar file tree, keyboard shortcuts (`1`–`8`), and audience mode toggle (no search bar — by design)
   - How to read the highlights: `**bolded keywords**` are AI-marked important terms; numbers are auto-emphasized
   - How to customize: `:root` CSS variables for colors, font link for typography, `.kw` / `.num` / `.credits` classes if you want to restyle highlights or the credits block
   - How to use tooltips, suggestions, pitch narratives, and simulations for stakeholder communication
   - How to regenerate: re-run the skill with different options

---

## Supporting Files

| File | Purpose | When to Read |
| --- | --- | --- |
| [scripts/extract-codebase.py](scripts/extract-codebase.py) | Python script for codebase structure extraction | Phase 1 (extraction) |
| [scripts/generate-visualization.py](scripts/generate-visualization.py) | Generates the full HTML visualization from extraction JSON (Pineapple theme) | Phase 4 (default generation) |
| [visualization-base.css](visualization-base.css) | Mandatory responsive CSS — embedded by the script | Phase 4 (generation) |
