from pathlib import Path
import pypdf

pdfs = sorted(Path(".data_cache/pdfs").glob("*.pdf"))

[print(f"{pdf.name}: {len(pypdf.PdfReader(str(pdf)).pages)} pages") for pdf in pdfs]

print(
    f"\nTotal: {sum(len(pypdf.PdfReader(str(pdf)).pages) for pdf in pdfs)} pages across {len(pdfs)} PDFs"
)
