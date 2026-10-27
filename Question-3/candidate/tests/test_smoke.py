from app.worker import extract_document

def test_extraction_stub():
    assert extract_document("https://example.com/invoice.pdf")["pages"] == 2
