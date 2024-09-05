// To parse this data:
//
//   import { Convert } from "./file";
//
//   const word = Convert.toWord(json);
//
// These functions will throw an error if the JSON doesn't
// match the expected interface, even if the JSON is valid.

export interface Word {
    _id:                string;
    simp:               string;
    trad:               string;
    items:              Item[];
    gloss?:             string;
    pinyinSearchString: string;
    statistics?:        Statistics;
}

export interface Item {
    source?:      Source;
    pinyin?:      string;
    simpTrad?:    SimpTrad;
    definitions?: string[];
    tang?:        string[];
}

export enum SimpTrad {
    Both = "both",
    Simp = "simp",
    Trad = "trad",
}

export enum Source {
    Cedict = "cedict",
    DongChinese = "dong-chinese",
    Unicode = "unicode",
}

export interface Statistics {
    hskLevel:                  number;
    topWords?:                 TopWord[];
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
    pinyinFrequency?:          number;
}

export interface TopWord {
    word:  string;
    share: number;
    trad:  string;
    gloss: string;
}

// Converts JSON strings to/from your types
// and asserts the results of JSON.parse at runtime
export class Convert {
    public static toWord(json: string): Word[] {
        return cast(JSON.parse(json), a(r("Word")));
    }

    public static wordToJson(value: Word[]): string {
        return JSON.stringify(uncast(value, a(r("Word"))), null, 2);
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
    "Word": o([
        { json: "_id", js: "_id", typ: "" },
        { json: "simp", js: "simp", typ: "" },
        { json: "trad", js: "trad", typ: "" },
        { json: "items", js: "items", typ: a(r("Item")) },
        { json: "gloss", js: "gloss", typ: u(undefined, "") },
        { json: "pinyinSearchString", js: "pinyinSearchString", typ: "" },
        { json: "statistics", js: "statistics", typ: u(undefined, r("Statistics")) },
    ], false),
    "Item": o([
        { json: "source", js: "source", typ: u(undefined, r("Source")) },
        { json: "pinyin", js: "pinyin", typ: u(undefined, "") },
        { json: "simpTrad", js: "simpTrad", typ: u(undefined, r("SimpTrad")) },
        { json: "definitions", js: "definitions", typ: u(undefined, a("")) },
        { json: "tang", js: "tang", typ: u(undefined, a("")) },
    ], false),
    "Statistics": o([
        { json: "hskLevel", js: "hskLevel", typ: 0 },
        { json: "topWords", js: "topWords", typ: u(undefined, a(r("TopWord"))) },
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
        { json: "pinyinFrequency", js: "pinyinFrequency", typ: u(undefined, 0) },
    ], false),
    "TopWord": o([
        { json: "word", js: "word", typ: "" },
        { json: "share", js: "share", typ: 3.14 },
        { json: "trad", js: "trad", typ: "" },
        { json: "gloss", js: "gloss", typ: "" },
    ], false),
    "SimpTrad": [
        "both",
        "simp",
        "trad",
    ],
    "Source": [
        "cedict",
        "dong-chinese",
        "unicode",
    ],
};
