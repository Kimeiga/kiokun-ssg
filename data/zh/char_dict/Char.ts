// To parse this data:
//
//   import { Convert } from "./file";
//
//   const char = Convert.toChar(json);
//
// These functions will throw an error if the JSON doesn't
// match the expected interface, even if the JSON is valid.

export interface Char {
    _id:                string;
    char:               string;
    codepoint?:         string;
    strokeCount?:       number | string;
    sources?:           Source[];
    images?:            Image[] | null;
    shuowen?:           string;
    variants?:          Variant[];
    gloss?:             string;
    statistics?:        Statistics;
    hint?:              string;
    isVerified?:        boolean;
    variantOf?:         string;
    simpVariants?:      string[];
    comments?:          Comment[];
    customSources?:     string[];
    components?:        Component[];
    data?:              CharData | null;
    fragments?:         Array<number[]> | null;
    oldPronunciations?: OldPronunciation[] | null;
    originalMeaning?:   string;
    tradVariants?:      string[];
    pinyinFrequencies?: PinyinFrequency[];
}

export interface Comment {
    source: Source;
    text:   string;
}

export enum Source {
    AcademiaSinica = "academia-sinica",
    BaxterSagart = "baxter-sagart",
    DongChinese = "dong-chinese",
    Makemeahanzi = "makemeahanzi",
    Unicode = "unicode",
}

export interface Component {
    type:                   TypeElement[];
    character:              string;
    hint?:                  null | string;
    isOldPronunciation?:    boolean;
    isGlyphChanged?:        boolean;
    isFromOriginalMeaning?: boolean;
}

export enum TypeElement {
    Deleted = "deleted",
    Distinguishing = "distinguishing",
    Iconic = "iconic",
    Meaning = "meaning",
    Remnant = "remnant",
    Simplified = "simplified",
    Sound = "sound",
    Unknown = "unknown",
}

export interface CharData {
    strokes:    string[];
    medians:    Array<Array<number[]>>;
    character?: string;
}

export interface Image {
    url?:        string;
    source:      Source;
    description: string;
    type:        ImageType;
    era:         Era;
    data?:       ImageData;
    fragments?:  Array<number[]>;
}

export interface ImageData {
    strokes: string[];
    medians: Array<Array<number[]>>;
}

export enum Era {
    CaoWeiThreeKingdoms222280AD = "Cao Wei (Three Kingdoms: 222-280 AD)",
    ChuWarringStates475221BC = "Chu (Warring States: 475-221 BC)",
    EarlySpringAndAutumn700BC = "Early Spring and Autumn (~700 BC)",
    EarlyWarringStates400BC = "Early Warring States (~400 BC)",
    EarlyWesternZhou1000BC = "Early Western Zhou (~1000 BC)",
    EasternHanDynasty25220AD = "Eastern Han dynasty (25-220 AD)",
    HanDynasty202BC220AD = "Han dynasty (202 BC - 220 AD)",
    JinDynasty266420AD = "Jin dynasty (266-420 AD)",
    LateShangDynasty1100BC = "Late Shang dynasty (~1100 BC)",
    LateSpringAndAutumn500BC = "Late Spring and Autumn (~500 BC)",
    LateWarringStates250BC = "Late Warring States (~250 BC)",
    LateWesternZhou800BC = "Late Western Zhou (~800 BC)",
    MidSpringAndAutumn600BC = "Mid Spring and Autumn (~600 BC)",
    MidWarringStates300BC = "Mid Warring States (~300 BC)",
    MidWesternZhou900BC = "Mid Western Zhou (~900 BC)",
    Modern = "Modern",
    QinDynasty221206BC = "Qin dynasty (221-206 BC)",
    Shuowen100AD = "Shuowen (~100 AD)",
    SpringAndAutumn771476BC = "Spring and Autumn (771-476 BC)",
    The1200221Bc = "(~1200 - 221 BC)",
    The12501000Bc = "(~1250-1000 BC)",
    The200Ad = "(~200 AD)",
    WarringStates475221BC = "Warring States (475-221 BC)",
    WesternHanDynasty202BC9AD = "Western Han dynasty (202 BC-9 AD)",
    WesternJinDynasty266316AD = "Western Jin dynasty (266-316 AD)",
    WesternZhou1045771BC = "Western Zhou (1045-771 BC)",
    WuThreeKingdoms222280AD = "Wu (Three Kingdoms: 222-280 AD)",
    XinDynasty923AD = "Xin dynasty (9-23 AD)",
}

export enum ImageType {
    Bronze = "Bronze",
    Clerical = "Clerical",
    Oracle = "Oracle",
    Regular = "Regular",
    Seal = "Seal",
}

export interface OldPronunciation {
    pinyin?: string;
    MC:      string;
    OC?:     string;
    gloss?:  string;
    source?: Source;
}

export interface PinyinFrequency {
    pinyin: string;
    count:  number;
}

export interface Statistics {
    hskLevel:                  number;
    movieWordCount?:           number;
    movieWordCountPercent?:    number;
    movieWordRank?:            number;
    movieWordContexts?:        number;
    movieWordContextsPercent?: number;
    bookWordCount?:            number;
    bookWordCountPercent?:     number;
    bookWordRank?:             number;
    movieCharCount?:           number;
    movieCharCountPercent?:    number;
    movieCharRank?:            number;
    movieCharContexts?:        number;
    movieCharContextsPercent?: number;
    bookCharCount?:            number;
    bookCharCountPercent?:     number;
    bookCharRank?:             number;
    topWords?:                 TopWord[];
    pinyinFrequency?:          number;
}

export interface TopWord {
    word:  string;
    share: number;
    trad:  string;
    gloss: string;
}

export interface Variant {
    char:   null | string;
    parts:  null | string;
    source: Source;
}

// Converts JSON strings to/from your types
// and asserts the results of JSON.parse at runtime
export class Convert {
    public static toChar(json: string): Char[] {
        return cast(JSON.parse(json), a(r("Char")));
    }

    public static charToJson(value: Char[]): string {
        return JSON.stringify(uncast(value, a(r("Char"))), null, 2);
    }
}

function invalidValue(typ: any, val: any, key: any, parent: any = ''): never {
    const prettyTyp = prettyTypeName(typ);
    const parentText = parent ? ` on ${parent}` : '';
    const keyText = key ? ` for key "${key}"` : '';
    throw Error(`Invalid value${keyText}${parentText}. Expected ${prettyTyp} but got ${JSON.stringify(val)}`);
}

function prettyTypeName(typ: any): string {
    if (Array.isArray(typ)) {
        if (typ.length === 2 && typ[0] === undefined) {
            return `an optional ${prettyTypeName(typ[1])}`;
        } else {
            return `one of [${typ.map(a => { return prettyTypeName(a); }).join(", ")}]`;
        }
    } else if (typeof typ === "object" && typ.literal !== undefined) {
        return typ.literal;
    } else {
        return typeof typ;
    }
}

function jsonToJSProps(typ: any): any {
    if (typ.jsonToJS === undefined) {
        const map: any = {};
        typ.props.forEach((p: any) => map[p.json] = { key: p.js, typ: p.typ });
        typ.jsonToJS = map;
    }
    return typ.jsonToJS;
}

function jsToJSONProps(typ: any): any {
    if (typ.jsToJSON === undefined) {
        const map: any = {};
        typ.props.forEach((p: any) => map[p.js] = { key: p.json, typ: p.typ });
        typ.jsToJSON = map;
    }
    return typ.jsToJSON;
}

function transform(val: any, typ: any, getProps: any, key: any = '', parent: any = ''): any {
    function transformPrimitive(typ: string, val: any): any {
        if (typeof typ === typeof val) return val;
        return invalidValue(typ, val, key, parent);
    }

    function transformUnion(typs: any[], val: any): any {
        // val must validate against one typ in typs
        const l = typs.length;
        for (let i = 0; i < l; i++) {
            const typ = typs[i];
            try {
                return transform(val, typ, getProps);
            } catch (_) {}
        }
        return invalidValue(typs, val, key, parent);
    }

    function transformEnum(cases: string[], val: any): any {
        if (cases.indexOf(val) !== -1) return val;
        return invalidValue(cases.map(a => { return l(a); }), val, key, parent);
    }

    function transformArray(typ: any, val: any): any {
        // val must be an array with no invalid elements
        if (!Array.isArray(val)) return invalidValue(l("array"), val, key, parent);
        return val.map(el => transform(el, typ, getProps));
    }

    function transformDate(val: any): any {
        if (val === null) {
            return null;
        }
        const d = new Date(val);
        if (isNaN(d.valueOf())) {
            return invalidValue(l("Date"), val, key, parent);
        }
        return d;
    }

    function transformObject(props: { [k: string]: any }, additional: any, val: any): any {
        if (val === null || typeof val !== "object" || Array.isArray(val)) {
            return invalidValue(l(ref || "object"), val, key, parent);
        }
        const result: any = {};
        Object.getOwnPropertyNames(props).forEach(key => {
            const prop = props[key];
            const v = Object.prototype.hasOwnProperty.call(val, key) ? val[key] : undefined;
            result[prop.key] = transform(v, prop.typ, getProps, key, ref);
        });
        Object.getOwnPropertyNames(val).forEach(key => {
            if (!Object.prototype.hasOwnProperty.call(props, key)) {
                result[key] = transform(val[key], additional, getProps, key, ref);
            }
        });
        return result;
    }

    if (typ === "any") return val;
    if (typ === null) {
        if (val === null) return val;
        return invalidValue(typ, val, key, parent);
    }
    if (typ === false) return invalidValue(typ, val, key, parent);
    let ref: any = undefined;
    while (typeof typ === "object" && typ.ref !== undefined) {
        ref = typ.ref;
        typ = typeMap[typ.ref];
    }
    if (Array.isArray(typ)) return transformEnum(typ, val);
    if (typeof typ === "object") {
        return typ.hasOwnProperty("unionMembers") ? transformUnion(typ.unionMembers, val)
            : typ.hasOwnProperty("arrayItems")    ? transformArray(typ.arrayItems, val)
            : typ.hasOwnProperty("props")         ? transformObject(getProps(typ), typ.additional, val)
            : invalidValue(typ, val, key, parent);
    }
    // Numbers can be parsed by Date but shouldn't be.
    if (typ === Date && typeof val !== "number") return transformDate(val);
    return transformPrimitive(typ, val);
}

function cast<T>(val: any, typ: any): T {
    return transform(val, typ, jsonToJSProps);
}

function uncast<T>(val: T, typ: any): any {
    return transform(val, typ, jsToJSONProps);
}

function l(typ: any) {
    return { literal: typ };
}

function a(typ: any) {
    return { arrayItems: typ };
}

function u(...typs: any[]) {
    return { unionMembers: typs };
}

function o(props: any[], additional: any) {
    return { props, additional };
}

function m(additional: any) {
    return { props: [], additional };
}

function r(name: string) {
    return { ref: name };
}

const typeMap: any = {
    "Char": o([
        { json: "_id", js: "_id", typ: "" },
        { json: "char", js: "char", typ: "" },
        { json: "codepoint", js: "codepoint", typ: u(undefined, "") },
        { json: "strokeCount", js: "strokeCount", typ: u(undefined, u(0, "")) },
        { json: "sources", js: "sources", typ: u(undefined, a(r("Source"))) },
        { json: "images", js: "images", typ: u(undefined, u(a(r("Image")), null)) },
        { json: "shuowen", js: "shuowen", typ: u(undefined, "") },
        { json: "variants", js: "variants", typ: u(undefined, a(r("Variant"))) },
        { json: "gloss", js: "gloss", typ: u(undefined, "") },
        { json: "statistics", js: "statistics", typ: u(undefined, r("Statistics")) },
        { json: "hint", js: "hint", typ: u(undefined, "") },
        { json: "isVerified", js: "isVerified", typ: u(undefined, true) },
        { json: "variantOf", js: "variantOf", typ: u(undefined, "") },
        { json: "simpVariants", js: "simpVariants", typ: u(undefined, a("")) },
        { json: "comments", js: "comments", typ: u(undefined, a(r("Comment"))) },
        { json: "customSources", js: "customSources", typ: u(undefined, a("")) },
        { json: "components", js: "components", typ: u(undefined, a(r("Component"))) },
        { json: "data", js: "data", typ: u(undefined, u(r("CharData"), null)) },
        { json: "fragments", js: "fragments", typ: u(undefined, u(a(a(0)), null)) },
        { json: "oldPronunciations", js: "oldPronunciations", typ: u(undefined, u(a(r("OldPronunciation")), null)) },
        { json: "originalMeaning", js: "originalMeaning", typ: u(undefined, "") },
        { json: "tradVariants", js: "tradVariants", typ: u(undefined, a("")) },
        { json: "pinyinFrequencies", js: "pinyinFrequencies", typ: u(undefined, a(r("PinyinFrequency"))) },
    ], false),
    "Comment": o([
        { json: "source", js: "source", typ: r("Source") },
        { json: "text", js: "text", typ: "" },
    ], false),
    "Component": o([
        { json: "type", js: "type", typ: a(r("TypeElement")) },
        { json: "character", js: "character", typ: "" },
        { json: "hint", js: "hint", typ: u(undefined, u(null, "")) },
        { json: "isOldPronunciation", js: "isOldPronunciation", typ: u(undefined, true) },
        { json: "isGlyphChanged", js: "isGlyphChanged", typ: u(undefined, true) },
        { json: "isFromOriginalMeaning", js: "isFromOriginalMeaning", typ: u(undefined, true) },
    ], false),
    "CharData": o([
        { json: "strokes", js: "strokes", typ: a("") },
        { json: "medians", js: "medians", typ: a(a(a(3.14))) },
        { json: "character", js: "character", typ: u(undefined, "") },
    ], false),
    "Image": o([
        { json: "url", js: "url", typ: u(undefined, "") },
        { json: "source", js: "source", typ: r("Source") },
        { json: "description", js: "description", typ: "" },
        { json: "type", js: "type", typ: r("ImageType") },
        { json: "era", js: "era", typ: r("Era") },
        { json: "data", js: "data", typ: u(undefined, r("ImageData")) },
        { json: "fragments", js: "fragments", typ: u(undefined, a(a(0))) },
    ], false),
    "ImageData": o([
        { json: "strokes", js: "strokes", typ: a("") },
        { json: "medians", js: "medians", typ: a(a(a(3.14))) },
    ], false),
    "OldPronunciation": o([
        { json: "pinyin", js: "pinyin", typ: u(undefined, "") },
        { json: "MC", js: "MC", typ: "" },
        { json: "OC", js: "OC", typ: u(undefined, "") },
        { json: "gloss", js: "gloss", typ: u(undefined, "") },
        { json: "source", js: "source", typ: u(undefined, r("Source")) },
    ], false),
    "PinyinFrequency": o([
        { json: "pinyin", js: "pinyin", typ: "" },
        { json: "count", js: "count", typ: 0 },
    ], false),
    "Statistics": o([
        { json: "hskLevel", js: "hskLevel", typ: 0 },
        { json: "movieWordCount", js: "movieWordCount", typ: u(undefined, 0) },
        { json: "movieWordCountPercent", js: "movieWordCountPercent", typ: u(undefined, 3.14) },
        { json: "movieWordRank", js: "movieWordRank", typ: u(undefined, 0) },
        { json: "movieWordContexts", js: "movieWordContexts", typ: u(undefined, 0) },
        { json: "movieWordContextsPercent", js: "movieWordContextsPercent", typ: u(undefined, 3.14) },
        { json: "bookWordCount", js: "bookWordCount", typ: u(undefined, 0) },
        { json: "bookWordCountPercent", js: "bookWordCountPercent", typ: u(undefined, 3.14) },
        { json: "bookWordRank", js: "bookWordRank", typ: u(undefined, 0) },
        { json: "movieCharCount", js: "movieCharCount", typ: u(undefined, 0) },
        { json: "movieCharCountPercent", js: "movieCharCountPercent", typ: u(undefined, 3.14) },
        { json: "movieCharRank", js: "movieCharRank", typ: u(undefined, 0) },
        { json: "movieCharContexts", js: "movieCharContexts", typ: u(undefined, 0) },
        { json: "movieCharContextsPercent", js: "movieCharContextsPercent", typ: u(undefined, 3.14) },
        { json: "bookCharCount", js: "bookCharCount", typ: u(undefined, 0) },
        { json: "bookCharCountPercent", js: "bookCharCountPercent", typ: u(undefined, 3.14) },
        { json: "bookCharRank", js: "bookCharRank", typ: u(undefined, 0) },
        { json: "topWords", js: "topWords", typ: u(undefined, a(r("TopWord"))) },
        { json: "pinyinFrequency", js: "pinyinFrequency", typ: u(undefined, 0) },
    ], false),
    "TopWord": o([
        { json: "word", js: "word", typ: "" },
        { json: "share", js: "share", typ: 3.14 },
        { json: "trad", js: "trad", typ: "" },
        { json: "gloss", js: "gloss", typ: "" },
    ], false),
    "Variant": o([
        { json: "char", js: "char", typ: u(null, "") },
        { json: "parts", js: "parts", typ: u(null, "") },
        { json: "source", js: "source", typ: r("Source") },
    ], false),
    "Source": [
        "academia-sinica",
        "baxter-sagart",
        "dong-chinese",
        "makemeahanzi",
        "unicode",
    ],
    "TypeElement": [
        "deleted",
        "distinguishing",
        "iconic",
        "meaning",
        "remnant",
        "simplified",
        "sound",
        "unknown",
    ],
    "Era": [
        "Cao Wei (Three Kingdoms: 222-280 AD)",
        "Chu (Warring States: 475-221 BC)",
        "Early Spring and Autumn (~700 BC)",
        "Early Warring States (~400 BC)",
        "Early Western Zhou (~1000 BC)",
        "Eastern Han dynasty (25-220 AD)",
        "Han dynasty (202 BC - 220 AD)",
        "Jin dynasty (266-420 AD)",
        "Late Shang dynasty (~1100 BC)",
        "Late Spring and Autumn (~500 BC)",
        "Late Warring States (~250 BC)",
        "Late Western Zhou (~800 BC)",
        "Mid Spring and Autumn (~600 BC)",
        "Mid Warring States (~300 BC)",
        "Mid Western Zhou (~900 BC)",
        "Modern",
        "Qin dynasty (221-206 BC)",
        "Shuowen (~100 AD)",
        "Spring and Autumn (771-476 BC)",
        "(~1200 - 221 BC)",
        "(~1250-1000 BC)",
        "(~200 AD)",
        "Warring States (475-221 BC)",
        "Western Han dynasty (202 BC-9 AD)",
        "Western Jin dynasty (266-316 AD)",
        "Western Zhou (1045-771 BC)",
        "Wu (Three Kingdoms: 222-280 AD)",
        "Xin dynasty (9-23 AD)",
    ],
    "ImageType": [
        "Bronze",
        "Clerical",
        "Oracle",
        "Regular",
        "Seal",
    ],
};
