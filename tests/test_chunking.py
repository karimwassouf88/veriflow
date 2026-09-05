from app.rag.chunking import chunk_text

def test_chunk_text_splits_long_text():
    text = "\n\n".join([f"Paragraph {i} " + ("word " * 50) for i in range(10)])
    chunks = chunk_text(text, chunk_size=300, overlap=50)
    assert len(chunks) > 1
    assert all(len(c) <= 350 for c in chunks)

def test_chunk_text_handles_short_text():
    assert chunk_text("Just one short paragraph.") == ["Just one short paragraph."]

def test_chunk_text_handles_empty_text():
    assert chunk_text("") == []