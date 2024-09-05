import os
import sys
from pathlib import Path
import fnmatch
from typing import List, Tuple


def parse_gitignore(gitignore_path: Path) -> List[str]:
    if not gitignore_path.exists():
        return []

    with open(gitignore_path, "r") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def is_ignored(path: Path, ignore_patterns: List[str]) -> bool:
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(str(path), pattern) or fnmatch.fnmatch(path.name, pattern):
            return True
    return False


def find_large_files(
    directory: Path, size_limit_mb: int = 50, ignore_patterns: List[str] = []
) -> List[Tuple[Path, int]]:
    size_limit_bytes = size_limit_mb * 1024 * 1024  # Convert MB to bytes
    large_files = []

    for root, dirs, files in os.walk(directory):
        # Remove ignored directories
        dirs[:] = [d for d in dirs if not is_ignored(Path(root) / d, ignore_patterns)]

        for file in files:
            file_path = Path(root) / file
            if file_path.is_file() and not is_ignored(file_path, ignore_patterns):
                size = file_path.stat().st_size
                if size > size_limit_bytes:
                    large_files.append((file_path, size))

    return large_files


def main():
    if len(sys.argv) > 1:
        directory = Path(sys.argv[1])
    else:
        directory = Path.cwd()

    gitignore_path = directory / ".gitignore"
    ignore_patterns = parse_gitignore(gitignore_path)

    print(f"Searching for files larger than 50 MiB in: {directory}")
    print("(Respecting .gitignore rules)")
    large_files = find_large_files(directory, ignore_patterns=ignore_patterns)

    if large_files:
        print("\nLarge files found:")
        for file_path, size in sorted(large_files, key=lambda x: x[1], reverse=True):
            print(f"{file_path}: {size / (1024 * 1024):.2f} MiB")
    else:
        print("\nNo files larger than 50 MiB found.")

    print(f"\nTotal number of large files: {len(large_files)}")


if __name__ == "__main__":
    main()
