import xml.etree.ElementTree as ET
from collections import defaultdict
from lxml import etree

def analyze_dblp_structure(file_path, limit=None):
    context = etree.iterparse(file_path, events=("end",), recover=True)

    record_types = defaultdict(int)
    field_names = defaultdict(int)

    count = 0

    for event, elem in context:
        parent = elem.getparent()

        if parent is not None and parent.tag == "dblp":
            record_type = elem.tag

            record_types[record_type] += 1

            for child in elem:
                field_names[child.tag] += 1

            count += 1
            elem.clear()

            if limit and count >= limit:
                break

    return record_types, field_names

import xml.etree.ElementTree as ET
from lxml import etree
import pandas as pd

def parse_dblp(file_path, limit=500_000):
    records = []
    context = etree.iterparse(file_path, events=("end",), recover=True)
    count = 0
    for event, elem in context:
        if elem.getparent() is not None and elem.getparent().tag == "dblp":
            record = {"type": elem.tag}
            for child in elem:
                if child.tag in ("title", "year", "author", "booktitle", "pages"):
                    if child.tag == "author":
                        record.setdefault("authors", []).append(child.text)
                    else:
                        record[child.tag] = child.text
            records.append(record)
            elem.clear()
            count += 1
            if limit and count >= limit:
                break
    return pd.DataFrame(records)


if __name__ == "__main__":
    file_path = "dblp.xml"

    record_types, field_names = analyze_dblp_structure(file_path, limit=10_000)



    print("\n=== RECORD TYPES ===")
    for k, v in sorted(record_types.items(), key=lambda x: -x[1]):
        print(f"{k}: {v}")

    print("\n=== FIELD NAMES ===")
    for k, v in sorted(field_names.items(), key=lambda x: -x[1]):
        print(f"{k}: {v}")

    df = parse_dblp("dblp.xml", limit=10_000)
    
    df["authors"] = df["authors"].apply(
        lambda x: ";".join(x) if isinstance(x, list) else ""
    )

    df["year"] = pd.to_numeric(df["year"], errors="coerce")

    df.to_csv("dblp_sample.csv", index=False)