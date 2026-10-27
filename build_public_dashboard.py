"""Build the data-only Plotly figures used by the public GitHub Pages view.

This intentionally exports visual arrays only.  It removes sample identifiers,
literature names, hover text, selection state, and all database-management UI.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from plotly.utils import PlotlyJSONEncoder


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = Path(__file__).resolve().parent / "data"
sys.path.insert(0, str(ROOT / "dashboard"))

import app  # noqa: E402


PRIVATE_TRACE_KEYS = {
    "customdata", "hovertemplate", "hovertext", "text", "selected", "unselected",
    "name", "legendgroup",
}
PRIVATE_LAYOUT_KEYS = {"meta"}


def public_figure(figure):
    """Remove record-level and source-level presentation fields from a figure."""
    payload = figure.to_plotly_json()
    for trace in payload.get("data", []):
        for key in PRIVATE_TRACE_KEYS:
            trace.pop(key, None)
        trace["hoverinfo"] = "skip"
        trace["showlegend"] = False
    layout = payload.setdefault("layout", {})
    for key in PRIVATE_LAYOUT_KEYS:
        layout.pop(key, None)
    layout["showlegend"] = False
    layout.pop("title", None)
    return payload


def write(name: str, figure) -> None:
    destination = OUTPUT / f"{name}.json"
    destination.write_text(
        json.dumps(public_figure(figure), cls=PlotlyJSONEncoder, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(f"{destination.name}: {destination.stat().st_size / 1024 / 1024:.2f} MiB")


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    figure1_data = app.prepare_view_data("main-a")
    figure1_map, figure1_bc = app.split_figure1(figure1_data)
    write("figure1_map", figure1_map)
    write("figure1_bc", figure1_bc)
    for view, filename in (("main-a", "figure2a"), ("main-b", "figure2b"), ("main-c", "figure2c")):
        write(filename, app.build_figure(app.prepare_view_data(view), view))


if __name__ == "__main__":
    main()
