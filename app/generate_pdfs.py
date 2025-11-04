import csv
from io import StringIO
from pathlib import Path

from app.csv_api import OrtCbdIntCsv
from markdown_pdf import MarkdownPdf, Section

root = Path(__file__).resolve().parent.parent

Path(".data_cache/pdfs").mkdir(exist_ok=True)

with open(root / ".data_cache/source-data.csv", "r", encoding="utf-8") as f:
    source_data = f.read()

reader = csv.DictReader(StringIO(source_data))
models = []
entries = []
for row in reader:
    try:
        model = OrtCbdIntCsv(**row)
        models.append(model)
    except Exception as e:
        print(f"Error parsing row: {e}")
        continue


def _append_if_present(heading: str, value: str) -> str:
    if value == "":
        return ""
    return f"## {heading}\n{value}\n\n\n"


governments = set(model.government for model in models)

for government in governments:
    print(f"Generating PDF for {government}")
    pdf = MarkdownPdf(toc_level=2, optimize=True)
    text = ""
    text += "![Header](app/header.png)\n\n\n"
    text += f"# {government} National Targets. GBF-NT\n\n\n"

    for model in models:
        if model.government != government:
            continue
        text += f"## {model.national_target_title}\n\n\n"

        # Subsequent sections (H2) only if present
        text += _append_if_present("Published on", model.published_on)
        text += _append_if_present("URL", model.url)
        text += _append_if_present("Unique ID", model.unique_id)
        text += _append_if_present("Government", model.government)
        text += _append_if_present("Description", model.description)
        text += _append_if_present("Main policy measures", model.main_policy_measures)
        text += _append_if_present("Global goals", model.global_goals)
        text += _append_if_present("Global targets", model.global_targets)
        text += _append_if_present(
            "Degree of alignment by target", model.degree_of_alignment_by_target
        )
        text += _append_if_present("Aspects covered", model.aspects_covered)
        text += _append_if_present(
            "Considerations for implementation from Section C",
            model.implementation_considerations,
        )
        text += _append_if_present(
            "Explain considerations", model.explain_considerations
        )
        text += _append_if_present("Headline indicators", model.headline_indicators)
        text += _append_if_present("Binary indicators", model.binary_indicators)
        text += _append_if_present("Component indicators", model.component_indicators)
        text += _append_if_present(
            "Complementary indicators", model.complementary_indicators
        )
        text += _append_if_present(
            "Other national indicators", model.other_national_indicators
        )
        text += _append_if_present("Non-state commitments", model.non_state_commitments)
        text += _append_if_present("Overlaps or links", model.overlaps_or_links)
        text += _append_if_present(
            "Commitments and actors", model.commitments_and_actors
        )
        text += _append_if_present(
            "Means of implementation", model.means_of_implementation
        )
        text += _append_if_present(
            "Please explain (means of implementation)",
            model.explain_means_of_implementation,
        )
        text += _append_if_present(
            "Additional explanation", model.additional_explanation
        )
        text += _append_if_present("Any other information", model.any_other_information)
        text += "---\n\n\n"

    pdf.add_section(
        Section(text),
        user_css="h1 {font-size: 14px;} h2 {font-size: 12px;} p {font-size: 10px;}",
    )
    pdf.save(str(root / f".data_cache/pdfs/{government}.pdf"))
