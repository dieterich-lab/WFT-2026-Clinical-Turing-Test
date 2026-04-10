# CARDIO:DE Annotations: Layout and Alignment Guide

This note summarizes where the CARDIO:DE texts and annotations are stored, which format is used, and how you can implement a first alignment pipeline.

## 1. Corpus location and structure

Base path:

`/prj/doctoral_letters/MIEdeep/corpus/cardiode/54_cardiode_v1.1.2/`

Main subfolders:

- `txt/` contains plain-text discharge letters
- `cas/` contains annotation files in UIMA CAS format

Both folders are split into:

- `CARDIODE400_main`
- `CARDIODE100_heldout`

## 2. Annotation format

Each annotation document is a ZIP archive in `cas/<split>/`, for example `1.zip`.

Inside each ZIP archive:

- `cas.xmi`: annotation content in UIMA CAS XMI
- `TypeSystem.xml`: type system definition for the annotations

The plain text document for the same case is found in `txt/<split>/` with the same numeric identifier, for example:

- `cas/CARDIODE400_main/1.zip` aligns with `txt/CARDIODE400_main/1.txt`

## 3. Alignment concept (high-level)

The XMI contains annotation spans with character offsets (typically `begin` and `end`).

A minimal alignment pipeline is:

1. Match files by document ID (`N.zip` ↔ `N.txt`).
2. Parse `cas.xmi` and read annotation offsets and labels.
3. Load the corresponding plain text.
4. Extract span text via `text[begin:end]`.
5. Store results in a table (e.g., CSV) for further processing.

## 4. Minimal extraction skeleton

Example extraction of all XMI files from one split:

```bash
mkdir -p cas_xmi
for f in /prj/doctoral_letters/MIEdeep/corpus/cardiode/54_cardiode_v1.1.2/cas/CARDIODE400_main/*.zip; do
  id=$(basename "$f" .zip)
  unzip -p "$f" cas.xmi > cas_xmi/${id}.xmi
done
```

Minimal Python skeleton:

```python
from lxml import etree

def extract_spans(xmi_path, txt_path):
    with open(txt_path, "r", encoding="utf-8") as fh:
        text = fh.read()

    tree = etree.parse(xmi_path)
    root = tree.getroot()

    spans = []
    for ann in root.findall('.//*[@begin][@end]'):
        begin = int(ann.get("begin"))
        end = int(ann.get("end"))
        label = etree.QName(ann.tag).localname
        span_text = text[begin:end]
        spans.append((label, begin, end, span_text))

    return spans
```

## 5. Practical notes

- Use UTF-8 consistently when reading text and XMI.
- Validate on a small subset first (e.g., 5-10 documents).
- Use `TypeSystem.xml` (and optional INCEpTION layer/tagset files) to identify the exact annotation classes you want to keep.
- A good first output format is: `doc_id, label, begin, end, span_text`.

This should be enough to implement your own alignment/extraction logic during the project.
