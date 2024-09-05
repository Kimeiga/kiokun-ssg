from pathlib import Path
from typing import List, Optional, Dict, Any
from enum import Enum


class SimpTrad(str, Enum):
    BOTH = "both"
    SIMP = "simp"
    TRAD = "trad"


class Source(str, Enum):
    CEDICT = "cedict"
    DONG_CHINESE = "dong-chinese"
    UNICODE = "unicode"


class TopWord:
    def __init__(self, data: Dict[str, Any]):
        self.word: str = data["word"]
        self.share: float = data["share"]
        self.trad: str = data["trad"]
        self.gloss: str = data["gloss"]

    def __repr__(self):
        return f"TopWord(word={self.word}, share={self.share}, trad={self.trad}, gloss={self.gloss})"

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}


class Statistics:
    def __init__(self, data: Dict[str, Any]):
        self.hsk_level: int = data["hskLevel"]
        self.top_words: Optional[List[TopWord]] = (
            [TopWord(w) for w in data.get("topWords", [])]
            if data.get("topWords")
            else None
        )
        self.movie_word_count: Optional[int] = data.get("movieWordCount")
        self.movie_word_count_percent: Optional[float] = data.get(
            "movieWordCountPercent"
        )
        self.movie_word_rank: Optional[int] = data.get("movieWordRank")
        self.movie_word_contexts: Optional[int] = data.get("movieWordContexts")
        self.movie_word_contexts_percent: Optional[float] = data.get(
            "movieWordContextsPercent"
        )
        self.book_word_count: Optional[int] = data.get("bookWordCount")
        self.book_word_count_percent: Optional[float] = data.get("bookWordCountPercent")
        self.book_word_rank: Optional[int] = data.get("bookWordRank")
        self.movie_char_count: Optional[int] = data.get("movieCharCount")
        self.movie_char_count_percent: Optional[float] = data.get(
            "movieCharCountPercent"
        )
        self.movie_char_rank: Optional[int] = data.get("movieCharRank")
        self.movie_char_contexts: Optional[int] = data.get("movieCharContexts")
        self.movie_char_contexts_percent: Optional[float] = data.get(
            "movieCharContextsPercent"
        )
        self.book_char_count: Optional[int] = data.get("bookCharCount")
        self.book_char_count_percent: Optional[float] = data.get("bookCharCountPercent")
        self.book_char_rank: Optional[int] = data.get("bookCharRank")
        self.pinyin_frequency: Optional[float] = data.get("pinyinFrequency")

    def __repr__(self):
        return f"Statistics(hsk_level={self.hsk_level}, top_words_count={len(self.top_words) if self.top_words else 0})"

    def to_dict(self):
        d = {k: v for k, v in self.__dict__.items() if v is not None}
        if self.top_words:
            d["top_words"] = [w.to_dict() for w in self.top_words]
        return d


class Item:
    def __init__(self, data: Dict[str, Any]):
        self.source: Optional[Source] = (
            Source(data["source"]) if data.get("source") else None
        )
        self.pinyin: Optional[str] = data.get("pinyin")
        self.simp_trad: Optional[SimpTrad] = (
            SimpTrad(data["simpTrad"]) if data.get("simpTrad") else None
        )
        self.definitions: Optional[List[str]] = data.get("definitions")
        self.tang: Optional[List[str]] = data.get("tang")

    def __repr__(self):
        return f"Item(source={self.source}, pinyin={self.pinyin}, simp_trad={self.simp_trad})"

    def to_dict(self):
        return {
            k: v if not isinstance(v, Enum) else v.value
            for k, v in self.__dict__.items()
            if v is not None
        }


class ChineseWordEntry:
    def __init__(self, data: Dict[str, Any]):
        self._id: str = data["_id"]
        self.simp: str = data["simp"]
        self.trad: str = data["trad"]
        self.items: List[Item] = [Item(item) for item in data["items"]]
        self.gloss: Optional[str] = data.get("gloss")
        self.pinyin_search_string: str = data["pinyinSearchString"]
        self.statistics: Optional[Statistics] = (
            Statistics(data["statistics"]) if data.get("statistics") else None
        )

    def __repr__(self):
        return f"ChineseWordEntry(id={self._id}, simp={self.simp}, trad={self.trad}, items_count={len(self.items)})"

    def to_dict(self):
        d = {k: v for k, v in self.__dict__.items() if v is not None}
        d["items"] = [item.to_dict() for item in self.items]
        if self.statistics:
            d["statistics"] = self.statistics.to_dict()
        return d


class ChineseWordDict:
    def __init__(self):
        self.words: List[ChineseWordEntry] = []

    def __repr__(self):
        return f"ChineseWordDict(words_count={len(self.words)})"

    def add_word(self, word_data: Dict[str, Any]):
        self.words.append(ChineseWordEntry(word_data))

    @classmethod
    def from_jsonl(cls, file_path: str):
        import json

        chinese_dict = cls()
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                word_data = json.loads(line)
                chinese_dict.add_word(word_data)
        return chinese_dict


def load_chinese_word_dict() -> ChineseWordDict:
    current_dir = Path(__file__).parent
    json_files = list(current_dir.glob("dictionary_word_*.jsonl"))
    if not json_files:
        raise FileNotFoundError(
            f"No dictionary_word_*.jsonl file found in {current_dir}"
        )
    json_file = max(
        json_files, key=lambda f: f.stat().st_mtime
    )  # Use the most recently modified file
    return ChineseWordDict.from_jsonl(str(json_file))
