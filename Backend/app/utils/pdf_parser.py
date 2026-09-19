from pypdf import PdfReader
from pathlib import Path

def extract_text_from_pdf(path:str | Path) ->str :
    reader=PdfReader(str(path))
    pages: list[str] = []

    for page in reader.pages:
        text=page.extract_text() or ""
        pages.append(text)

    return "\n\n".join(pages)