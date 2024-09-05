from pathlib import Path
from typing import List, Dict, Any, Optional
import json


class RadkfileRadicalInfo:
    def __init__(self, data: Dict[str, Any]):
        self.stroke_count: int = data["strokeCount"]
        self.code: Optional[str] = data.get("code")
        self.kanji: List[str] = data["kanji"]

    def to_dict(self):
        return {
            "strokeCount": self.stroke_count,
            "code": self.code,
            "kanji": self.kanji,
        }


class Radkfile:
    def __init__(self, data: Dict[str, Any]):
        self.version: str = data["version"]
        self.radicals: Dict[str, RadkfileRadicalInfo] = {
            radical: RadkfileRadicalInfo(info)
            for radical, info in data["radicals"].items()
        }

    def __repr__(self):
        return f"Radkfile(version={self.version}, radicals_count={len(self.radicals)})"

    def to_dict(self):
        return {
            "version": self.version,
            "radicals": {
                radical: info.to_dict() for radical, info in self.radicals.items()
            },
        }


def load_radkfile() -> Radkfile:
    current_dir = Path(__file__).parent
    json_files = list(current_dir.glob("radkfile-*.json"))
    if not json_files:
        raise FileNotFoundError(f"No radkfile-*.json file found in {current_dir}")
    json_file = json_files[0]  # Use the first matching file
    with open(json_file, "r", encoding="utf-8") as f:
        return Radkfile(json.load(f))


def write_radkfile_to_json(radkfile: Radkfile, output_file: str):
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(radkfile.to_dict(), f, ensure_ascii=False, indent=2)
