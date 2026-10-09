"""Load documents from a folder and apply light, documented normalization."""
import re
import sys
from dataclasses import dataclass
from pathlib import Path

SUPPORTED_SUFFIXES = {".md", ".txt"}

# Lines such as {* ../../docs_src/example.py hl[3] *} point to code files
# that are not part of the corpus, so they are removed.
PLACEHOLDER_PATTERN = re.compile(r"^[ \t]*\{\*.*\*\}[ \t]*$", re.MULTILINE)


@dataclass
class Document:
    doc_id: str  # the file name, used later as the "source" of each chunk
    text: str


def normalize(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = PLACEHOLDER_PATTERN.sub("", text)
    text = re.sub(r"[ \t]+\n", "\n", text)  # trailing spaces
    text = re.sub(r"\n{3,}", "\n\n", text)  # runs of blank lines
    return text.strip()


def load_documents(directory) -> list[Document]:
    directory = Path(directory)
    paths = sorted(p for p in directory.iterdir() if p.suffix in SUPPORTED_SUFFIXES)
    return [
        Document(doc_id=p.name, text=normalize(p.read_text(encoding="utf-8")))
        for p in paths
    ]


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raw_dir = Path(__file__).resolve().parents[2] / "data" / "raw"
    docs = load_documents(raw_dir)

    for d in docs:
        print(f"{d.doc_id:42}{len(d.text):>8} characters")
    print(f"Documents: {len(docs)}")
    print(f"Remaining '{{*' placeholders: {sum(d.text.count('{*') for d in docs)}")

    print(f"\n--- Preview of {docs[0].doc_id} ---")
    print(docs[0].text[:400])