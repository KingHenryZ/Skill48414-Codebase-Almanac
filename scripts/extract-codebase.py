#!/usr/bin/env python3
"""
Extract structure and metadata from a codebase for visualization.

Produces a codebase-analysis.json with:
  - File tree with types, sizes, line counts
  - Dependency graph from imports/exports
  - Symbol catalog (functions, classes, interfaces)
  - Package metadata and framework detection
  - Language breakdown and metrics

Usage:
    python extract-codebase.py <target_dir> [output_dir]

No external dependencies — uses only the Python standard library.
"""

import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

# ── Directories and files to always skip ─────────────────────────

SKIP_DIRS = {
    "node_modules", ".git", "__pycache__", ".venv", "venv", "env",
    ".next", ".nuxt", "dist", "build", "out", ".output", "target",
    "vendor", ".mypy_cache", ".pytest_cache", ".tox", ".eggs",
    "coverage", ".nyc_output", ".turbo", ".vercel", ".svelte-kit",
    ".parcel-cache", ".cache", ".idea", ".vscode",
}

SKIP_FILES = {
    ".DS_Store", "Thumbs.db", "desktop.ini",
    "package-lock.json", "pnpm-lock.yaml", "yarn.lock",
    "Cargo.lock", "poetry.lock", "Pipfile.lock",
}

BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".svg",
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    ".mp3", ".mp4", ".wav", ".ogg", ".webm",
    ".zip", ".tar", ".gz", ".bz2", ".7z", ".rar",
    ".exe", ".dll", ".so", ".dylib", ".o", ".a",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx",
    ".pyc", ".pyo", ".class", ".jar",
}

# ── Language detection by extension ──────────────────────────────

LANG_MAP = {
    ".js": "JavaScript", ".jsx": "JavaScript",
    ".ts": "TypeScript", ".tsx": "TypeScript",
    ".mjs": "JavaScript", ".cjs": "JavaScript",
    ".mts": "TypeScript", ".cts": "TypeScript",
    ".py": "Python", ".pyw": "Python",
    ".go": "Go",
    ".rs": "Rust",
    ".java": "Java",
    ".kt": "Kotlin", ".kts": "Kotlin",
    ".rb": "Ruby",
    ".php": "PHP",
    ".cs": "C#",
    ".c": "C", ".h": "C",
    ".cpp": "C++", ".hpp": "C++", ".cc": "C++",
    ".swift": "Swift",
    ".html": "HTML", ".htm": "HTML",
    ".css": "CSS", ".scss": "SCSS", ".less": "Less",
    ".json": "JSON",
    ".yaml": "YAML", ".yml": "YAML",
    ".toml": "TOML",
    ".xml": "XML",
    ".md": "Markdown", ".mdx": "MDX",
    ".sql": "SQL",
    ".sh": "Shell", ".bash": "Shell", ".zsh": "Shell",
    ".dockerfile": "Docker",
    ".vue": "Vue",
    ".svelte": "Svelte",
}

# ── Import pattern regexes per language ──────────────────────────

IMPORT_PATTERNS = {
    "JavaScript": [
        re.compile(r'''import\s+.*?from\s+['"]([^'"]+)['"]'''),
        re.compile(r'''require\s*\(\s*['"]([^'"]+)['"]\s*\)'''),
        re.compile(r'''import\s*\(\s*['"]([^'"]+)['"]\s*\)'''),
    ],
    "TypeScript": [
        re.compile(r'''import\s+.*?from\s+['"]([^'"]+)['"]'''),
        re.compile(r'''require\s*\(\s*['"]([^'"]+)['"]\s*\)'''),
        re.compile(r'''import\s*\(\s*['"]([^'"]+)['"]\s*\)'''),
    ],
    "Python": [
        re.compile(r'''^\s*import\s+([\w.]+)''', re.MULTILINE),
        re.compile(r'''^\s*from\s+([\w.]+)\s+import''', re.MULTILINE),
    ],
    "Go": [
        re.compile(r'''"([^"]+)"'''),
    ],
    "Rust": [
        re.compile(r'''use\s+([\w:]+)'''),
        re.compile(r'''extern\s+crate\s+(\w+)'''),
    ],
}

# ── Symbol extraction regexes ────────────────────────────────────

SYMBOL_PATTERNS = {
    "JavaScript": {
        "function": [
            re.compile(r'''(?:export\s+)?(?:async\s+)?function\s+(\w+)'''),
            re.compile(r'''(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\('''),
            re.compile(r'''(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:\w+\s*)?\s*=>\s*'''),
        ],
        "class": [
            re.compile(r'''(?:export\s+)?class\s+(\w+)'''),
        ],
    },
    "TypeScript": {
        "function": [
            re.compile(r'''(?:export\s+)?(?:async\s+)?function\s+(\w+)'''),
            re.compile(r'''(?:const|let|var)\s+(\w+)\s*(?::\s*\w[^=]*)?\s*=\s*(?:async\s+)?\('''),
        ],
        "class": [
            re.compile(r'''(?:export\s+)?class\s+(\w+)'''),
        ],
        "interface": [
            re.compile(r'''(?:export\s+)?interface\s+(\w+)'''),
        ],
        "type": [
            re.compile(r'''(?:export\s+)?type\s+(\w+)\s*[=<]'''),
        ],
    },
    "Python": {
        "function": [
            re.compile(r'''^\s*(?:async\s+)?def\s+(\w+)''', re.MULTILINE),
        ],
        "class": [
            re.compile(r'''^\s*class\s+(\w+)''', re.MULTILINE),
        ],
    },
    "Go": {
        "function": [
            re.compile(r'''func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)\s*\('''),
        ],
        "type": [
            re.compile(r'''type\s+(\w+)\s+(?:struct|interface)'''),
        ],
    },
    "Rust": {
        "function": [
            re.compile(r'''(?:pub\s+)?(?:async\s+)?fn\s+(\w+)'''),
        ],
        "class": [
            re.compile(r'''(?:pub\s+)?struct\s+(\w+)'''),
        ],
        "type": [
            re.compile(r'''(?:pub\s+)?enum\s+(\w+)'''),
            re.compile(r'''(?:pub\s+)?trait\s+(\w+)'''),
        ],
    },
    "Java": {
        "function": [
            re.compile(r'''(?:public|private|protected|static|\s)+[\w<>\[\]]+\s+(\w+)\s*\('''),
        ],
        "class": [
            re.compile(r'''(?:public\s+)?class\s+(\w+)'''),
        ],
        "interface": [
            re.compile(r'''(?:public\s+)?interface\s+(\w+)'''),
        ],
    },
}

# ── Export pattern regexes ───────────────────────────────────────

EXPORT_PATTERNS = {
    "JavaScript": [
        re.compile(r'''export\s+(?:default\s+)?(?:function|class|const|let|var|async)\s+(\w+)'''),
        re.compile(r'''module\.exports\s*='''),
        re.compile(r'''exports\.(\w+)\s*='''),
    ],
    "TypeScript": [
        re.compile(r'''export\s+(?:default\s+)?(?:function|class|const|let|var|async|interface|type|enum)\s+(\w+)'''),
    ],
    "Python": [
        re.compile(r'''__all__\s*=\s*\[([^\]]+)\]'''),
    ],
}

# ── Package manifest detection ───────────────────────────────────

MANIFEST_FILES = {
    "package.json": "npm",
    "requirements.txt": "pip",
    "Pipfile": "pipenv",
    "pyproject.toml": "python",
    "setup.py": "python",
    "go.mod": "go",
    "Cargo.toml": "cargo",
    "Gemfile": "bundler",
    "composer.json": "composer",
    "pom.xml": "maven",
    "build.gradle": "gradle",
    "build.gradle.kts": "gradle",
}

# ── Framework detection patterns ─────────────────────────────────

FRAMEWORK_SIGNATURES = {
    "React": {"deps": ["react", "react-dom"], "files": []},
    "Next.js": {"deps": ["next"], "files": ["next.config.js", "next.config.mjs", "next.config.ts"]},
    "Vue": {"deps": ["vue"], "files": []},
    "Nuxt": {"deps": ["nuxt"], "files": ["nuxt.config.js", "nuxt.config.ts"]},
    "Svelte": {"deps": ["svelte"], "files": []},
    "SvelteKit": {"deps": ["@sveltejs/kit"], "files": ["svelte.config.js"]},
    "Angular": {"deps": ["@angular/core"], "files": ["angular.json"]},
    "Express": {"deps": ["express"], "files": []},
    "Fastify": {"deps": ["fastify"], "files": []},
    "Koa": {"deps": ["koa"], "files": []},
    "Hono": {"deps": ["hono"], "files": []},
    "Django": {"deps": ["django", "Django"], "files": ["manage.py"]},
    "Flask": {"deps": ["flask", "Flask"], "files": []},
    "FastAPI": {"deps": ["fastapi"], "files": []},
    "Spring Boot": {"deps": ["spring-boot-starter"], "files": []},
    "Gin": {"deps": ["github.com/gin-gonic/gin"], "files": []},
    "Actix": {"deps": ["actix-web"], "files": []},
    "Tailwind CSS": {"deps": ["tailwindcss"], "files": ["tailwind.config.js", "tailwind.config.ts"]},
    "Prisma": {"deps": ["prisma", "@prisma/client"], "files": ["prisma/schema.prisma"]},
    "Docker": {"deps": [], "files": ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"]},
}


# ═══════════════════════════════════════════════════════════════════
# Core extraction functions
# ═══════════════════════════════════════════════════════════════════


def should_skip(name, is_dir=False):
    if is_dir:
        return name in SKIP_DIRS or name.startswith(".")
    return name in SKIP_FILES


def detect_language(filepath):
    name = os.path.basename(filepath).lower()
    if name == "dockerfile":
        return "Docker"
    ext = os.path.splitext(filepath)[1].lower()
    return LANG_MAP.get(ext)


def count_lines(filepath):
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return sum(1 for _ in f)
    except (OSError, UnicodeDecodeError):
        return 0


def read_file_safe(filepath, max_bytes=512_000):
    """Read a text file, capping at max_bytes to avoid memory issues."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read(max_bytes)
    except OSError:
        return ""


def is_binary(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    return ext in BINARY_EXTENSIONS


def build_file_tree(root_dir):
    """Walk the directory and build a nested tree structure + flat file list."""
    tree = {"name": os.path.basename(root_dir), "type": "directory", "children": []}
    flat_files = []

    def walk(dir_path, parent_node):
        try:
            entries = sorted(os.listdir(dir_path))
        except PermissionError:
            return

        for entry in entries:
            full_path = os.path.join(dir_path, entry)
            rel_path = os.path.relpath(full_path, root_dir)

            if os.path.isdir(full_path):
                if should_skip(entry, is_dir=True):
                    continue
                child = {"name": entry, "type": "directory", "path": rel_path, "children": []}
                parent_node["children"].append(child)
                walk(full_path, child)
            else:
                if should_skip(entry):
                    continue
                if is_binary(full_path):
                    lang = None
                    lines = 0
                else:
                    lang = detect_language(full_path)
                    lines = count_lines(full_path)

                size = os.path.getsize(full_path)
                file_node = {
                    "name": entry,
                    "type": "file",
                    "path": rel_path,
                    "language": lang,
                    "lines": lines,
                    "size": size,
                }
                parent_node["children"].append(file_node)
                flat_files.append(file_node)

    walk(root_dir, tree)
    return tree, flat_files


def extract_imports(content, language):
    """Extract import targets from source code."""
    patterns = IMPORT_PATTERNS.get(language, [])
    imports = []
    for pattern in patterns:
        for match in pattern.finditer(content):
            imports.append(match.group(1))
    return imports


def extract_exports(content, language):
    """Extract exported symbols from source code."""
    patterns = EXPORT_PATTERNS.get(language, [])
    exports = []
    for pattern in patterns:
        for match in pattern.finditer(content):
            if match.lastindex:
                exports.append(match.group(1))
    return exports


def extract_symbols(content, language):
    """Extract function, class, interface, and type symbols."""
    lang_patterns = SYMBOL_PATTERNS.get(language, {})
    symbols = []
    for kind, patterns in lang_patterns.items():
        seen = set()
        for pattern in patterns:
            for match in pattern.finditer(content):
                name = match.group(1)
                if name not in seen and not name.startswith("_"):
                    seen.add(name)
                    line_num = content[:match.start()].count("\n") + 1
                    symbols.append({
                        "name": name,
                        "kind": kind,
                        "line": line_num,
                    })
    return symbols


def detect_package_metadata(root_dir):
    """Read package manifests and extract dependency info."""
    metadata = {"managers": [], "dependencies": [], "dev_dependencies": []}

    pkg_json_path = os.path.join(root_dir, "package.json")
    if os.path.isfile(pkg_json_path):
        try:
            with open(pkg_json_path, "r", encoding="utf-8") as f:
                pkg = json.load(f)
            metadata["managers"].append("npm")
            metadata["name"] = pkg.get("name", "")
            metadata["version"] = pkg.get("version", "")
            metadata["description"] = pkg.get("description", "")
            metadata["scripts"] = pkg.get("scripts", {})
            metadata["workspaces"] = pkg.get("workspaces", [])
            for dep in pkg.get("dependencies", {}):
                metadata["dependencies"].append(dep)
            for dep in pkg.get("devDependencies", {}):
                metadata["dev_dependencies"].append(dep)
        except (json.JSONDecodeError, OSError):
            pass

    # Scan nested package.json files in monorepo workspaces
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if not should_skip(d, is_dir=True)]
        if dirpath == root_dir:
            continue
        if "package.json" in filenames:
            nested_path = os.path.join(dirpath, "package.json")
            try:
                with open(nested_path, "r", encoding="utf-8") as f:
                    nested_pkg = json.load(f)
                for dep in nested_pkg.get("dependencies", {}):
                    if dep not in metadata["dependencies"]:
                        metadata["dependencies"].append(dep)
                for dep in nested_pkg.get("devDependencies", {}):
                    if dep not in metadata["dev_dependencies"]:
                        metadata["dev_dependencies"].append(dep)
            except (json.JSONDecodeError, OSError):
                pass

    req_path = os.path.join(root_dir, "requirements.txt")
    if os.path.isfile(req_path):
        metadata["managers"].append("pip")
        content = read_file_safe(req_path)
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("-"):
                dep_name = re.split(r'[>=<!\[]', line)[0].strip()
                if dep_name:
                    metadata["dependencies"].append(dep_name)

    pyproject_path = os.path.join(root_dir, "pyproject.toml")
    if os.path.isfile(pyproject_path):
        metadata["managers"].append("python")

    go_mod_path = os.path.join(root_dir, "go.mod")
    if os.path.isfile(go_mod_path):
        metadata["managers"].append("go")
        content = read_file_safe(go_mod_path)
        for match in re.finditer(r'^\s+(\S+)\s+v', content, re.MULTILINE):
            metadata["dependencies"].append(match.group(1))

    cargo_path = os.path.join(root_dir, "Cargo.toml")
    if os.path.isfile(cargo_path):
        metadata["managers"].append("cargo")

    return metadata


def detect_frameworks(root_dir, metadata, flat_files):
    """Detect frameworks by checking dependencies and config files."""
    detected = []
    all_deps = set(metadata.get("dependencies", []) + metadata.get("dev_dependencies", []))
    all_file_names = {f["path"] for f in flat_files} | {f["name"] for f in flat_files}

    for framework, sigs in FRAMEWORK_SIGNATURES.items():
        dep_match = any(d in all_deps for d in sigs["deps"])
        file_match = any(f in all_file_names for f in sigs["files"])
        if dep_match or file_match:
            detected.append(framework)

    return detected


def build_dependency_graph(root_dir, flat_files):
    """Build a module dependency graph from import statements."""
    graph = {"nodes": [], "edges": []}
    node_set = set()

    for file_info in flat_files:
        lang = file_info.get("language")
        if not lang or lang in ("JSON", "YAML", "TOML", "XML", "Markdown", "MDX"):
            continue

        rel_path = file_info["path"]
        full_path = os.path.join(root_dir, rel_path)
        content = read_file_safe(full_path)
        if not content:
            continue

        if rel_path not in node_set:
            node_set.add(rel_path)
            graph["nodes"].append({"id": rel_path, "language": lang, "lines": file_info["lines"]})

        imports = extract_imports(content, lang)
        for imp in imports:
            is_relative = imp.startswith(".") or imp.startswith("/")
            graph["edges"].append({
                "from": rel_path,
                "to": imp,
                "is_external": not is_relative,
            })

    return graph


def build_symbol_catalog(root_dir, flat_files):
    """Extract all symbols (functions, classes, etc.) across the codebase."""
    catalog = []

    for file_info in flat_files:
        lang = file_info.get("language")
        if not lang or lang in ("JSON", "YAML", "TOML", "XML", "Markdown", "MDX", "HTML", "CSS", "SCSS", "Less"):
            continue

        full_path = os.path.join(root_dir, file_info["path"])
        content = read_file_safe(full_path)
        if not content:
            continue

        symbols = extract_symbols(content, lang)
        exports = extract_exports(content, lang)
        export_set = set(exports)

        for sym in symbols:
            sym["file"] = file_info["path"]
            sym["exported"] = sym["name"] in export_set
            catalog.append(sym)

    return catalog


def compute_metrics(flat_files, dependency_graph, symbol_catalog):
    """Compute summary metrics for the codebase."""
    lang_counts = defaultdict(lambda: {"files": 0, "lines": 0})
    total_lines = 0
    total_size = 0

    for f in flat_files:
        lang = f.get("language") or "Other"
        lang_counts[lang]["files"] += 1
        lang_counts[lang]["lines"] += f["lines"]
        total_lines += f["lines"]
        total_size += f["size"]

    symbol_counts = defaultdict(int)
    for sym in symbol_catalog:
        symbol_counts[sym["kind"]] += 1

    internal_edges = [e for e in dependency_graph["edges"] if not e["is_external"]]
    external_deps = {e["to"] for e in dependency_graph["edges"] if e["is_external"]}

    return {
        "total_files": len(flat_files),
        "total_lines": total_lines,
        "total_size_bytes": total_size,
        "languages": dict(lang_counts),
        "symbol_counts": dict(symbol_counts),
        "internal_connections": len(internal_edges),
        "external_dependencies": len(external_deps),
    }


def find_entry_points(root_dir, flat_files, metadata):
    """Heuristically identify entry point files."""
    entry_points = []
    entry_patterns = [
        "index.ts", "index.js", "index.tsx", "index.jsx",
        "main.ts", "main.js", "main.py", "main.go", "main.rs",
        "app.ts", "app.js", "app.py",
        "server.ts", "server.js", "server.py",
        "manage.py",
    ]
    scripts = metadata.get("scripts", {})
    if "start" in scripts or "dev" in scripts:
        entry_points.append({"type": "npm_script", "scripts": scripts})

    for f in flat_files:
        name = os.path.basename(f["path"])
        if name in entry_patterns:
            entry_points.append({"type": "file", "path": f["path"]})

    return entry_points


# ═══════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════


def extract_codebase(target_dir):
    """Run the full extraction pipeline and return the analysis dict."""
    target_dir = os.path.abspath(target_dir)

    print(f"  Scanning: {target_dir}")
    file_tree, flat_files = build_file_tree(target_dir)
    print(f"  Found {len(flat_files)} files")

    print("  Extracting package metadata...")
    metadata = detect_package_metadata(target_dir)

    print("  Detecting frameworks...")
    frameworks = detect_frameworks(target_dir, metadata, flat_files)

    print("  Building dependency graph...")
    dep_graph = build_dependency_graph(target_dir, flat_files)

    print("  Extracting symbols...")
    symbols = build_symbol_catalog(target_dir, flat_files)

    print("  Computing metrics...")
    metrics = compute_metrics(flat_files, dep_graph, symbols)

    print("  Finding entry points...")
    entry_points = find_entry_points(target_dir, flat_files, metadata)

    return {
        "project_root": target_dir,
        "project_name": metadata.get("name") or os.path.basename(target_dir),
        "description": metadata.get("description", ""),
        "file_tree": file_tree,
        "files": flat_files,
        "package_metadata": metadata,
        "frameworks": frameworks,
        "dependency_graph": dep_graph,
        "symbols": symbols,
        "entry_points": entry_points,
        "metrics": metrics,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract-codebase.py <target_dir> [output_dir]")
        sys.exit(1)

    target = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    if not os.path.isdir(target):
        print(f"Error: '{target}' is not a directory.")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    print("")
    print("╔══════════════════════════════════════╗")
    print("║     Codebase Structure Extraction     ║")
    print("╚══════════════════════════════════════╝")
    print("")

    analysis = extract_codebase(target)

    output_path = os.path.join(output_dir, "codebase-analysis.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2, default=str)

    print("")
    print(f"  Analysis written to: {output_path}")
    print(f"  Files:       {analysis['metrics']['total_files']}")
    print(f"  Lines:       {analysis['metrics']['total_lines']}")
    print(f"  Languages:   {', '.join(analysis['metrics']['languages'].keys())}")
    print(f"  Frameworks:  {', '.join(analysis['frameworks']) or 'none detected'}")
    print(f"  Symbols:     {sum(analysis['metrics']['symbol_counts'].values())}")
    print("")
