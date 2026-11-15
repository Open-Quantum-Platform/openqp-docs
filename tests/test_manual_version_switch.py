import hashlib
import unittest

from tools.stage_manual_version_switch import SWITCH, VERSION_ROW, add_switch


class ManualVersionSwitchTest(unittest.TestCase):
    def test_only_inserts_the_switch(self):
        home = b"<article>" + VERSION_ROW + b"\n<p>Existing manual.</p></article>"
        staged = add_switch(home, hashlib.sha256(home).hexdigest())
        self.assertEqual(staged.replace(SWITCH, b"", 1), home)
        self.assertEqual(staged.count(b'href="/manual/1.4/"'), 1)

    def test_rejects_wrong_or_ambiguous_source(self):
        with self.assertRaisesRegex(ValueError, "reviewed source"):
            add_switch(VERSION_ROW, "0" * 64)
        for home in (b"", VERSION_ROW * 2, VERSION_ROW + SWITCH):
            with self.subTest(home=home):
                with self.assertRaisesRegex(ValueError, "one 1.3 version row"):
                    add_switch(home, hashlib.sha256(home).hexdigest())
