#!/usr/bin/env python3
"""Config utilities for merging YAML and deriving registry names."""

from __future__ import annotations

import argparse
import sys
from typing import Any
from urllib.parse import urlparse

import yaml


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

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
