"""Inspect the frozen benchmark corpus: file count, size and basic text statistics."""
import argparse
from pathlib import Path

from src.corpora import CORPORA, get_corpus


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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", choices=CORPORA, default="fastapi-v1")
    args = parser.parse_args()
    corpus = get_corpus(args.corpus)
    files = sorted(path for path in corpus.raw_dir.iterdir() if path.suffix in {".md", ".txt"})
    if not files:
        print(f"No Markdown/text files found in {corpus.raw_dir}")
        return

    print(f"Corpus: {corpus.label} ({corpus.key})")
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
