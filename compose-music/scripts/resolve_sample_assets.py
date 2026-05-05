#!/usr/bin/env python3
"""Resolve user sample asset references without embedding local paths in specs."""

import argparse
import json
import os
import pathlib
import re
import sys


URI_RE = re.compile(r"^[a-z][a-z0-9+.-]*://", re.IGNORECASE)


def _reject_unsafe_path_text(value):
    text = str(value)
    if "\x00" in text or any(ord(char) < 32 for char in text):
        raise ValueError("sample path must not contain control characters")
    if URI_RE.match(text):
        raise ValueError("sample path must not be a URI")


def _canonical_path(value):
    _reject_unsafe_path_text(value)
    expanded = os.path.expandvars(os.path.expanduser(str(value)))
    _reject_unsafe_path_text(expanded)
    return pathlib.Path(expanded).resolve(strict=False)


def _is_relative_to(path, root):
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _load_manifest(path):
    manifest_path = pathlib.Path(path).expanduser()
    with manifest_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if isinstance(data, dict) and "sample_assets" in data:
        assets = data["sample_assets"]
    elif isinstance(data, list):
        assets = data
    elif isinstance(data, dict):
        assets = []
        for asset_id, value in data.items():
            if isinstance(value, dict):
                assets.append({"id": asset_id, **value})
    else:
        raise ValueError("manifest must be an array, object, or contain sample_assets")
    if not isinstance(assets, list):
        raise ValueError("manifest sample_assets must be an array")
    return assets


def _find_asset(assets, asset_id):
    for asset in assets:
        if isinstance(asset, dict) and asset.get("id") == asset_id:
            return asset
    raise ValueError(f"asset id {asset_id!r} was not found")


def resolve_asset(asset, check_files=False):
    """Resolve one sample asset object to a canonical absolute path."""
    if not isinstance(asset, dict):
        raise ValueError("asset must be an object")
    if not asset.get("id"):
        raise ValueError("asset.id is required")

    root = None
    if "path_ref" in asset:
        env_name = asset["path_ref"]
        if env_name not in os.environ:
            raise ValueError(f"environment variable {env_name} is not set")
        absolute_path = _canonical_path(os.environ[env_name])
    elif "root_env" in asset and "relative_path" in asset:
        env_name = asset["root_env"]
        if env_name not in os.environ:
            raise ValueError(f"environment variable {env_name} is not set")
        root = _canonical_path(os.environ[env_name])
        relative_path = asset["relative_path"]
        _reject_unsafe_path_text(relative_path)
        if pathlib.PurePath(relative_path).is_absolute() or ".." in pathlib.PurePath(relative_path).parts:
            raise ValueError("relative_path must stay inside root_env")
        absolute_path = (root / relative_path).resolve(strict=False)
    elif "path" in asset:
        absolute_path = _canonical_path(asset["path"])
    else:
        raise ValueError("asset must define path_ref, root_env plus relative_path, or path")

    if root is not None and not _is_relative_to(absolute_path, root):
        raise ValueError("resolved sample path must stay inside root_env")
    if check_files and not absolute_path.is_file():
        raise ValueError(f"sample file does not exist: {absolute_path}")

    resolved = {
        "id": asset["id"],
        "absolute_path": str(absolute_path),
    }
    for key in ("source", "original_bpm", "bars", "trim", "rights_status"):
        if key in asset:
            resolved[key] = asset[key]
    return resolved


def main(argv=None):
    parser = argparse.ArgumentParser(description="Resolve compose-music sample asset references.")
    parser.add_argument("--manifest", help="Path to sample_assets JSON manifest.")
    parser.add_argument("--asset-id", required=True, help="Sample asset id to resolve.")
    parser.add_argument("--check-files", action="store_true", help="Require the resolved file to exist.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    args = parser.parse_args(argv)

    try:
        if not args.manifest:
            raise ValueError("--manifest is required")
        asset = resolve_asset(_find_asset(_load_manifest(args.manifest), args.asset_id), check_files=args.check_files)
        output = {"ok": True, "asset": asset}
    except Exception as exc:
        output = {"ok": False, "error": str(exc)}
        print(json.dumps(output, indent=2 if args.pretty else None), file=sys.stderr)
        return 1

    print(json.dumps(output, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
