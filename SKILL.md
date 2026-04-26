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

- Output MUST be a single `.html` file (plus Mermaid CDN)
- Every visualization MUST include the full contents of `visualization-base.css`
- All diagrams use Mermaid.js syntax rendered client-side
- CSS variables for theming — never hardcoded colors in component styles
- Responsive down to 768px width
- `prefers-reduced-motion` support on all animations
- Print-friendly mode via `@media print`
- MUST include glossary tooltips for technical terms and architecture jargon
- MUST support two audience modes inside the same visualization:
  - **Developer/Programmer Mode** (deeper technical detail)
  - **Easy Mode** (plain-language simplification)
- MUST include simulation views so users can explore "what happens if..." scenarios for architecture, scale, and risk

---

## Phase 0: Detect Mode

Determine what the user wants:

- **Mode A: New Analysis** — User points to a codebase directory. Go to Phase 1.
- **Mode B: Demo** — User wants to try it out. Use the built-in `example/` directory. Go to Phase 1.

### Fresh Generation Rule

**Always generate a brand-new HTML file.** Never reuse, patch, or modify a previously generated visualization. Even if a `.code-visualizer/` directory already contains HTML files from prior runs, ignore them and generate fresh. Each output file MUST have a unique timestamped filename:

```
.code-visualizer/visualization-YYYYMMDD-HHMMSS.html
```

This guarantees every run produces an independent artifact and prior visualizations are preserved for comparison.

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

**Question 0 — Audience Mode** (header: "Audience Mode"):
Which mode should be available by default? Options:
- "Both (recommended)" — Toggle between Developer/Programmer + Easy mode
- "Developer/Programmer mode default"
- "Easy mode default"

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
Which visual theme do you want? Options:
- "Pineapple Tropical (default)" — The built-in theme used by `generate-visualization.py`. Golden yellow, amber, and tropical green with hand-drawn pineapple hero, diamond-lattice textures, and editorial serif typography. No extra configuration needed.
- "Choose from presets" — Pick from the 6 themes in [STYLE_PRESETS.md](STYLE_PRESETS.md) (Blueprint Dark, Obsidian Graph, Neon Terminal, Paper White, Arctic Light, Warm Slate). Requires manual HTML generation in Phase 4 instead of the script.
- "Show me previews" — Generate 3 single-page HTML previews to compare before choosing.

### Step 2.1: Pineapple Tropical (default path)

No additional style configuration needed. Proceed directly to Phase 3. The generation script in Phase 4 handles everything.

### Step 2.2: Style Previews (if "Show me previews")

Read [STYLE_PRESETS.md](STYLE_PRESETS.md) for available themes.

Generate 3 single-page HTML previews under `.code-visualizer/previews/` (style-a.html, style-b.html, style-c.html). Each preview should show:
- The project name and a summary card
- A sample Mermaid diagram
- A sample file tree section
- The color palette and typography in action

Open each preview for the user automatically.

Ask (header: "Theme"):
Which style do you prefer? Options: Style A: [Name] / Style B: [Name] / Style C: [Name] / Mix elements

### Step 2.3: Direct Selection (if "Choose from presets")

Show the available presets from [STYLE_PRESETS.md](STYLE_PRESETS.md) and let the user pick.

**Note:** Choosing a preset theme (Steps 2.2 or 2.3) requires manual HTML generation in Phase 4 — the generation script only supports the Pineapple Tropical theme.

---

## Phase 3: AI Enrichment

The extraction script provides structure. Now the agent reads key files to add semantic understanding. Every tab (except Overview) requires **two versions** of its prose content: one for **Developer mode** (precise, technical, references file paths) and one for **Easy mode** (plain-language, no jargon, targets non-coders).

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
- **Project summary** — 2-3 sentences: what the project is, what it does, who it is for. This goes directly below the hero/pineapple illustration.
- **Tab summaries** — for each of the other 7 tabs, write a 1-2 sentence "highlight finding" (the single most important takeaway from the actual analysis). These become clickable cards linking to each tab. **Each card description must be specific to the codebase** — never use generic text like "Explore the X analysis." Example: "6 feature domains across 4 packages with 19 API endpoints" not "Explore the Product analysis."

The Overview tab must **not** include a "Frameworks" section or a "Navigation" section — remove them if the script generates them. The language bar, metrics row, and tab summary cards are sufficient.

### Step 3.3: Product Enrichment

Produce content for the Product tab in **both** Developer and Easy mode:

**Developer mode content:**
- **Feature map** — card grid of detected feature domains. Each entry: domain name, implementing modules/files, key endpoints, scope description
- **User workflow diagrams** — Mermaid flowcharts of primary user journeys derived from route analysis and controller logic. Use technical labels (HTTP methods, endpoint paths)
- **API surface table** — every route/endpoint with columns: Method, Path, Auth Required, Description
- **Product architecture** — how features are distributed across packages/modules; which package owns which domain
- **Design patterns identified** — product patterns visible in the code (RBAC, pagination, rate limiting, input sanitization, error messaging strategy)

**Easy mode content:**
- **"What does this app do?"** — plain-language feature descriptions
- **"How do people use it?"** — simplified workflow diagrams with friendly labels (e.g., "Sign up" instead of "POST /auth/register")
- **"What can users do?"** — capability checklist with checkmarks
- **"How is the app organized?"** — simple explanation of the main parts and their roles

### Step 3.4: Technical Enrichment

Produce content for the Technical tab in **both** Developer and Easy mode:

**Developer mode content:**
- **Architecture diagram** — Mermaid diagram of system layers annotated with actual module names
- **Backend analysis** — middleware pipeline, route structure, controller patterns, error handling strategy, with file paths
- **Frontend analysis** (if applicable) — component tree, state management, routing, build tooling. If no frontend, state that explicitly
- **Module dependency graph** — Mermaid graph of internal import/export relationships
- **Symbol catalog** — searchable table: name, kind, file, exported status (generated by the script from extraction JSON)
- **Code quality signals** — file size distribution, largest files, circular dependency warnings, coupling indicators

**Easy mode content:**
- **"How is the code built?"** — building-blocks analogy explaining the layers
- **"The main parts"** — simplified architecture diagram with plain labels
- **"How the parts connect"** — simplified dependency view in plain sentences
- **"Code health check"** — traffic-light (green/yellow/red) indicators for size, complexity, organization with plain explanations

### Step 3.5: Database Enrichment (conditional)

Only produce this content if the codebase has a database. Detection criteria: SQL files, ORM models, migration folders, database drivers in dependencies (e.g., `better-sqlite3`, `pg`, `mongoose`, `prisma`, `drizzle`, `sequelize`, `typeorm`). If no database is detected, set `has_database: false` and skip this step.

**Developer mode content:**
- **Schema design** — ER diagram (Mermaid `erDiagram`) with tables, columns, types, relationships (FK, unique constraints)
- **Index analysis** — existing indexes, which queries benefit, missing index recommendations
- **Query patterns** — ORM vs raw SQL, transaction usage, bulk operations
- **Backend integration** — connection management (pooling, WAL mode), where DB calls live (repository pattern? inline?), error handling for DB failures
- **Data flow** — Mermaid sequence diagram: request → controller → database → response

**Easy mode content:**
- **"What data does the app store?"** — plain-language descriptions of each data type
- **"How is data organized?"** — simplified ER diagram with friendly labels and plain relationship words
- **"How does the app talk to the database?"** — simple read/write explanation
- **"Is the data safe?"** — plain-language data integrity explanation

### Step 3.6: Security Enrichment

Produce content for the Security tab in **both** Developer and Easy mode:

**Developer mode content:**
- **Risk summary** — counts of High / Medium / Low severity findings
- **Detailed findings** — each finding with: severity, title, file location, code context (`detail`), and specific remediation steps in **`remediation`** (optional alias **`recommendation`** — both render under **Recommendation:** in the HTML; if both are set, `remediation` wins)
- **Authentication & authorization analysis** — JWT/session patterns, secret management, token expiry, role checks
- **Input validation audit** — what inputs are validated, what are not, injection risk areas
- **Dependency risk** — known CVEs or risky patterns in third-party packages
- **Scalability analysis** — bottlenecks (in-memory state, single-process, no caching, no queue), horizontal vs vertical readiness, connection pooling, rate limiting capacity

**Easy mode content:**
- **"Is the app safe?"** — traffic-light overall safety rating with a one-sentence verdict
- **"What needs attention?"** — plain-language risk descriptions
- **"Who can access what?"** — simplified auth explanation
- **"Can the app handle growth?"** — plain-language scalability assessment

### Step 3.7: Suggestion Enrichment

Produce content for the Suggestions tab in **both** Developer and Easy mode:

**Developer mode content:**
- **Product suggestions** — feature gaps, missing UX flows, inconsistent API patterns, missing error states. Each with: title, description, affected files, effort estimate (small/medium/large)
- **Technical suggestions** — refactoring opportunities, architecture improvements, performance optimizations, test coverage gaps, missing strictness
- **Security hardening** — specific fixes with file paths and code-level guidance
- **Scalability roadmap** — concrete ordered steps (e.g., "1. Add persistent DB → 2. Add caching → 3. Extract background jobs → 4. Add load balancer")
- **Priority matrix** — effort-vs-impact ranking: what to do first, what to do later

**Easy mode content:**
- **"How to make the product better"** — plain-language improvement ideas
- **"How to make the code stronger"** — simplified technical suggestions
- **"How to make it safer"** — non-jargon security improvements
- **"How to handle more users"** — growth readiness in plain language
- **"What to do first"** — prioritized action items labeled: "Do now", "Do soon", "Do later"

### Step 3.8: Pitch Enrichment

Produce content for the Pitch tab in **both** Developer and Easy mode:

**Developer mode content:**
- **Technical elevator pitch** — 3-4 sentence paragraph: tech stack, architecture pattern, key technical strengths. Copy-pasteable.
- **Architecture strengths** — bullet list of what the codebase does well
- **Tech stack justification** — why these technologies make sense for the use case
- **Integration narrative** — how this project fits into or extends a larger ecosystem
- **By the numbers** — key metrics formatted for a pitch deck slide

**Easy mode content:**
- **"Tell your story"** — ready-to-use narrative paragraph: "We built [project] to solve [problem]. It lets users [capability]."
- **"The one-liner"** — single sentence value proposition for a landing page
- **"Who is this for?"** — target audience in plain terms
- **"Why does this matter?"** — impact statement connecting the project to a real-world problem
- **"What makes it special?"** — 3-4 differentiators in plain language

### Step 3.9: Simulation Enrichment

Produce content for the Simulation tab in **both** Developer and Easy mode:

**Developer mode content:**
- **Growth scenario** — what happens at 10×, 100×, 1000× users: infrastructure needs, DB load, latency projections
- **Feature expansion modeling** — what adding features A, B, C would require: which modules change, estimated effort, dependency impact
- **Failure mode analysis** — what breaks first under load, dependency failure impact, disaster recovery readiness
- **Team scaling** — how the codebase supports 2, 5, 10+ developers: module boundaries, merge conflict hotspots, onboarding complexity
- **Architecture evolution path** — what the architecture should evolve into at each growth stage

**Easy mode content:**
- **"What if it takes off?"** — success scenario narrative for 10,000 users
- **"What comes next?"** — feature expansion possibilities framed as opportunities
- **"Growing pains to watch for"** — plain-language warnings about scaling
- **"Building your team"** — how the project structure supports more contributors
- **"The big picture"** — long-term vision framing

### Step 3.10: Write Enrichment JSON

After completing all enrichment steps (3.2–3.9), write the content to `.code-visualizer/enrichment.json`. The generation script reads this file and injects the content into the HTML automatically — no manual HTML editing needed.

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

### Security findings: recommendation text (required for the Security tab)

Each object in `security.findings` **must** include actionable guidance in at least one of these fields (they are merged for display):

| Field | Purpose |
| --- | --- |
| **`remediation`** | Preferred — specific steps the team should take (rendered under **Recommendation:** in HTML). |
| **`recommendation`** | Optional synonym of `remediation` (used only if `remediation` is missing). |
| **`detail`** | Used only when both of the above are empty (fallback so the row is not blank). |

The Phase 4 script maps these keys into the single **Recommendation:** line in display order: **`remediation` → `recommendation` → `detail`**. Use **`remediation`** in new JSON to match the Step 3.6 prose template.

### Mermaid syntax for Mermaid.js 10 / 11 (diagrams must parse)

Diagrams are rendered by **Mermaid.js from jsDelivr** (currently v10+). Invalid syntax shows **“Syntax error in text”** in the browser. Follow these rules when authoring `workflow_mermaid`, `architecture_mermaid`, `er_mermaid`, `data_flow_mermaid`, and similar fields:

1. **Subgraphs (flowchart / graph)** — Put **one space** between the subgraph id and the opening bracket: `subgraph myId [Title with spaces]`. Avoid `subgraph myId["Title"]` (no space before `[`), which breaks newer parsers. The generator also normalizes common `subgraph id["..."]` patterns when present.
2. **Square node labels with a colon (`:`)** — If the text inside `[...]` contains `:`, wrap the label in double quotes: `U["Browser: app.js"]` instead of `U[Browser: app.js]`. The generator attempts to fix unquoted colon labels, but writing them quoted is safer.
3. **`erDiagram` attribute types** — Use Mermaid-friendly types such as **`string`**, `int`, `boolean`, `date`, etc. Do **not** use SQL-style **`text`** as the first word on an attribute line (it is a syntax error in many Mermaid builds). The generator rewrites `text` → `string` on attribute lines inside entity blocks when possible.
4. **Dependency graph** — Internal module labels in the auto-generated dependency diagram are sanitized by the script (never HTML-entity-escaped inside Mermaid source).

---

## Phase 4: HTML Generation

### Default Path: Run the Generation Script

If the user chose the Pineapple Tropical theme (default) or did not express a theme preference, run the generation script:

```bash
python scripts/generate-visualization.py <analysis.json> <output.html> [title] [project_name] --enrichment <enrichment.json>
```

Arguments:
- `<analysis.json>` — Path to the `codebase-analysis.json` from Phase 1 (e.g., `.code-visualizer/codebase-analysis.json`)
- `<output.html>` — Path for the output HTML file. **MUST use a timestamped name** (e.g., `.code-visualizer/visualization-20260426-134500.html`). Never reuse or overwrite a previous output file.
- `[title]` — (Optional) Custom page title. Defaults to `"{project_name} — Code Visualization"`
- `[project_name]` — (Optional) Override the project name detected in the JSON
- `--enrichment <enrichment.json>` — **(Required)** Path to the `enrichment.json` written in Phase 3 Step 3.10. The script merges this into the analysis data and fills all content sections automatically.

The script produces a single self-contained HTML file with the Pineapple Tropical Maximalist theme. It reads `visualization-base.css` from the project root automatically and embeds all CSS, JS, Mermaid diagrams, and an SVG pineapple hero illustration inline. Before embedding, it **normalizes Mermaid source** (subgraph spacing, common `erDiagram` type mistakes, colon-in-label edge cases, and dependency-node labels) so diagrams parse under **Mermaid.js 10+**, and it maps security finding text in order **`remediation` → `recommendation` → `detail`** into the **Recommendation:** row.

**What the script generates:**

The visualization has 8 tabs (7 mandatory + 1 conditional). Every tab except Overview has separate **Developer mode** and **Easy mode** content, toggled by the header switch.

| Tab | Developer Mode | Easy Mode |
| --- | --- | --- |
| Overview | Hero + metrics + language bar + clickable summary grid linking to every other tab | (same — no mode split) |
| Product | Feature map, user workflow diagrams, API surface table, product architecture, design patterns | "What does this app do?", "How do people use it?", capability checklist, simple organization |
| Technical | Architecture diagram, backend/frontend analysis, dependency graph, symbol catalog, code quality | "How is the code built?", main parts, connections, traffic-light health check |
| Database *(conditional)* | ER diagram, index analysis, query patterns, backend integration, data flow sequence | "What data?", simplified ER, "How does it talk to the DB?", data safety |
| Security | Risk summary, detailed findings, auth analysis, input validation audit, dependency risk, scalability | "Is it safe?" rating, plain-language risks, "Who can access what?", growth assessment |
| Suggestions | Product / technical / security suggestions with files + effort, scalability roadmap, priority matrix | Plain-language improvements, "What to do first" with Do now / Do soon / Do later |
| Pitch | Technical elevator pitch, architecture strengths, tech stack justification, metrics for pitch deck | "Tell your story" narrative, one-liner, "Who is this for?", differentiators |
| Simulation | Growth at 10×/100×/1000×, feature expansion modeling, failure modes, team scaling, architecture evolution | "What if it takes off?", "What comes next?", growing pains, team growth, big picture |

The Database tab is **conditionally shown**: if the extraction JSON contains no database-related data (`has_database: false` or no schema/models), the tab button and panel are omitted from the output.

**Built-in features:**
- Sidebar with collapsible file tree — click a file to jump to its symbols in the Technical tab
- Tab bar with keyboard shortcuts: `1`–`8` for tabs, `/` for search, `Esc` to clear
- Developer/Easy mode toggle in the header — switches content in all tabs simultaneously
- Accessible tooltips on key terms (keyboard and screen reader friendly)
- Pineapple-skin diamond-lattice dividers between sections
- `prefers-reduced-motion` support, print-friendly mode, responsive down to 768px

### Alternate Path: Manual HTML Generation (non-Pineapple theme)

If the user chose a theme from [STYLE_PRESETS.md](STYLE_PRESETS.md) in Phase 2, generate the HTML manually. **Before generating, read these supporting files:**

- [html-template.md](html-template.md) — HTML skeleton and JS contracts
- [visualization-base.css](visualization-base.css) — Mandatory CSS (include in full)
- [animation-patterns.md](animation-patterns.md) — Interaction patterns

The manually generated HTML must follow the same output structure (all 8 tabs, sidebar, navigation, mode toggle) and key requirements listed in [html-template.md](html-template.md). Apply the chosen preset's CSS variables, fonts, Mermaid theme config, and signature elements from [STYLE_PRESETS.md](STYLE_PRESETS.md).

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

1. **Clean up** — Delete `.code-visualizer/previews/` if it exists
2. **Open in browser (mandatory)** — Always run `open <output.html>` (macOS) or `xdg-open <output.html>` (Linux) immediately after generation. Do not skip this step or ask whether the user wants it opened — just open it.
3. **Summarize** — Tell the user:
   - File location, file size, visualization scope
   - Navigation: Tab bar (8 tabs), sidebar file tree, search (/ key), keyboard shortcuts (1-8), and audience mode toggle
   - How to customize: `:root` CSS variables for colors, font link for typography
   - How to use tooltips, suggestions, pitch narratives, and simulations for stakeholder communication
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
| [scripts/extract-codebase.py](scripts/extract-codebase.py) | Python script for codebase structure extraction | Phase 1 (extraction) |
| [scripts/generate-visualization.py](scripts/generate-visualization.py) | Generates the full HTML visualization from extraction JSON (Pineapple theme) | Phase 4 (default generation) |
| [STYLE_PRESETS.md](STYLE_PRESETS.md) | Visual themes with CSS variables, fonts, and diagram config | Phase 2 (if choosing non-default theme) |
| [visualization-base.css](visualization-base.css) | Mandatory responsive CSS — included by the script, or manually in alternate path | Phase 4 (generation) |
| [html-template.md](html-template.md) | HTML skeleton, JS contracts, accessibility requirements | Phase 4 (manual generation only) |
| [animation-patterns.md](animation-patterns.md) | Subtle interaction patterns for tree, tabs, cards | Phase 4 (manual generation only) |
| [scripts/deploy.sh](scripts/deploy.sh) | Deploy visualization to Vercel | Phase 6 (sharing) |
| [scripts/export-pdf.sh](scripts/export-pdf.sh) | Export visualization to PDF | Phase 6 (sharing) |
