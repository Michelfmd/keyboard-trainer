import unittest
from random import Random
from string import Formatter

from app.data.words import SPANISH_WORDS, WORD_LISTS
from app.modes.words import WordsMode
from app.ui.i18n import SPANISH, translate


class LanguageTests(unittest.TestCase):
    def test_spanish_words_with_each_difficulty(self) -> None:
        for difficulty, lengths in (
            ("easy", {1, 2}),
            ("medium", {3, 4}),
            ("hard", {20}),
        ):
            mode = WordsMode(rng=Random(4), difficulty=difficulty, language="es")
            mode.start()
            words = mode.target.split()
            self.assertIn(len(words), lengths)
            self.assertTrue(set(words) <= set(SPANISH_WORDS))
            mode.reset()
            self.assertEqual(mode.language, "es")
            self.assertTrue(set(mode.target.split()) <= set(SPANISH_WORDS))

    def test_spanish_characters_recorded_correctly(self) -> None:
        mode = WordsMode(count=len(SPANISH_WORDS), language="es")
        mode.start()
        self.assertIn("ñ", mode.target)
        self.assertIn("é", mode.target)
        for key in mode.target:
            mode.handle_input(key)
        self.assertTrue(mode.is_finished())
        self.assertTrue(all(event.correct for event in mode.session.events))

    def test_invalid_language(self) -> None:
        with self.assertRaises(ValueError):
            WordsMode(language="fr")

    def test_word_lists_are_unique(self) -> None:
        for words in WORD_LISTS.values():
            self.assertEqual(len(words), len(set(words)))

    def test_translation_and_formatting(self) -> None:
        self.assertEqual(translate("en", "Settings"), "Settings")
        self.assertEqual(translate("es", "Settings"), "Ajustes")
        self.assertEqual(translate("es", "Keyboard Trainer"), "Keyboard Trainer")
        self.assertEqual(
            translate("es", "{position} / {total} characters", position=2, total=4),
            "2 / 4 caracteres",
        )

    def test_translations_preserve_format_fields(self) -> None:
        formatter = Formatter()
        for english, spanish in SPANISH.items():
            with self.subTest(text=english):
                source = {field for _, field, _, _ in formatter.parse(english) if field}
                translated = {
                    field for _, field, _, _ in formatter.parse(spanish) if field
                }
                self.assertEqual(source, translated)
