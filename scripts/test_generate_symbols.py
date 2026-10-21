import unittest

from generate_symbols import apply_manual, render


class ManualSymbolsTests(unittest.TestCase):
    def test_alias_replacement_and_missing_function_insertion(self):
        sections = [{
            "name": ".main", "vram": 0x80000400, "size": 0x100,
            "functions": [{"name": "suffixed_alias", "vram": 0x80000410, "size": 8}],
        }]
        manual = [{"name": ".main", "functions": [
            {"name": "canonical", "vram": 0x80000410, "size": 8},
            {"name": "missing", "vram": 0x80000420, "size": 4},
        ]}]
        apply_manual(sections, manual)
        self.assertEqual(sections[0]["functions"], manual[0]["functions"])
        # Reapplying overrides must not duplicate entries.
        apply_manual(sections, manual)
        self.assertEqual(sections[0]["functions"], manual[0]["functions"])

    def test_reject_moved_manual_symbol(self):
        sections = [{
            "name": ".main", "vram": 0x80000400, "size": 0x100,
            "functions": [{"name": "moved", "vram": 0x80000440, "size": 4}],
        }]
        manual = [{"name": ".main", "functions": [
            {"name": "moved", "vram": 0x80000410, "size": 4},
        ]}]
        with self.assertRaisesRegex(ValueError, "moved"):
            apply_manual(sections, manual)

    def test_reject_out_of_section_override(self):
        sections = [{"name": ".main", "vram": 0x1000, "size": 4, "functions": []}]
        manual = [{"name": ".main", "functions": [{"name": "bad", "vram": 0x1000, "size": 8}]}]
        with self.assertRaisesRegex(ValueError, "outside section"):
            apply_manual(sections, manual)

    def test_stable_order_for_equal_addresses(self):
        section = {
            "name": ".data", "vram": 0x1000, "size": 8,
            "symbols": [{"name": "z", "vram": 0x1000}, {"name": "a", "vram": 0x1000}],
        }
        first = render([section], "symbols")
        section["symbols"].reverse()
        self.assertEqual(first, render([section], "symbols"))


if __name__ == "__main__":
    unittest.main()
