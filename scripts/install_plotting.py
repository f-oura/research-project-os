#!/usr/bin/env python3
"""Install or check custom-plot without changing research code or installing Python."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from plotting import inspect, install
from record_utils import load_profile


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', type=Path)
    parser.add_argument('--revision', help='full pinned custom-plot SHA; default: bundled pin')
    parser.add_argument('--profile', type=Path)
    parser.add_argument('--check', action='store_true', help='read-only dependency and runtime check')
    parser.add_argument('--python', default=sys.executable, help='existing plotting interpreter to check')
    args = parser.parse_args()
    profile = load_profile(args.profile.resolve()) if args.profile else {}
    try:
        if args.check:
            result = inspect(args.path.resolve(), profile, args.python)
        else:
            revision = args.revision or json.loads((Path(__file__).resolve().parents[1] / 'config/plotting.json').read_text())['revision']
            result = install(args.path, revision, profile)
        print(json.dumps(result, indent=2))
        return 0 if result['status'] == 'PASS' else 2
    except (OSError, ValueError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
