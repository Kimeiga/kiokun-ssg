from pathlib import Path
from typing import List, Dict, Any
import json


class Kradfile:
    def __init__(self, data: Dict[str, Any]):
        self.version: str = data["version"]
        self.kanji: Dict[str, List[str]] = data["kanji"]

    def __repr__(self):
        return f"Kradfile(version={self.version}, kanji_count={len(self.kanji)})"

    def to_dict(self):
        return {"version": self.version, "kanji": self.kanji}


def load_kradfile() -> Kradfile:
    current_dir = Path(__file__).parent
    json_files = list(current_dir.glob("kradfile-*.json"))
    if not json_files:
        raise FileNotFoundError(f"No kradfile-*.json file found in {current_dir}")
    json_file = json_files[0]  # Use the first matching file
    with open(json_file, "r", encoding="utf-8") as f:
        return Kradfile(json.load(f))


def write_kradfile_to_json(kradfile: Kradfile, output_file: str):
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(kradfile.to_dict(), f, ensure_ascii=False, indent=2)
