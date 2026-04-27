#!/usr/bin/env python3
"""Render a blog folder's _render/body.html (produced by blogpost-html-renderer)
into a final index.html using the Jinja2 layout template.

Usage:
    python render.py <blog_folder>

Inputs (read from <blog_folder>):
    - _render/body.html   (enriched HTML body fragment from html-renderer agent)
    - _render/toc.json    (TOC outline from html-renderer agent)
    - metadata.json       (title/tags/date/images mapping)

Output:
    - index.html          (final blog page wrapping body in templates/blog.html.j2)

The script does NOT do its own markdown-to-HTML conversion. The html-renderer
agent is responsible for the body markup. This script is purely the
layout-wrapping driver, so it stays small and testable.
"""
import argparse
import json
import os
import sys
from pathlib import Path

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
except ImportError:
    sys.stderr.write(
        "ERROR: jinja2 not installed. Install with: pip install jinja2\n"
    )
    sys.exit(2)


PLUGIN_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = PLUGIN_ROOT / "templates"


def load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"WARN: {path} is not valid JSON ({exc}); using default.\n")
        return default


def render(blog_folder: Path) -> Path:
    if not blog_folder.exists() or not blog_folder.is_dir():
        sys.stderr.write(f"ERROR: blog folder does not exist: {blog_folder}\n")
        sys.exit(1)

    body_path = blog_folder / "_render" / "body.html"
    toc_path = blog_folder / "_render" / "toc.json"
    meta_path = blog_folder / "metadata.json"

    if not body_path.exists():
        sys.stderr.write(
            f"ERROR: {body_path} missing. Run blogpost-html-renderer first.\n"
        )
        sys.exit(1)

    body_html = body_path.read_text(encoding="utf-8")
    toc = load_json(toc_path, default=[])
    metadata = load_json(meta_path, default={})

    title = metadata.get("topic") or metadata.get("title") or "(제목 없음)"
    tags = metadata.get("tags", []) or []
    created_at = metadata.get("created_at", "")

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(enabled_extensions=("j2",), default=False),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("blog.html.j2")

    output = template.render(
        title=title,
        tags=tags,
        created_at=created_at,
        toc=toc,
        body=body_html,
        metadata=metadata,
    )

    out_path = blog_folder / "index.html"
    out_path.write_text(output, encoding="utf-8")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render blog folder to index.html via Jinja layout."
    )
    parser.add_argument("blog_folder", help="Absolute path to the per-blog folder.")
    args = parser.parse_args()

    blog_folder = Path(args.blog_folder).expanduser().resolve()
    out_path = render(blog_folder)
    print(f"OK: wrote {out_path} ({out_path.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
