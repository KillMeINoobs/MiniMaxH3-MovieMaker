"""Regenerate public schemas from the bundled declarative source; no network."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from kmin_video_director.contracts.specs import SCHEMAS

if __name__ == "__main__":
    folder = ROOT / "schemas"
    folder.mkdir(exist_ok=True)
    for name, schema in SCHEMAS.items():
        (folder / (name + ".schema.json")).write_text(
            json.dumps(schema, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
