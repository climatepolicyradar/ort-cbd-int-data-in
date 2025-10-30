# ort-cbd-int

## Description

Extracts data from [ort.cbd.int](https://ort.cbd.int/national-targets?recordTypes=nationalTarget7)
and generates a `db_state` JSON file tobe consumed by the `/bulk-import` endpoint

## Usage

All data is stored in the `.data_cache` directory.

### Generate data
```
uv run pytest ./app/main.py
```

### Generate PDFs
```
uv run ./app/generate-pdfs.py
```