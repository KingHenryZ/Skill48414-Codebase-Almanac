# Skill48414: Codebase Almanac

This skill streamlines the "vibe-coding" experience by providing a clear visual map of your codebase. Designed for both engineers and non-engineers to assemble contexts by offering actionable insights and intelligent suggestions for product features, architectural improvements, security risks, databases, and the idea validation process.

> You point it at a folder of code. It produces **one self-contained HTML file** that opens in any browser. That file is the "almanac" — chapters of maps, statistics, plain-language explanations, findings, and suggestions, all in one place, readable by engineers and non-engineers alike.

---

## Get It From GitHub

You only do this once.

### Step 1 — Make sure you have Python 3

Open a terminal and type:

```bash
python3 --version
```

If you see something like `Python 3.10.4` you're done. If you see `command not found`, install Python from <https://www.python.org/downloads/> and try again.

**No other tools to install.** No `pip install`, no `npm install`. The skill uses only the Python standard library.

### Step 2 — Download the skill ZIP

1. Open <https://github.com/KingHenryZ/Project48414> in your browser
2. Click the green **Code** button → **Download ZIP**
3. Unzip it somewhere you'll remember (e.g. your Desktop or `~/Documents/`)
4. Open the unzipped `Project48414` folder

That folder is the skill.

### Step 3 — Open the skill folder in your editor

**For Cursor users:** open Cursor → **File → Open Folder…** → pick the `Project48414` folder. The skill is auto-registered via `.cursor/rules/visualizer.mdc` — nothing else to do.

**For Claude Code users:** copy the folder into your skills directory:

```bash
cp -r Project48414 ~/.claude/skills/codebase-almanac
```

The skill is now available as `/codebase-almanac` inside Claude Code.

---

## Use It

### First: try the built-in example

There's a small toy codebase already inside `example/`. Run the skill on it first so you can see what the output looks like before bringing your own code.

**In Cursor**, open the chat sidebar and paste:

```text
Run the codebase almanac on example/
```

**In Claude Code**, type:

```text
/codebase-almanac
Run it on example/
```

Then sit back. The assistant will:

1. Scan the example folder
2. Read the important files
3. Write content for every tab
4. Generate the HTML
5. Open it in your default browser

You should see a page with a giant pineapple illustration on the right and chapters laid out below it. **That's the almanac.**

### Then: use it on your own code

Same idea, just point it at any folder on your machine.

**In Cursor:**

```text
Run the codebase almanac on /Users/yourname/path/to/your-project
```

**In Claude Code:**

```text
/codebase-almanac
Run it on /Users/yourname/path/to/your-project
```

The output is written to `.codebase-almanac/visualization-YYYYMMDD-HHMMSS.html` inside your target project. Every run produces a fresh, timestamped file — old ones are kept for comparison.

## What's In Each Tab

The output has up to **8 tabs**. Every tab (except Overview) has a **Developer View** for engineers and a **General View** for non-technical readers — toggle inside the tab.

| Tab | What you'll find |
|---|---|
| **Overview** | The hero pineapple, headline metrics (files / lines / packages / symbols), a language breakdown, and a card grid that links to every other tab. Start here. |
| **Product** | What the app does in plain language, the feature map, user workflows, the API surface, and the product architecture. The page for product managers and stakeholders. |
| **Technical** | Architecture diagram, dependency graph, full symbol catalog, code-quality cards, and a 4-tier code health check (Health / Sick / Severe Sick / Death). The page for engineers. |
| **Database** *(only shown if a database is detected)* | Entity-relationship diagram, index analysis, query patterns, and how the backend talks to the data layer. |
| **Security** | Three-card risk summary (high / medium / low), detailed findings with file locations and recommendations, an authentication audit, an input-validation audit, dependency risk notes, and a scalability section. |
| **Suggestions** | Actionable improvements grouped into Product / Technical / Security, each with a "Pineapple Seasoning Score" effort chip (🍍 Quick Win → 🍍🍍🍍 Big Bake), plus a scalability roadmap and a priority matrix. |
| **Pitch** | A one-line headline, a "tell your story" narrative, who it's for, why it matters, what makes it special, architecture strengths, and tech-stack justification. The page for talking *about* the codebase to humans. |
| **Simulation** | "What if it takes off?" scenarios — 10× / 100× / 1000× growth, what comes next, growing pains, team scaling, and a step-by-step big-picture roadmap. |


---

## License

MIT — see [LICENSE](LICENSE).

---

## The Pineapple Project Team

Made by:

- **Henry Zou** — [@HenryZou on LinkedIn](https://www.linkedin.com/in/cunhanzou/)
- **Jenny Zheng** — [@JennyZheng on LinkedIn](https://www.linkedin.com/in/jenzheny/)

> In the coming era of AGI, building solutions becomes a collective process akin to a pineapple, where technical and non-technical contributors fuse like individual berries into a unified, organic whole. This partnership mirrors the 8 & 13 dual spirals of the Fibonacci sequence, intertwining creative human intent with AI-driven structural analysis to assemble a perfect, high-resolution context for building at the speed of thought.
