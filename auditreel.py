"""Build an offline storyboard from synthetic audit evidence."""
import argparse
import json
from datetime import date
from pathlib import Path


def fields(value, expected, label):
    if type(value) is not dict or value.keys() != set(expected.split()):
        raise ValueError(f"Invalid fields in {label}")


def label(value, name):
    if not isinstance(value, str) or not value.strip() or "\n" in value:
        raise ValueError(f"Invalid {name}")
    return value.strip()


def iso_date(value):
    value = label(value, "date")
    parsed = date.fromisoformat(value)
    if parsed.isoformat() != value:
        raise ValueError("Dates must use YYYY-MM-DD")
    return parsed


def storyboard(spec):
    fields(spec, "synthetic as_of max_age_days topics evidence", "spec")
    if spec["synthetic"] is not True:
        raise ValueError("Only synthetic evidence is accepted")
    as_of = iso_date(spec["as_of"])
    max_age = spec["max_age_days"]
    if type(max_age) is not int or not 0 <= max_age <= 90:
        raise ValueError("max_age_days must be an integer between 0 and 90")
    if not isinstance(spec["topics"], list) or not 1 <= len(spec["topics"]) <= 4:
        raise ValueError("Specify one to four topics")
    topics = [label(x, "topic") for x in spec["topics"]]
    if len(topics) != len(set(topics)):
        raise ValueError("Topics must be unique")
    if not isinstance(spec["evidence"], list):
        raise ValueError("evidence must be a list")

    by_topic = {name: [] for name in topics}
    ids = set()
    for row in spec["evidence"]:
        fields(row, "id topic observed_on observation", "evidence record")
        evidence_id = label(row["id"], "evidence ID")
        if not evidence_id.startswith("SYN-") or len(evidence_id) <= 4 or evidence_id in ids:
            raise ValueError("Evidence IDs must be unique and start with SYN-")
        ids.add(evidence_id)
        topic = label(row["topic"], "evidence topic")
        if topic not in by_topic:
            raise ValueError(f"Undeclared topic: {topic}")
        observed = iso_date(row["observed_on"])
        age = (as_of - observed).days
        if not 0 <= age <= max_age:
            raise ValueError(f"Stale or future-dated evidence: {evidence_id}")
        finding = label(row["observation"], "observation")
        if len(finding) > 100:
            raise ValueError(f"Observation too long: {evidence_id}")
        by_topic[topic].append((finding, evidence_id))

    frames = [{"start_s": 0, "end_s": 3, "narration": "Here is an audit of a fictional page.",
               "visual": "Display a synthetic-demo title card", "evidence_ids": []}]
    for i, (topic, rows) in enumerate(by_topic.items()):
        if not rows:
            raise ValueError(f"Missing evidence for {topic}")
        if len({finding for finding, _ in rows}) != 1:
            raise ValueError(f"Conflicting evidence for {topic}")
        start = 3 + 6 * i
        sources = sorted(evidence_id for _, evidence_id in rows)
        frames.append({"start_s": start, "end_s": start + 6, "narration": rows[0][0],
                       "visual": f"Show topic card: {topic}", "evidence_ids": sources})
    return {"synthetic": True, "as_of": spec["as_of"], "frames": frames}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        result = storyboard(json.loads(args.input.read_text(encoding="utf-8")))
    except (UnicodeError, OSError, ValueError) as exc:
        parser.exit(2, f"Storyboard blocked: {exc}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
