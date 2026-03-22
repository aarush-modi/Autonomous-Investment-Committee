import re


SEC_SECTION_PATTERN = re.compile(
    r"(?=Item\s+\d+[A-Za-z]?[\.\:\-\s])", re.IGNORECASE
)


def chunk_sec_filing(text: str, max_chunk_size: int = 1000) -> list[dict]:
    sections = SEC_SECTION_PATTERN.split(text)
    chunks = []

    for section in sections:
        section = section.strip()
        if not section:
            continue

        if len(section) <= max_chunk_size:
            chunks.append({"text": section, "type": "section"})
        else:
            sub_chunks = recursive_chunk(section, max_chunk_size)
            chunks.extend(sub_chunks)

    return chunks


def recursive_chunk(text: str, max_chunk_size: int = 1000, overlap: int = 100) -> list[dict]:
    if len(text) <= max_chunk_size:
        return [{"text": text, "type": "chunk"}]

    # Try splitting on double newlines first
    paragraphs = text.split("\n\n")
    if len(paragraphs) > 1:
        return _merge_splits(paragraphs, max_chunk_size, overlap)

    # Fall back to single newlines
    lines = text.split("\n")
    if len(lines) > 1:
        return _merge_splits(lines, max_chunk_size, overlap)

    # Last resort: split on sentences
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return _merge_splits(sentences, max_chunk_size, overlap)


def _merge_splits(parts: list[str], max_chunk_size: int, overlap: int) -> list[dict]:
    chunks = []
    current = ""

    for part in parts:
        if current and len(current) + len(part) + 1 > max_chunk_size:
            chunks.append({"text": current.strip(), "type": "chunk"})
            # Keep overlap from end of current chunk
            current = current[-overlap:] + "\n" + part if overlap else part
        else:
            current = current + "\n" + part if current else part

    if current.strip():
        chunks.append({"text": current.strip(), "type": "chunk"})

    return chunks
