import json
import os
from pathlib import Path
from typing import List, Optional, Dict, Any


class KanjiElement:
    def __init__(self, data: Dict[str, Any]):
        self.common: Optional[bool] = (
            data.get("common") if data.get("common") is not None else None
        )
        self.text: Optional[str] = data.get("text") if data.get("text") else None
        self.tags: Optional[List[str]] = data.get("tags") if data.get("tags") else None

    def __repr__(self):
        return f"KanjiElement(text={self.text}, common={self.common}, tags={self.tags})"

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}


class ReadingElement:
    def __init__(self, data: Dict[str, Any]):
        self.common: Optional[bool] = (
            data.get("common") if data.get("common") is not None else None
        )
        self.text: Optional[str] = data.get("text") if data.get("text") else None
        self.tags: Optional[List[str]] = data.get("tags") if data.get("tags") else None
        self.applies_to_kanji: Optional[List[str]] = (
            data.get("appliesToKanji") if data.get("appliesToKanji") else None
        )

    def __repr__(self):
        return f"ReadingElement(text={self.text}, common={self.common}, tags={self.tags}, applies_to_kanji={self.applies_to_kanji})"

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}


class Gloss:
    def __init__(self, data: Dict[str, Any]):
        self.lang: Optional[str] = data.get("lang") if data.get("lang") else None
        self.gender: Optional[str] = data.get("gender") if data.get("gender") else None
        self.type: Optional[str] = data.get("type") if data.get("type") else None
        self.text: Optional[str] = data.get("text") if data.get("text") else None

    def __repr__(self):
        return f"Gloss(text={self.text}, lang={self.lang}, gender={self.gender}, type={self.type})"

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}


class Sense:
    def __init__(self, data: Dict[str, Any]):
        self.part_of_speech: Optional[List[str]] = (
            data.get("partOfSpeech") if data.get("partOfSpeech") else None
        )
        self.applies_to_kanji: Optional[List[str]] = (
            data.get("appliesToKanji") if data.get("appliesToKanji") else None
        )
        self.applies_to_kana: Optional[List[str]] = (
            data.get("appliesToKana") if data.get("appliesToKana") else None
        )
        self.related: Optional[List[str]] = (
            data.get("related") if data.get("related") else None
        )
        self.antonym: Optional[List[str]] = (
            data.get("antonym") if data.get("antonym") else None
        )
        self.field: Optional[List[str]] = (
            data.get("field") if data.get("field") else None
        )
        self.dialect: Optional[List[str]] = (
            data.get("dialect") if data.get("dialect") else None
        )
        self.misc: Optional[List[str]] = data.get("misc") if data.get("misc") else None
        self.info: Optional[List[str]] = data.get("info") if data.get("info") else None
        self.language_source: Optional[List[Dict[str, Any]]] = (
            data.get("languageSource") if data.get("languageSource") else None
        )
        self.gloss: Optional[List[Gloss]] = (
            [Gloss(g) for g in data.get("gloss")] if data.get("gloss") else None
        )

    def __repr__(self):
        return f"Sense(part_of_speech={self.part_of_speech}, gloss={self.gloss})"

    def to_dict(self):
        d = {k: v for k, v in self.__dict__.items() if v is not None}
        if self.gloss:
            d["gloss"] = [g.to_dict() for g in self.gloss]
        return d


class JMdictEntry:
    def __init__(self, data: Dict[str, Any]):
        self.id: str = data["id"]
        self.kanji: Optional[List[KanjiElement]] = (
            [KanjiElement(k) for k in data.get("kanji")] if data.get("kanji") else None
        )
        self.kana: Optional[List[ReadingElement]] = (
            [ReadingElement(k) for k in data.get("kana")] if data.get("kana") else None
        )
        self.sense: Optional[List[Sense]] = (
            [Sense(s) for s in data.get("sense")] if data.get("sense") else None
        )

    def __repr__(self):
        return f"JMdictEntry(id={self.id}, kanji={self.kanji}, kana={self.kana}, sense={self.sense})"

    def to_dict(self):
        d = {"id": self.id}
        if self.kanji:
            d["kanji"] = [k.to_dict() for k in self.kanji]
        if self.kana:
            d["kana"] = [k.to_dict() for k in self.kana]
        if self.sense:
            d["sense"] = [s.to_dict() for s in self.sense]
        return d

    def get_all_kana(self) -> List[str]:
        """Return a list of all kana readings."""
        return [k.text for k in self.kana] if self.kana else []

    def get_all_kanji(self) -> List[str]:
        """Return a list of all kanji writings."""
        return [k.text for k in self.kanji] if self.kanji else []

    def get_all_readings(self) -> List[str]:
        """Return a list of all readings (both kana and kanji)."""
        return self.get_all_kanji() + self.get_all_kana()


class JMdict:
    def __init__(self, data: Dict[str, Any]):
        self.words: List[JMdictEntry] = [JMdictEntry(entry) for entry in data["words"]]

    def __repr__(self):
        return f"JMdict(words_count={len(self.words)})"


def load_jmdict() -> JMdict:
    current_dir = Path(__file__).parent
    json_files = list(current_dir.glob("jmdict-*.json"))
    if not json_files:
        raise FileNotFoundError(f"No jmdict-*.json file found in {current_dir}")
    json_file = json_files[0]  # Use the first matching file
    with open(json_file, "r", encoding="utf-8") as f:
        return JMdict(json.load(f))


def write_entry_to_json(entry: JMdictEntry, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"{entry.id}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(entry.to_dict(), f, ensure_ascii=False, indent=2)
