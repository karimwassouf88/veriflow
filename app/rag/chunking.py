def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> list[str]:
    """Paragraph-aware chunking: packs paragraphs up to chunk_size, carrying
    the tail of each chunk forward as overlap so context isn't lost at
    boundaries. Falls back to a hard split for any single oversized paragraph."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [text.strip()] if text.strip() else []

    chunks: list[str] = []
    current = ""
    for para in paragraphs:
        if len(current) + len(para) + 1 <= chunk_size:
            current = f"{current}\n{para}".strip()
        else:
            if current:
                chunks.append(current)
            tail = current[-overlap:] if len(current) > overlap else current
            current = f"{tail}\n{para}".strip()
            while len(current) > chunk_size:
                chunks.append(current[:chunk_size])
                current = current[chunk_size - overlap:]
    if current:
        chunks.append(current)
    return chunks