# File: data/jp/kanjidic/types.py

import json
from pathlib import Path
from typing import Dict, Any, List, Optional


class Kanjidic2Codepoint:
    def __init__(self, data: Dict[str, Any]):
        self.type: str = data["type"]
        self.value: str = data["value"]

    def to_dict(self):
        return json.loads(json.dumps(self.__dict__))


class Kanjidic2Radical:
    def __init__(self, data: Dict[str, Any]):
        self.type: str = data["type"]
        self.value: int = data["value"]

    def to_dict(self):
        return json.loads(json.dumps(self.__dict__))


class Kanjidic2Variant:
    def __init__(self, data: Dict[str, Any]):
        self.type: str = data["type"]
        self.value: str = data["value"]

    def to_dict(self):
        return json.loads(json.dumps(self.__dict__))


class Kanjidic2Misc:
    def __init__(self, data: Dict[str, Any]):
        self.grade: Optional[int] = data.get("grade")
        self.stroke_counts: List[int] = data["strokeCounts"]
        self.variants: List[Kanjidic2Variant] = [
            Kanjidic2Variant(v) for v in data.get("variants", [])
        ]
        self.frequency: Optional[int] = data.get("frequency")
        self.radical_names: List[str] = data.get("radicalNames", [])
        self.jlpt_level: Optional[int] = data.get("jlptLevel")

    def to_dict(self):
        d = {k: v for k, v in self.__dict__.items() if v is not None}
        d["variants"] = [v.to_dict() for v in self.variants]
        return json.loads(json.dumps(d))


class Kanjidic2DictionaryReference:
    def __init__(self, data: Dict[str, Any]):
        self.type: str = data["type"]
        self.morohashi: Optional[Dict[str, int]] = data.get("morohashi")
        self.value: str = data["value"]

    def to_dict(self):
        return json.loads(
            json.dumps({k: v for k, v in self.__dict__.items() if v is not None})
        )


class Kanjidic2QueryCode:
    def __init__(self, data: Dict[str, Any]):
        self.type: str = data["type"]
        self.skip_misclassification: Optional[str] = data.get("skipMisclassification")
        self.value: str = data["value"]

    def to_dict(self):
        return json.loads(
            json.dumps({k: v for k, v in self.__dict__.items() if v is not None})
        )


class Kanjidic2Reading:
    def __init__(self, data: Dict[str, Any]):
        self.type: str = data["type"]
        self.on_type: Optional[str] = data.get("onType")
        self.status: Optional[str] = data.get("status")
        self.value: str = data["value"]

    def to_dict(self):
        return json.loads(
            json.dumps({k: v for k, v in self.__dict__.items() if v is not None})
        )


class Kanjidic2Meaning:
    def __init__(self, data: Dict[str, Any]):
        self.lang: str = data["lang"]
        self.value: str = data["value"]

    def to_dict(self):
        return json.loads(json.dumps(self.__dict__))


class Kanjidic2ReadingMeaning:
    def __init__(self, data: Dict[str, Any]):
        group = data["groups"][0]  # We're assuming there's always exactly one group
        self.readings: List[Kanjidic2Reading] = [
            Kanjidic2Reading(r) for r in group["readings"]
        ]
        self.meanings: List[Kanjidic2Meaning] = [
            Kanjidic2Meaning(m) for m in group["meanings"]
        ]
        self.nanori: List[str] = data.get("nanori", [])

        # Add separate lists for onyomi and kunyomi
        self.onyomi: List[str] = [r.value for r in self.readings if r.type == "ja_on"]
        self.kunyomi: List[str] = [r.value for r in self.readings if r.type == "ja_kun"]

    def to_dict(self):
        return {
            "readings": [r.to_dict() for r in self.readings],
            "meanings": [m.to_dict() for m in self.meanings],
            "nanori": self.nanori,
            "onyomi": self.onyomi,
            "kunyomi": self.kunyomi,
        }


class Kanjidic2Character:
    def __init__(self, data: Dict[str, Any]):
        self.literal: str = data["literal"]
        self.codepoints: List[Kanjidic2Codepoint] = [
            Kanjidic2Codepoint(c) for c in data["codepoints"]
        ]
        self.radicals: List[Kanjidic2Radical] = [
            Kanjidic2Radical(r) for r in data["radicals"]
        ]
        self.misc: Kanjidic2Misc = Kanjidic2Misc(data["misc"])
        self.dictionary_references: List[Kanjidic2DictionaryReference] = [
            Kanjidic2DictionaryReference(d) for d in data["dictionaryReferences"]
        ]
        self.query_codes: List[Kanjidic2QueryCode] = [
            Kanjidic2QueryCode(q) for q in data["queryCodes"]
        ]
        self.reading_meaning: Optional[Kanjidic2ReadingMeaning] = (
            Kanjidic2ReadingMeaning(data["readingMeaning"])
            if data.get("readingMeaning")
            else None
        )

    def __repr__(self):
        return f"Kanjidic2Character(literal={self.literal})"

    def to_dict(self):
        d = {
            "literal": self.literal,
            "codepoints": [c.to_dict() for c in self.codepoints],
            "radicals": [r.to_dict() for r in self.radicals],
            "misc": self.misc.to_dict(),
            "dictionary_references": [d.to_dict() for d in self.dictionary_references],
            "query_codes": [q.to_dict() for q in self.query_codes],
        }
        if self.reading_meaning:
            d["reading_meaning"] = self.reading_meaning.to_dict()
        return json.loads(json.dumps(d))


class Kanjidic2:
    def __init__(self, data: Dict[str, Any]):
        self.characters: Dict[str, Kanjidic2Character] = {
            char_data["literal"]: Kanjidic2Character(char_data)
            for char_data in data["characters"]
        }

    def __repr__(self):
        return f"Kanjidic2(characters_count={len(self.characters)})"

    def get_character(self, kanji: str) -> Optional[Kanjidic2Character]:
        return self.characters.get(kanji)

    def to_dict(self):
        return {
            "fileVersion": self.file_version,
            "databaseVersion": self.database_version,
            "date": self.date,
            "characters": {k: v.to_dict() for k, v in self.characters.items()},
        }


def load_kanjidic() -> Kanjidic2:
    current_dir = Path(__file__).parent
    json_files = list(current_dir.glob("kanjidic2-*.json"))
    if not json_files:
        raise FileNotFoundError(f"No kanjidic2-*.json file found in {current_dir}")
    json_file = json_files[0]  # Use the first matching file
    with open(json_file, "r", encoding="utf-8") as f:
        return Kanjidic2(json.load(f))
