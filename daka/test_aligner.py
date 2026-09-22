import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from daka import daka


class SpecialDaysArchiveTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / "config.json"
        self.path.write_text(json.dumps({
            "start_date": "2026-08-27", "start_tray": 51,
            "end_tray": None, "default_days": 7,
            "special_days": {"55": 4, "57": 5},
            "completed_days": {"51": 7, "52": 7, "53": 7},
        }))
        patcher = patch.object(daka, "ALIGNER_CONFIG_FILE", str(self.path))
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_future_and_current_special_days_are_retained(self):
        original = self.path.read_bytes()
        for day in (22, 25, 27):
            config = daka.load_aligner_config(date(2026, 9, day))
            self.assertEqual(config["special_days"], {55: 4, 57: 5})
            self.assertEqual(self.path.read_bytes(), original)

    def test_archive_on_end_day_preserves_timeline_and_is_idempotent(self):
        before = daka.load_aligner_config(date(2026, 9, 22))
        after = daka.load_aligner_config(date(2026, 9, 28))
        stored = json.loads(self.path.read_text())
        self.assertEqual(list(stored)[0], "special_days")
        self.assertEqual(stored["start_date"], "2026-08-27")
        self.assertEqual(stored["start_tray"], 51)
        self.assertIsNone(stored["end_tray"])
        self.assertEqual(stored["default_days"], 7)
        self.assertEqual(stored["special_days"], {"57": 5})
        self.assertEqual(stored["completed_days"]["55"], 4)
        for when in (date(2026, 9, 25), date(2026, 9, 28), date(2026, 10, 1)):
            self.assertEqual(daka.calculate_aligner_status(before, when),
                             daka.calculate_aligner_status(after, when))
        with patch.object(daka.os, "replace") as replace:
            daka.load_aligner_config(date(2026, 9, 28))
            replace.assert_not_called()

    def test_multiple_finished_specials_are_archived(self):
        config = daka.load_aligner_config(date(2026, 10, 10))
        self.assertEqual(config["special_days"], {})
        self.assertEqual(config["completed_days"][55], 4)
        self.assertEqual(config["completed_days"][57], 5)

    def test_existing_completed_days_win(self):
        raw = json.loads(self.path.read_text())
        raw["special_days"]["53"] = 15
        self.path.write_text(json.dumps(raw))
        config = daka.load_aligner_config(date(2026, 9, 22))
        self.assertEqual(config["completed_days"][53], 7)
        self.assertNotIn(53, config["special_days"])
        self.assertEqual(daka.calculate_aligner_status(config, date(2026, 9, 22)),
                         {"kind": "wearing", "tray": 54, "days": 2})

    def test_write_failure_preserves_original_file(self):
        original = self.path.read_bytes()
        with patch.object(daka.os, "replace", side_effect=OSError("write failed")):
            with self.assertRaisesRegex(ValueError, "无法更新"):
                daka.load_aligner_config(date(2026, 9, 28))
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(list(self.path.parent.glob(".aligner_config-*.tmp")), [])

    def test_archive_preserves_extra_configuration(self):
        raw = json.loads(self.path.read_text())
        raw["note"] = "保留自定义备注"
        self.path.write_text(json.dumps(raw))
        daka.load_aligner_config(date(2026, 9, 28))
        self.assertEqual(json.loads(self.path.read_text())["note"], raw["note"])


if __name__ == "__main__":
    unittest.main()
