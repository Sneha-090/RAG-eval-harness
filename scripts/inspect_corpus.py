"""Inspect the frozen benchmark corpus: file count, size and basic text statistics."""
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def inspect_file(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    return {
        "name": path.name,
        "bytes": path.stat().st_size,
        "words": len(text.split()),
        "lines": len(lines),
        "headings": sum(1 for line in lines if line.startswith("#")),
        "code_fences": sum(1 for line in lines if line.strip().startswith("```")) // 2,
        "code_includes": sum(1 for line in lines if line.strip().startswith("{*")),
    }


def main() -> None:
    files = sorted(RAW_DIR.glob("*.md"))
    if not files:
        print(f"No .md files found in {RAW_DIR}")
        return

    rows = [inspect_file(f) for f in files]
    header = f"{'file':42}{'bytes':>8}{'words':>8}{'lines':>7}{'heads':>7}{'fences':>8}{'includes':>10}"
    print(header)
    print("-" * len(header))
    for r in rows:
        print(
            f"{r['name']:42}{r['bytes']:>8}{r['words']:>8}{r['lines']:>7}"
            f"{r['headings']:>7}{r['code_fences']:>8}{r['code_includes']:>10}"
        )
    print("-" * len(header))
    print(f"Files: {len(rows)}")
    print(f"Total bytes: {sum(r['bytes'] for r in rows)}")
    print(f"Total words: {sum(r['words'] for r in rows)}")


if __name__ == "__main__":
    main()