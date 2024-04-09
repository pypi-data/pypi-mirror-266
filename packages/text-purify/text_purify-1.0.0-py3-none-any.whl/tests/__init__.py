import unittest
import text_purify


class Test(unittest.TestCase):
    def test_remove_special_characters(self):
        text = "Jakiś! tekst? z #różnymi$ znakami& specjalnymi*."
        clean_text = text_purify.remove_special_characters(text)
        self.assertEqual(clean_text, 'Jakiś tekst z różnymi znakami specjalnymi')

    def test_remove_html_tags(self):
        text_with_html = "To jest <strong>ważny</strong> tekst z <a href='link' target = '_blank'>linkiem</a>."
        clean_text = text_purify.remove_html_tags(text_with_html)
        self.assertEqual(clean_text, 'To jest ważny tekst z linkiem.')

    def test_remove_double_spaces(self):
        text = 'this   is test  text :)'
        clean_text = text_purify.remove_double_spaces(text)
        self.assertEqual(clean_text, 'this is test text :)')
