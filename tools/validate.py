"""Validate the OpenDXL API schema, and every example against it.

    pip install jsonschema pyyaml
    python tools/validate.py

Two checks, and the first one is the reason this script exists at all:

1. The schema is itself a valid JSON Schema 2020-12 document, and every
   reference in it resolves. Between 2019 and 2026 the schema pointed at
   `http://swagger.io/v2/schema.json`, which stopped existing when the
   specification moved to the OpenAPI Initiative. Nothing noticed, because
   nothing ever tried to resolve it.

2. Every example under examples/ validates against the schema.

The OpenAPI schema is resolved from the copy in schemas/vendor/ rather than
over the network. That is not only about working offline: a validation whose
result depends on a third-party host is a validation that can change its mind
without anyone editing anything. `--online` fetches it instead, which is how
you check that the vendored copy still matches what the OpenAPI Initiative
publishes.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - the message is the point
    print("pyyaml is required: pip install pyyaml", file=sys.stderr)
    raise SystemExit(2)

try:
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource
except ImportError:  # pragma: no cover
    print("jsonschema >= 4.18 is required: pip install jsonschema", file=sys.stderr)
    raise SystemExit(2)

REPO = Path(__file__).resolve().parent.parent
SCHEMA = REPO / "schemas" / "v0.1" / "schema.json"
VENDOR = REPO / "schemas" / "vendor"
EXAMPLES = REPO / "examples"


def load_example(path: Path) -> object:
    text = path.read_text(encoding="utf-8")
    if path.suffix in (".yaml", ".yml"):
        return yaml.safe_load(text)
    return json.loads(text)


def build_registry(online: bool) -> Registry:
    """Every external schema the document references, keyed by its $id."""
    registry = Registry()
    for path in sorted(VENDOR.glob("*.json")):
        document = json.loads(path.read_text(encoding="utf-8"))
        uri = document.get("$id")
        if not uri:
            print("  %s has no $id, skipping" % path.name)
            continue
        if online:
            with urllib.request.urlopen(uri, timeout=30) as response:
                fetched = json.loads(response.read().decode("utf-8"))
            if fetched != document:
                print("  %s differs from %s" % (path.name, uri))
                print("  the vendored copy is out of date, or the published one changed")
                raise SystemExit(1)
            print("  %s matches %s" % (path.name, uri))
        else:
            print("  %s -> %s" % (path.name, uri))
        registry = registry.with_resource(uri, Resource.from_contents(document))
    return registry


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--online", action="store_true",
                        help="check the vendored schemas against the published ones")
    args = parser.parse_args()

    print("[1/3] external schemas")
    registry = build_registry(args.online)

    print("[2/3] the schema itself")
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, registry=registry)
    # check_schema does not resolve $refs, so walk them: an unresolvable
    # reference is exactly the failure this repository already lived through.
    unresolved = []
    for error in validator.iter_errors({}):
        pass  # forces the resolver to touch every reference reachable from the root
    for ref in sorted({r for r in find_refs(schema)}):
        if ref.startswith("#"):
            continue
        try:
            validator._resolver.lookup(ref)
        except Exception as problem:  # noqa: BLE001 - report, do not classify
            unresolved.append("%s (%s)" % (ref, type(problem).__name__))
    if unresolved:
        print("  unresolved references:")
        for ref in unresolved:
            print("    %s" % ref)
        return 1
    print("  valid, and every reference resolves")

    print("[3/3] examples")
    failures = 0
    files = sorted(p for p in EXAMPLES.rglob("*") if p.suffix in (".json", ".yaml", ".yml"))
    if not files:
        print("  no examples found")
        return 1
    for path in files:
        errors = sorted(validator.iter_errors(load_example(path)), key=lambda e: e.path)
        if errors:
            failures += 1
            print("  %s: %d problem(s)" % (path.relative_to(REPO), len(errors)))
            for error in errors[:5]:
                where = "/".join(str(p) for p in error.absolute_path) or "<root>"
                print("    %s: %s" % (where, error.message))
        else:
            print("  %s: ok" % path.relative_to(REPO))
    return 1 if failures else 0


def find_refs(node: object) -> list[str]:
    """Every $ref value in the document, in document order."""
    found: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "$ref" and isinstance(value, str):
                found.append(value)
            else:
                found.extend(find_refs(value))
    elif isinstance(node, list):
        for item in node:
            found.extend(find_refs(item))
    return found


if __name__ == "__main__":
    raise SystemExit(main())
