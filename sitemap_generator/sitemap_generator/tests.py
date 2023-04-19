# from django.test import TestCase
import unittest
from URLSanitizer import URLSanitizer


class TestURLSanitizer(unittest.TestCase):

    def test_sanitize_url(self):
        self.assertEqual(URLSanitizer.sanitize_url("/xd", "https://wp.pl"), "https://wp.pl/xd")
        # self.assertEqual(URLSanitizer.sanitize_url("https://crawler-test.com//urls/double_slash/disallowed_start", "https://crawler-test.com"), None)
        self.assertEqual(URLSanitizer.sanitize_url("https://crawler-test.com/?parameter-on-hostname-root=parameter-value", "https://crawler-test.com"), "https://crawler-test.com/?parameter-on-hostname-root=parameter-value")
        self.assertEqual(URLSanitizer.sanitize_url("/", "https://www.test.com"), "https://www.test.com")

    def test_is_file(self):
        self.assertTrue(URLSanitizer.is_file("/test/index.html"))
        self.assertTrue(URLSanitizer.is_file("test.pdf"))
        self.assertTrue(URLSanitizer.is_file("https://testsite.com/test/index.gif"))

    def test_is_email(self):
        self.assertTrue(URLSanitizer.is_email("mailto:pzjudo@pzjudo.pl"))
        self.assertTrue(URLSanitizer.is_email("pzjudo@pzjudo.pl"))
        self.assertFalse(URLSanitizer.is_email("/not_mail"))

    # def test_is_image_by_extension(self):
    #     pass
    #
    # def test_is_image_by_header(self):
    #     pass
    #
    # def test_is_doc_by_extension(self):
    #     pass
    #
    # def test_is_doc_by_header(self):
    #     pass


if __name__ == '__main__':
    unittest.main()
