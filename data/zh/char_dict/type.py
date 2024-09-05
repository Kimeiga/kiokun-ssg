from pathlib import Path
from typing import List, Optional, Dict, Any, Union
from enum import Enum


class TypeElement(str, Enum):
    DELETED = "deleted"
    DISTINGUISHING = "distinguishing"
    ICONIC = "iconic"
    MEANING = "meaning"
    REMNANT = "remnant"
    SIMPLIFIED = "simplified"
    SOUND = "sound"
    UNKNOWN = "unknown"


class ImageType(str, Enum):
    BRONZE = "Bronze"
    CLERICAL = "Clerical"
    ORACLE = "Oracle"
    REGULAR = "Regular"
    SEAL = "Seal"


class Comment:
    def __init__(self, data: Dict[str, Any]):
        self.source: str = data["source"]
        self.text: str = data["text"]

    def to_dict(self):
        return self.__dict__


class Component:
    def __init__(self, data: Dict[str, Any]):
        self.type: List[TypeElement] = [TypeElement(t) for t in data["type"]]
        self.character: str = data["character"]
        self.hint: Optional[str] = data.get("hint")
        self.is_old_pronunciation: Optional[bool] = data.get("isOldPronunciation")
        self.is_glyph_changed: Optional[bool] = data.get("isGlyphChanged")
        self.is_from_original_meaning: Optional[bool] = data.get(
            "isFromOriginalMeaning"
        )

    def to_dict(self):
        return {
            k: v if not isinstance(v, Enum) else v.value
            for k, v in self.__dict__.items()
            if v is not None
        }


class CharData:
    def __init__(self, data: Dict[str, Any]):
        self.strokes: List[str] = data["strokes"]
        self.medians: List[List[List[int]]] = data["medians"]
        self.character: Optional[str] = data.get("character")

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}


class ImageData:
    def __init__(self, data: Dict[str, Any]):
        self.strokes: List[str] = data["strokes"]
        self.medians: List[List[List[int]]] = data["medians"]

    def to_dict(self):
        return self.__dict__


class Image:
    def __init__(self, data: Dict[str, Any]):
        self.url: Optional[str] = data.get("url")
        self.source: str = data["source"]
        self.description: str = data["description"]
        self.type: ImageType = ImageType(data["type"])
        self.era: str = data["era"]
        self.data: Optional[ImageData] = (
            ImageData(data["data"]) if data.get("data") else None
        )
        self.fragments: Optional[List[List[int]]] = data.get("fragments")

    def to_dict(self):
        d = {
            k: v if not isinstance(v, Enum) else v.value
            for k, v in self.__dict__.items()
            if v is not None
        }
        if self.data:
            d["data"] = self.data.to_dict()
        return d


class OldPronunciation:
    def __init__(self, data: Dict[str, Any]):
        self.pinyin: Optional[str] = data.get("pinyin")
        self.MC: str = data["MC"]
        self.OC: Optional[str] = data.get("OC")
        self.gloss: Optional[str] = data.get("gloss")
        self.source: Optional[str] = data.get("source")

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}


class PinyinFrequency:
    def __init__(self, data: Dict[str, Any]):
        self.pinyin: str = data["pinyin"]
        self.count: int = data["count"]

    def to_dict(self):
        return self.__dict__


class TopWord:
    def __init__(self, data: Dict[str, Any]):
        self.word: str = data["word"]
        self.share: float = data["share"]
        self.trad: str = data["trad"]
        self.gloss: str = data["gloss"]

    def to_dict(self):
        return self.__dict__


class Statistics:
    def __init__(self, data: Dict[str, Any]):
        self.hsk_level: int = data["hskLevel"]
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
        self.top_words: Optional[List[TopWord]] = (
            [TopWord(w) for w in data["topWords"]] if data.get("topWords") else None
        )
        self.pinyin_frequency: Optional[float] = data.get("pinyinFrequency")

    def to_dict(self):
        d = {k: v for k, v in self.__dict__.items() if v is not None}
        if self.top_words:
            d["top_words"] = [w.to_dict() for w in self.top_words]
        return d


class Variant:
    def __init__(self, data: Dict[str, Any]):
        self.char: Optional[str] = data.get("char")
        self.parts: Optional[str] = data.get("parts")
        self.source: str = data["source"]

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}


class ChineseCharEntry:
    def __init__(self, data: Dict[str, Any]):
        self._id: str = data["_id"]
        self.char: str = data["char"]
        self.codepoint: Optional[str] = data.get("codepoint")
        self.stroke_count: Optional[Union[int, str]] = data.get("strokeCount")
        self.sources: Optional[List[str]] = data.get("sources")
        self.images: Optional[List[Image]] = (
            [Image(i) for i in data["images"]] if data.get("images") else None
        )
        self.shuowen: Optional[str] = data.get("shuowen")
        self.variants: Optional[List[Variant]] = (
            [Variant(v) for v in data["variants"]] if data.get("variants") else None
        )
        self.gloss: Optional[str] = data.get("gloss")
        self.statistics: Optional[Statistics] = (
            Statistics(data["statistics"]) if data.get("statistics") else None
        )
        self.hint: Optional[str] = data.get("hint")
        self.is_verified: Optional[bool] = data.get("isVerified")
        self.variant_of: Optional[str] = data.get("variantOf")
        self.simp_variants: Optional[List[str]] = data.get("simpVariants")
        self.comments: Optional[List[Comment]] = (
            [Comment(c) for c in data["comments"]] if data.get("comments") else None
        )
        self.custom_sources: Optional[List[str]] = data.get("customSources")
        self.components: Optional[List[Component]] = (
            [Component(c) for c in data["components"]]
            if data.get("components")
            else None
        )
        self.data: Optional[CharData] = (
            CharData(data["data"]) if data.get("data") else None
        )
        self.fragments: Optional[List[List[int]]] = data.get("fragments")
        self.old_pronunciations: Optional[List[OldPronunciation]] = (
            [OldPronunciation(op) for op in data["oldPronunciations"]]
            if data.get("oldPronunciations")
            else None
        )
        self.original_meaning: Optional[str] = data.get("originalMeaning")
        self.trad_variants: Optional[List[str]] = data.get("tradVariants")
        self.pinyin_frequencies: Optional[List[PinyinFrequency]] = (
            [PinyinFrequency(pf) for pf in data["pinyinFrequencies"]]
            if data.get("pinyinFrequencies")
            else None
        )

    def __repr__(self):
        return f"ChineseCharEntry(id={self._id}, char={self.char})"

    def to_dict(self):
        d = {k: v for k, v in self.__dict__.items() if v is not None}
        d["images"] = [i.to_dict() for i in self.images] if self.images else None
        d["variants"] = [v.to_dict() for v in self.variants] if self.variants else None
        d["statistics"] = self.statistics.to_dict() if self.statistics else None
        d["comments"] = [c.to_dict() for c in self.comments] if self.comments else None
        d["components"] = (
            [c.to_dict() for c in self.components] if self.components else None
        )
        d["data"] = self.data.to_dict() if self.data else None
        d["old_pronunciations"] = (
            [op.to_dict() for op in self.old_pronunciations]
            if self.old_pronunciations
            else None
        )
        d["pinyin_frequencies"] = (
            [pf.to_dict() for pf in self.pinyin_frequencies]
            if self.pinyin_frequencies
            else None
        )
        return d


class ChineseCharDict:
    def __init__(self):
        self.chars: List[ChineseCharEntry] = []

    def __repr__(self):
        return f"ChineseCharDict(chars_count={len(self.chars)})"

    def add_char(self, char_data: Dict[str, Any]):
        self.chars.append(ChineseCharEntry(char_data))

    @classmethod
    def from_jsonl(cls, file_path: str):
        import json

        chinese_dict = cls()
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                char_data = json.loads(line)
                chinese_dict.add_char(char_data)
        return chinese_dict


def load_chinese_char_dict() -> ChineseCharDict:
    current_dir = Path(__file__).parent
    json_files = list(current_dir.glob("dictionary_char_*.jsonl"))
    if not json_files:
        raise FileNotFoundError(
            f"No dictionary_char_*.jsonl file found in {current_dir}"
        )
    json_file = max(
        json_files, key=lambda f: f.stat().st_mtime
    )  # Use the most recently modified file
    return ChineseCharDict.from_jsonl(str(json_file))
