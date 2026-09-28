"""Extract experimental species and cigarette-butt materials with a local LLM.

Input workbooks must contain paragraph-level article data with the columns used
by the manuscript workflow. The script writes one checkpointed XLSX file and
never downloads or redistributes article full text.
"""
from argparse import ArgumentParser
from pathlib import Path
import json

import ollama
import pandas as pd


SYSTEM_PROMPT = """You are a scientific data extractor.
Return one valid JSON object with exactly two equally sized arrays: species and
material. Extract only organisms directly tested by the authors of the current
article and the cigarette-butt material used with each organism. Do not extract
organisms mentioned only in citations, reviews, introductions, or comparisons
with previous studies. Use null when a value is not explicitly reported. Do not
write any text outside the JSON object."""

REQUIRED_COLUMNS = {
    "title", "article_id", "sentence_id", "abstract", "section", "text",
    "doi", "year", "authors",
}


def extract(text: str, title: str, model: str) -> str:
    response = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Title: {title}\nPassage: {text}"},
        ],
        options={"temperature": 0.0, "num_ctx": 20000},
    )
    content = response.message.content.strip()
    parsed = json.loads(content)
    if set(parsed) != {"species", "material"}:
        raise ValueError("Unexpected extraction keys")
    if len(parsed["species"]) != len(parsed["material"]):
        raise ValueError("Species and material arrays have different lengths")
    return json.dumps(parsed, ensure_ascii=False)


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("input_dir", type=Path, help="Directory of article XLSX files")
    parser.add_argument("output", type=Path, help="Output XLSX checkpoint")
    parser.add_argument("--model", default="gpt-oss:120b")
    args = parser.parse_args()

    files = sorted(args.input_dir.glob("*.xlsx"))
    if not files:
        raise FileNotFoundError(f"No XLSX files found in {args.input_dir}")
    data = pd.concat((pd.read_excel(path) for path in files), ignore_index=True)
    missing = REQUIRED_COLUMNS.difference(data.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    results = []
    args.output.parent.mkdir(parents=True, exist_ok=True)
    for index, row in data.iterrows():
        try:
            extraction = extract(str(row["text"]), str(row["title"]), args.model)
        except (json.JSONDecodeError, ValueError) as error:
            extraction = json.dumps({"error": str(error)}, ensure_ascii=False)
        results.append({
            "title": row["title"], "article_id": row["article_id"],
            "sentence_id": row["sentence_id"], "model": args.model,
            "abstract": row["abstract"], "section": row["section"],
            "text": row["text"], "extraction": extraction,
            "DOI": row["doi"], "year": row["year"], "authors": row["authors"],
        })
        pd.DataFrame(results).to_excel(args.output, index=False)
        print(f"Processed {index + 1}/{len(data)}")


if __name__ == "__main__":
    main()
