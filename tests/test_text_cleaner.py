"""
Unit-Tests fuer TextCleaner
"""

import unittest
import sys
from pathlib import Path

# Parent-Ordner zum Pfad hinzufuegen, damit text_cleaner importiert werden kann
sys.path.insert(0, str(Path(__file__).parent.parent))

from text_cleaner import TextCleaner


class TestTextCleaner(unittest.TestCase):
    def setUp(self):
        self.cleaner = TextCleaner()

    def test_fix_lists_and_enumerations_bullets(self):
        text = "\u2022 Erster Punkt\n\u2022 Zweiter Punkt"
        result = self.cleaner.fix_lists_and_enumerations(text)
        self.assertNotIn("\u2022", result)
        self.assertIn("Erster Punkt", result)
        self.assertIn("Zweiter Punkt", result)

    def test_fix_lists_and_enumerations_letters(self):
        text = "a) Option A\nb) Option B"
        result = self.cleaner.fix_lists_and_enumerations(text)
        self.assertIn("erstens, Option A", result)
        self.assertIn("zweitens, Option B", result)

    def test_fix_lists_and_enumerations_numbers(self):
        text = "1. Schritt eins\n2. Schritt zwei"
        result = self.cleaner.fix_lists_and_enumerations(text)
        self.assertIn("Punkt eins, Schritt eins", result)
        self.assertIn("Punkt zwei, Schritt zwei", result)

    def test_fix_urls_domain_mode(self):
        text = "Besuche uns unter https://www.example.com/path oder www.test.de."
        result = self.cleaner.fix_urls(text, mode="domain")
        self.assertIn("Link zu example.com", result)
        self.assertIn("Link zu test.de", result)
        self.assertNotIn("https://", result)

    def test_fix_urls_remove_mode(self):
        text = "Mehr Infos unter https://example.com"
        result = self.cleaner.fix_urls(text, mode="remove")
        self.assertNotIn("example.com", result)
        self.assertNotIn("https", result)

    def test_fix_thousands(self):
        text = "Die Zahl 1.234 ist groß, und 5.678.900 ist riesig."
        result = self.cleaner.fix_thousands(text)
        self.assertIn("1234", result)
        self.assertIn("5678900", result)
        self.assertNotIn("1.234", result)
        self.assertNotIn("5.678.900", result)

    def test_remove_line_breaks_in_sentences(self):
        text = "Hast du dich jemals gefragt,\nwie KI-Stimmen funktionieren?"
        result = self.cleaner.remove_line_breaks_in_sentences(text)
        self.assertIn("Hast du dich jemals gefragt, wie KI-Stimmen funktionieren?", result)
        self.assertNotIn("gefragt,\nwie", result)

    def test_clean_integration(self):
        text = """Hast du dich jemals gefragt,
wie KI-Stimmen funktionieren?

\u2022 Erster Punkt
\u2022 Zweiter Punkt

Die Zahl 1.234 ist groß.
Besuche uns unter https://example.com."""
        result = self.cleaner.clean(text)
        # Sätze sollten verbunden sein
        self.assertIn("Hast du dich jemals gefragt, wie KI-Stimmen funktionieren?", result)
        # Aufzählungen bereinigt
        self.assertIn("Erster Punkt", result)
        self.assertIn("Zweiter Punkt", result)
        # Tausenderpunkte entfernt
        self.assertIn("1234", result)
        # URLs bereinigt
        self.assertIn("Link zu example.com", result)

    def test_normalize_whitespace_paragraphs(self):
        text = "Erster Absatz\n\n\n\nZweiter Absatz"
        result = self.cleaner.normalize_whitespace(text)
        self.assertEqual(result, "Erster Absatz\n\nZweiter Absatz")


if __name__ == "__main__":
    unittest.main()
