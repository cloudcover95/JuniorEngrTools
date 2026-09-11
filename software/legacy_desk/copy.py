"""Shop language. Not research-paper voice."""

LABELS = {
    "allow_extrude": {
        True: "OK to build the 3D file",
        False: "Do not build yet — missing a signed height or elevation",
    },
    "interp_hypothesis": {
        True: "Guess from notes — you can edit this",
        False: "Taken from an explicit HEIGHT / ELEV line",
    },
    "rec": {
        "high_confidence": "Looks consistent",
        "review_needed": "Check the sheet before you trust it",
        "low_confidence": "Too noisy — do not use this guess",
    },
}


def speak(report: dict) -> dict:
    rec = report.get("rec") or report.get("interp", {}).get("source")
    out = dict(report)
    out["plain"] = {
        "build": LABELS["allow_extrude"].get(bool(report.get("allow_extrude")), ""),
        "height_status": LABELS["interp_hypothesis"].get(
            bool(report.get("interp_hypothesis", True)), ""
        ),
        "check": LABELS["rec"].get(report.get("rec"), report.get("rec") or ""),
        "hint": "POST /fix {\"field\":\"height\",\"value\":8,\"by\":\"nico\"} to sign a guess.",
    }
    return out
