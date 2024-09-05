from pathlib import Path
from typing import List, Optional, Dict, Any, Union
import json


class JMnedictKanji:
    def __init__(self, data: Dict[str, Any]):
        self.text: str = data["text"]
        self.tags: List[str] = data.get("tags", [])

    def to_dict(self):
        return json.loads(json.dumps(self.__dict__))


class JMnedictKana:
    def __init__(self, data: Dict[str, Any]):
        self.text: str = data["text"]
        self.tags: List[str] = data.get("tags", [])
        self.applies_to_kanji: List[str] = data.get("appliesToKanji", [])

    def to_dict(self):
        return json.loads(json.dumps(self.__dict__))


class JMnedictTranslationTranslation:
    def __init__(self, data: Dict[str, Any]):
        self.lang: str = data["lang"]
        self.text: str = data["text"]

    def to_dict(self):
        return json.loads(json.dumps(self.__dict__))


class JMnedictTranslation:
    def __init__(self, data: Dict[str, Any]):
        self.type: List[str] = data.get("type", [])
        self.related: List[Union[List[str], List[str, str], List[str, str, int]]] = (
            data.get("related", [])
        )
        self.translation: List[JMnedictTranslationTranslation] = [
            JMnedictTranslationTranslation(t) for t in data.get("translation", [])
        ]

    def to_dict(self):
        return {
            "type": self.type,
            "related": self.related,
            "translation": [t.to_dict() for t in self.translation],
        }


class JMnedictWord:
    def __init__(self, data: Dict[str, Any]):
        self.id: str = data["id"]
        self.kanji: List[JMnedictKanji] = [
            JMnedictKanji(k) for k in data.get("kanji", [])
        ]
        self.kana: List[JMnedictKana] = [JMnedictKana(k) for k in data.get("kana", [])]
        self.translation: List[JMnedictTranslation] = [
            JMnedictTranslation(t) for t in data.get("translation", [])
        ]

    def __repr__(self):
        return f"JMnedictWord(id={self.id}, kanji={[k.text for k in self.kanji]}, kana={[k.text for k in self.kana]})"

    def to_dict(self):
        return {
            "id": self.id,
            "kanji": [k.to_dict() for k in self.kanji],
            "kana": [k.to_dict() for k in self.kana],
            "translation": [t.to_dict() for t in self.translation],
        }


class JMnedict:
    def __init__(self, data: Dict[str, Any]):
        self.version: str = data["version"]
        self.languages: List[str] = data["languages"]
        self.dict_date: str = data["dictDate"]
        self.common_only: bool = data["commonOnly"]
        self.dict_revisions: List[str] = data["dictRevisions"]
        self.tags: Dict[str, str] = data["tags"]
        self.words: List[JMnedictWord] = [JMnedictWord(w) for w in data["words"]]

    def __repr__(self):
        return f"JMnedict(words_count={len(self.words)})"

    def to_dict(self):
        return {
            "version": self.version,
            "languages": self.languages,
            "dictDate": self.dict_date,
            "commonOnly": self.common_only,
            "dictRevisions": self.dict_revisions,
            "tags": self.tags,
            "words": [w.to_dict() for w in self.words],
        }


def load_jmnedict() -> JMnedict:
    current_dir = Path(__file__).parent
    json_files = list(current_dir.glob("jmnedict-*.json"))
    if not json_files:
        raise FileNotFoundError(f"No jmnedict-*.json file found in {current_dir}")
    json_file = json_files[0]  # Use the first matching file
    with open(json_file, "r", encoding="utf-8") as f:
        return JMnedict(json.load(f))


def write_entry_to_json(entry: JMnedictWord, output_dir: str):
    import os

    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"{entry.id}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(entry.to_dict(), f, ensure_ascii=False, indent=2)
