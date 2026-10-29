"""scripts/set_first_pomo.py の対象日の決め方と書き込み・読み取りを確認する。"""
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import date, datetime
from pathlib import Path

from scripts.set_first_pomo import main, read_first_pomo, target_date, write_first_pomo


class TargetDateTest(unittest.TestCase):
    def test_evening_means_tomorrow(self):
        self.assertEqual(target_date(datetime(2026, 10, 29, 23, 30)), date(2026, 10, 30))

    def test_after_midnight_before_five_is_still_the_same_night(self):
        self.assertEqual(target_date(datetime(2026, 10, 30, 0, 20)), date(2026, 10, 30))
        self.assertEqual(target_date(datetime(2026, 10, 30, 4, 59)), date(2026, 10, 30))
        self.assertEqual(target_date(datetime(2026, 10, 30, 5, 0)), date(2026, 10, 31))

    def test_today_flag_and_explicit_date_win(self):
        now = datetime(2026, 10, 29, 23, 30)
        self.assertEqual(target_date(now, today=True), date(2026, 10, 29))
        self.assertEqual(target_date(now, explicit=date(2026, 11, 1), today=True), date(2026, 11, 1))


class FileRoundTripTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "first_pomo.txt"

    def tearDown(self):
        self.tmp.cleanup()

    def test_write_then_read(self):
        write_first_pomo(self.path, date(2026, 10, 30), "Anki「SC重点」を1ポモ")
        self.assertEqual(read_first_pomo(self.path), (date(2026, 10, 30), "Anki「SC重点」を1ポモ"))
        text = self.path.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("# 明日の最初の1ポモ"))
        self.assertTrue(text.endswith("2026-10-30\nAnki「SC重点」を1ポモ\n"))

    def test_hand_written_file_with_slash_date_and_multiple_lines(self):
        self.path.write_text("2026/10/30\nAnki\n終わったら午後問3\n", encoding="utf-8")
        self.assertEqual(read_first_pomo(self.path), (date(2026, 10, 30), "Anki / 終わったら午後問3"))

    def test_missing_or_dateless_file_is_unset(self):
        self.assertEqual(read_first_pomo(self.path), (None, ""))
        self.path.write_text("# ヘッダだけ\n", encoding="utf-8")
        self.assertEqual(read_first_pomo(self.path), (None, ""))

    def test_main_writes_tomorrow_and_show_reads_it_back(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = main(["Anki", "1ポモ", "--path", str(self.path), "--now", "2026-10-29T23:30"])
        self.assertEqual(code, 0)
        self.assertIn("10/30 の最初の1ポモ: Anki 1ポモ", out.getvalue())
        self.assertEqual(read_first_pomo(self.path), (date(2026, 10, 30), "Anki 1ポモ"))
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(main(["--show", "--path", str(self.path)]), 0)
        self.assertEqual(out.getvalue().strip(), "2026-10-30 の最初の1ポモ: Anki 1ポモ")

    def test_main_refuses_empty_text(self):
        with redirect_stdout(io.StringIO()):
            code = main(["--path", str(self.path), "--now", "2026-10-29T23:30"])
        self.assertEqual(code, 1)
        self.assertFalse(self.path.exists())


if __name__ == "__main__":
    unittest.main()
