from pathlib import Path

import fitz


def extract_page_link_urls(page) -> list[str]:
    urls = []
    for link in page.get_links():
        uri = link.get("uri")
        if uri:
            urls.append(uri)
    return urls


def extract_text_from_pdf(pdf_path: str) -> str:
    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError("File must be a PDF")

    document = None
    try:
        document = fitz.open(path)
        all_text = []
        for page in document:
            page_text = page.get_text("text")
            if page_text:
                all_text.append(page_text.strip())
            link_urls = extract_page_link_urls(page)
            if link_urls:
                all_text.extend(link_urls)
        return "\n\n".join(all_text)
    except Exception as error:
        raise ValueError("File is not a valid PDF") from error
    finally:
        if document is not None:
            document.close()
