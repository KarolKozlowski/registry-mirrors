#!/usr/bin/env python3
"""Config utilities for merging YAML and deriving registry names."""

from __future__ import annotations

import argparse
import sys
from typing import Any
from urllib.parse import urlparse
from pathlib import Path
import re

import yaml
from jinja2 import Environment, FileSystemLoader


def deep_merge(base: Any, override: Any) -> Any:
    if isinstance(base, dict) and isinstance(override, dict):
        merged = dict(base)
        for key, value in override.items():
            if key in merged:
                merged[key] = deep_merge(merged[key], value)
            else:
                merged[key] = value
        return merged
    return override


def load_yaml(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def dump_yaml(data: Any, path: str) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, default_flow_style=False, sort_keys=False)


def load_config(path: str) -> dict[str, Any]:
    data = load_yaml(path)
    if not isinstance(data, dict):
        raise ValueError("Config must be a mapping")
    common = data.get("common")
    registries = data.get("registries")
    if not isinstance(common, dict) or not isinstance(registries, dict):
        raise ValueError("Config must contain 'common' and 'registries' mappings")
    return {"common": common, "registries": registries}


def cmd_merge(args: argparse.Namespace) -> int:
    data = load_config(args.config)
    registry = data["registries"].get(args.registry)
    if not isinstance(registry, dict):
        raise ValueError(f"Registry '{args.registry}' not found")
    merged = deep_merge(data["common"], registry)
    dump_yaml(merged, args.output)
    return 0


def _hostname_from_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.netloc:
        host = parsed.netloc
    else:
        host = parsed.path
    host = host.split("/")[0]
    host = host.split(":")[0]
    return host


def cmd_registry_name(args: argparse.Namespace) -> int:
    data = load_config(args.config)
    registry = data["registries"].get(args.registry)
    url = (
        registry.get("proxy", {}).get("remoteurl")
        if isinstance(registry, dict)
        else None
    )
    if not url:
        return 1
    host = _hostname_from_url(url)
    parts = host.split(".") if host else []
    if not parts:
        return 1
    n = max(1, int(args.parts))
    if len(parts) <= n:
        name = ".".join(parts)
    else:
        name = ".".join(parts[-n:])
    print(name)
    return 0


def cmd_list_registries(args: argparse.Namespace) -> int:
    data = load_config(args.config)
    for name in sorted(data["registries"].keys()):
        print(name)
    return 0


def cmd_build_config(args: argparse.Namespace) -> int:
    common = load_yaml(args.common)
    if not isinstance(common, dict):
        raise ValueError("Common config must be a mapping")

    custom_dir = Path(args.custom_dir)
    registries: dict[str, Any] = {}
    for path in sorted(custom_dir.glob("*.yml")):
        data = load_yaml(str(path))
        if not isinstance(data, dict):
            raise ValueError(f"Custom config must be a mapping: {path}")
        registries[path.stem] = data

    combined = {"common": common, "registries": registries}
    dump_yaml(combined, args.output)
    return 0


def cmd_render_compose(args: argparse.Namespace) -> int:
    template_path = Path(args.template)
    cfg_root = load_yaml(args.config)
    if not isinstance(cfg_root, dict):
        raise ValueError("Config must be a mapping")
    env = Environment(
        loader=FileSystemLoader(str(template_path.parent)),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["regex_replace"] = lambda value, pattern, repl: re.sub(pattern, repl, value)
    template = env.get_template(template_path.name)
    rendered = template.render(config_file=args.config, cfg_root=cfg_root)
    with open(args.output, "w", encoding="utf-8") as handle:
        handle.write(rendered)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Registry config utilities")
    sub = parser.add_subparsers(dest="command", required=True)

    merge = sub.add_parser("merge", help="Merge common config with a registry override")
    merge.add_argument("config", help="Path to config.yml")
    merge.add_argument("registry", help="Registry key")
    merge.add_argument("-o", "--output", required=True, help="Output file")
    merge.set_defaults(func=cmd_merge)

    reg = sub.add_parser("registry-name", help="Derive registry name from remoteurl")
    reg.add_argument("config", help="Path to config.yml")
    reg.add_argument("registry", help="Registry key")
    reg.add_argument("--parts", default=2, type=int, help="Number of domain parts")
    reg.set_defaults(func=cmd_registry_name)

    lst = sub.add_parser("list-registries", help="List registry keys")
    lst.add_argument("config", help="Path to config.yml")
    lst.set_defaults(func=cmd_list_registries)

    build = sub.add_parser("build-config", help="Build combined config.yml from src")
    build.add_argument("common", help="Path to common YAML")
    build.add_argument("custom_dir", help="Path to custom YAML directory")
    build.add_argument("-o", "--output", required=True, help="Output file")
    build.set_defaults(func=cmd_build_config)

    render = sub.add_parser("render-compose", help="Render docker-compose from Jinja template")
    render.add_argument("template", help="Path to docker-compose.yml.j2")
    render.add_argument("config", help="Path to config.yml")
    render.add_argument("-o", "--output", required=True, help="Output file")
    render.set_defaults(func=cmd_render_compose)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
