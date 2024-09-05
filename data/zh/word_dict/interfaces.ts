export interface Word {
  _id: string;
  simp: string;
  trad: string;
  items?: (ItemsEntity | null)[] | null;
  gloss?: string | null;
  pinyinSearchString: string;
  statistics?: Statistics | null;
}
export interface ItemsEntity {
  source?: string | null;
  pinyin?: string | null;
  simpTrad?: string | null;
  definitions?: (string | null)[] | null;
  tang?: (string)[] | null;
}
export interface Statistics {
  hskLevel: number;
  topWords?: (TopWordsEntity | null)[] | null;
  movieWordCount?: number | null;
  movieWordCountPercent?: number | null;
  movieWordRank?: number | null;
  movieWordContexts?: number | null;
  movieWordContextsPercent?: number | null;
  bookWordCount?: number | null;
  bookWordCountPercent?: number | null;
  bookWordRank?: number | null;
  movieCharCount?: number | null;
  movieCharCountPercent?: number | null;
  movieCharRank?: number | null;
  movieCharContexts?: number | null;
  movieCharContextsPercent?: number | null;
  bookCharCount?: number | null;
  bookCharCountPercent?: number | null;
  bookCharRank?: number | null;
  pinyinFrequency?: number | null;
}
export interface TopWordsEntity {
  word: string;
  share: number;
  trad: string;
  gloss: string;
}
