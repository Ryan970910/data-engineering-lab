"""Plan the two filename changes; deliberately no filesystem or DB side effects."""

from pathlib import PureWindowsPath


def plan(records, target_directory, run_date):
    selected = {}
    for record in records:
        if record["kind"] not in selected and record["modified_date"] == run_date:
            selected[record["kind"]] = record
    if "roi" not in selected:
        raise ValueError("An ROI input is required; no files were copied")
    result = []
    for kind in ("question", "roi"):
        if kind in selected:
            source = PureWindowsPath(selected[kind]["path"])
            name = source.stem.rpartition("_")[0] + ".xlsx"
            result.append({"kind": kind, "source": str(source),
                           "destination": str(PureWindowsPath(target_directory) / name)})
    return result
