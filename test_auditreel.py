import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from auditreel import storyboard


HERE = Path(__file__).resolve().parent
EXAMPLE = json.loads((HERE / "synthetic_audit.json").read_text(encoding="utf-8"))


class AuditReelTest(unittest.TestCase):
    def setUp(self):
        self.spec = copy.deepcopy(EXAMPLE)

    def test_timed_script_with_sources(self):
        frames = storyboard(self.spec)["frames"]
        self.assertEqual([(x["start_s"], x["end_s"]) for x in frames],
                         [(0, 3), (3, 9), (9, 15), (15, 21)])
        self.assertEqual([x["evidence_ids"] for x in frames],
                         [[], ["SYN-01"], ["SYN-02"], ["SYN-03"]])

    def test_missing(self):
        self.spec["evidence"].pop()
        with self.assertRaisesRegex(ValueError, "Missing"):
            storyboard(self.spec)

    def test_stale_and_future(self):
        for day in ("2026-11-16", "2026-11-25"):
            self.spec["evidence"][0]["observed_on"] = day
            with self.subTest(day=day), self.assertRaisesRegex(ValueError, "Stale"):
                storyboard(self.spec)

    def test_conflict_and_corroboration(self):
        second = dict(self.spec["evidence"][0], id="SYN-04")
        self.spec["evidence"].append(second)
        self.assertEqual(storyboard(self.spec)["frames"][1]["evidence_ids"], ["SYN-01", "SYN-04"])
        second["observation"] = "A session length is visible."
        with self.assertRaisesRegex(ValueError, "Conflicting"):
            storyboard(self.spec)

    def test_real_input_flag_rejected(self):
        self.spec["synthetic"] = False
        with self.assertRaisesRegex(ValueError, "synthetic"):
            storyboard(self.spec)

    def test_duplicate_id_rejected(self):
        self.spec["evidence"][1]["id"] = self.spec["evidence"][0]["id"]
        with self.assertRaisesRegex(ValueError, "unique"):
            storyboard(self.spec)

    def test_cli_emits_no_partial_storyboard_when_blocked(self):
        self.spec["evidence"].pop()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text(json.dumps(self.spec), encoding="utf-8")
            run = subprocess.run([sys.executable, str(HERE / "auditreel.py"), str(path)],
                                 capture_output=True, text=True)
        self.assertEqual(run.returncode, 2)
        self.assertEqual(run.stdout, "")
        self.assertIn("Missing evidence", run.stderr)
