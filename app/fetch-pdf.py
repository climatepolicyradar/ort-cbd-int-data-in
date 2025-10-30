import asyncio
import csv
import os
from io import StringIO

from app.csv_api import OrtCbdIntCsv
from playwright.async_api import async_playwright

PRINT_HIDE_TEMPLATE = """
@media print {
  .header, .footer, footer { display: none !important; }
  button { display: none !important; }
  #slaask-button { display: none !important; }
  #slaask-button-cross { display: none !important; }
  #slaask-button-close { display: none !important; }
}
"""


async def html_url_to_pdf(url: str, output_path: str) -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle", timeout=60000)
        await page.add_style_tag(content=PRINT_HIDE_TEMPLATE)
        await page.emulate_media(media="print")
        await page.pdf(path=output_path, format="A4", print_background=True)
        await browser.close()


with open(".data_cache/source-data.csv", "r", encoding="utf-8-sig") as f:
    source_data = f.read()

reader = csv.DictReader(StringIO(source_data))
models: list[OrtCbdIntCsv] = []

for row in reader:
    try:
        model = OrtCbdIntCsv(**row)
        models.append(model)
    except Exception as e:
        print(f"Error parsing row: {e}")
        continue

for model in models:
    # if the PDF doesn't exist, fethc it
    if not os.path.exists(f"./.data_cache/pdfs/{model.unique_id}.pdf"):
        print(f"Fetching PDF for {model.unique_id}")
        asyncio.run(
            html_url_to_pdf(model.url, f"./.data_cache/pdfs/{model.unique_id}.pdf")
        )
        print(f"PDF fetched for {model.unique_id}")
    else:
        print(f"PDF already exists for {model.unique_id}")
