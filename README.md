# Skill48414: Codebase Almanac

A skill that turns any codebase into a single interactive HTML **almanac** — chapters of maps, statistics, plain-language explanations, security findings, and recommendations in one navigable artifact for both technical and non-technical readers.

If you are non-technical, you can ignore all internal files and just use the prompts below.

## Quickest Way To Use It

### In Cursor

Copy and paste one of these:

```text
Run the code visualizer on example/
```

```text
Generate a code visualization for this project
```

```text
Visualize the codebase at /path/to/my/project
```

### In Claude Code

If installed as a skill, call:

```text
/codebase-almanac
```

Then say:

```text
Run it on example/
```

or

```text
Run it on /path/to/my/project
```

## What You Will Get

The assistant will generate **one HTML file** and open it in your browser.

That file has 4 tabs:
- Overview
- Product
- Technical
- Security

## If You Want The Built-in Demo

Say exactly:

```text
Run the code visualizer on example/
```

## If You Want Your Own Codebase

Say exactly:

```text
Visualize /path/to/my/project
```

## Optional: Save As PDF

After your HTML is generated, ask:

```text
Export this visualization to PDF
```

## Sharing The HTML

The output is a single self-contained `.html` file. Share it the way you share any file: email it, drop it in Slack, attach it to a doc, or commit it to your own static host (GitHub Pages, S3, Netlify, etc.).
