# from django.test import TestCase
import unittest
from URLSanitizer import URLSanitizer
from RobotsHandler import RobotsHandler


class TestURLSanitizer(unittest.TestCase):

    def test_sanitize_url(self):
        self.assertEqual(URLSanitizer.sanitize_url("/xd", "https://wp.pl"), "https://wp.pl/xd")
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


    def test_is_image_by_header(self):
        self.assertTrue(URLSanitizer.is_image_by_header({'content-type':'image/gif'}))
        self.assertTrue(URLSanitizer.is_image_by_header({'content-type':'image/jpeg'}))
        self.assertTrue(URLSanitizer.is_image_by_header({'content-type':'image/png'}))
        self.assertTrue(URLSanitizer.is_image_by_header({'content-type':'image/jpg'}))
        self.assertTrue(URLSanitizer.is_image_by_header({'content-type':'image/webp'}))
        self.assertTrue(URLSanitizer.is_image_by_header({'content-type':'image/svg+xml'}))
        self.assertTrue(URLSanitizer.is_image_by_header({'content-type':'image/bmp'}))
        self.assertFalse(URLSanitizer.is_image_by_header({'content-type':'application/pdf'}))
        self.assertFalse(URLSanitizer.is_image_by_header({'Quote':'It is hard to light a candle, easy to curse the dark instead.'}))

    def test_is_doc_by_header(self):
        self.assertTrue(URLSanitizer.is_doc_by_header({'content-type':'application/pptx'}))
        self.assertTrue(URLSanitizer.is_doc_by_header({'content-type':'application/msword'}))
        self.assertTrue(URLSanitizer.is_doc_by_header({'content-type':'application/ppt'}))
        self.assertTrue(URLSanitizer.is_doc_by_header({'content-type':'application/xls'}))
        self.assertTrue(URLSanitizer.is_doc_by_header({'content-type':'application/txt'}))
        self.assertTrue(URLSanitizer.is_doc_by_header({'content-type':'application/zip'}))
        self.assertFalse(URLSanitizer.is_doc_by_header({'content-type':'image/gif'}))
        self.assertFalse(URLSanitizer.is_doc_by_header({'Quote':'Und der Haifisch der hat Tranen'}))

class TestRobotsHandler(unittest.TestCase):
    def test_join_robots_txt(self):
        self.assertEqual(RobotsHandler.join_robots_txt("https://en.wikipedia.org"), "https://en.wikipedia.org/robots.txt")
        self.assertEqual(RobotsHandler.join_robots_txt("https://en.wikipedia.org/something/"), "https://en.wikipedia.org/robots.txt")

if __name__ == '__main__':
    unittest.main()
