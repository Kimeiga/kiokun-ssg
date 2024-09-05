import json
import argparse
from typing import Dict, Any, List, Union
from collections import defaultdict


def infer_type_structure(value: Any) -> Union[str, Dict[str, Any], List[Any]]:
    if isinstance(value, str):
        return "str"
    elif isinstance(value, int):
        return "int"
    elif isinstance(value, float):
        return "float"
    elif isinstance(value, bool):
        return "bool"
    elif isinstance(value, list):
        if not value:
            return "List[Any]"
        return [infer_type_structure(value[0])]
    elif isinstance(value, dict):
        return {k: infer_type_structure(v) for k, v in value.items()}
    elif value is None:
        return "None"
    else:
        return type(value).__name__


def merge_structures(s1: Any, s2: Any) -> Any:
    if isinstance(s1, dict) and isinstance(s2, dict):
        result = {}
        all_keys = set(s1.keys()) | set(s2.keys())
        for key in all_keys:
            if key in s1 and key in s2:
                result[key] = merge_structures(s1[key], s2[key])
            elif key in s1:
                result[key] = merge_structures(s1[key], "None")
            else:
                result[key] = merge_structures(s2[key], "None")
        return result
    elif isinstance(s1, list) and isinstance(s2, list):
        return [merge_structures(s1[0], s2[0])]
    elif s1 == "None" or s2 == "None":
        return f"Optional[{s1 if s2 == 'None' else s2}]"
    elif s1 == s2:
        return s1
    else:
        return f"Union[{s1}, {s2}]"


def analyze_jsonl_structure(file_path: str) -> Dict[str, Any]:
    structure = {}

    with open(file_path, "r") as file:
        for line in file:
            try:
                entry: Dict[str, Any] = json.loads(line.strip())
                entry_structure = infer_type_structure(entry)
                structure = merge_structures(structure, entry_structure)
            except json.JSONDecodeError:
                print(f"Warning: Skipping invalid JSON line: {line.strip()}")

    return structure


def simplify_structure(structure: Any) -> Any:
    if isinstance(structure, dict):
        return {k: simplify_structure(v) for k, v in structure.items()}
    elif isinstance(structure, list):
        return [simplify_structure(structure[0])]
    elif isinstance(structure, str):
        if structure.startswith("Optional[") and structure.endswith("]"):
            return structure
        if structure.startswith("Union[") and structure.endswith("]"):
            types = [t.strip() for t in structure[6:-1].split(",")]
            unique_types = list(set(types))
            if len(unique_types) == 1:
                return unique_types[0]
            if "None" in unique_types:
                other_types = [t for t in unique_types if t != "None"]
                if len(other_types) == 1:
                    return f"Optional[{other_types[0]}]"
            return f"Union[{', '.join(unique_types)}]"
    return structure


def print_structure(structure: Any, indent: str = "") -> None:
    if isinstance(structure, dict):
        for key, value in structure.items():
            print(f"{indent}{key}:")
            print_structure(value, indent + "  ")
    elif isinstance(structure, list):
        print(f"{indent}List[")
        print_structure(structure[0], indent + "  ")
        print(f"{indent}]")
    else:
        print(f"{indent}{structure}")


def main():
    parser = argparse.ArgumentParser(
        description="Recursively analyze the structure of a JSONL file."
    )
    parser.add_argument("file_path", help="Path to the JSONL file")
    args = parser.parse_args()

    result = analyze_jsonl_structure(args.file_path)
    simplified_result = simplify_structure(result)
    print("Recursive structure of the JSONL file:")
    print_structure(simplified_result)


if __name__ == "__main__":
    main()
