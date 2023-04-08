import re
from urllib.parse import urlparse, urlunsplit, urlsplit, urljoin
import urllib.error


class URLSanitizer:

    docs_extensions = ['.pdf', '.docx', '.doc', '.xls', '.ppt', '.txt', '.zip']
    image_extensions = ['.jpg', '.jpeg', '.gif', '.png', '.svg']

    @classmethod
    def is_doc_by_header(cls, headers):
        """
        Checking if the resource is PDF file
        :param headers: website page headers
        :return: True if pdf file, False otherwise
        """
        content_type = headers.get('content-type')

        # if content_type.endswith("pdf"):
        for ext in cls.docs_extensions:
            if content_type.endswith(ext):
                return True

        return False

    @classmethod
    def is_doc_by_extension(cls, url):
        """
        Checking if the resource is PDF file
        :type url: url to check
        :return: True if pdf file, False otherwise
        """

        for ext in cls.docs_extensions:
            if url.endswith(ext):
                return True

        return False

    @staticmethod
    def is_image_by_header(headers):
        """
        Checking if the resource is image (file format jpg, jpeg, gif, png)

        :param headers: website page headers
        :return: True if an image, False otherwise
        """

        content_type = headers.get('content-type')

        if content_type.startswith("image/"):
            return True

        return False

    @classmethod
    def is_image_by_extension(cls, url):
        """
        Checking if the resource is image (file format jpg, jpeg, gif, png)

        :param url: url to check
        :return: True if an image, False otherwise
        """

        # if content_type.endswith("pdf"):
        for ext in cls.image_extensions:
            if url.endswith(ext):
                return True

        return False

    @staticmethod
    def is_email(url):
        checker = re.compile("^.+[@].+[.][a-z]{2,3}$")

        if checker.search(url) is not None:
            return True

        return False

    @staticmethod
    def add_url_to_base(self, url):
        return urljoin(self._base_url, url)

    @staticmethod
    def is_file(url):
        """
        Checking if resource pointed by URL is a file
        :param url: Resource location
        :return: True if resource is file, False otherwise
        """
        checker = re.compile("^.+[.].+$")

        if checker.search(url) is not None:
            return True

        return False

    @staticmethod
    def check_url(url):
        """
        Extracting scheme, domain, path, query and anchors from the url
        :param url: Url to be checked
        :return: Void
        """
        base_url_parsed = urlparse(url)

        print('URL DATA: ')
        print('\tscheme: ', base_url_parsed.scheme)
        print('\tnetloc: ', base_url_parsed.netloc)
        print('\tpath: ', base_url_parsed.path)
        print('\tquery: ', base_url_parsed.query)
        print('\tfragment (anchor): ', base_url_parsed.fragment)
        print()

        return base_url_parsed._asdict()

    @staticmethod
    def sanitize_url(url, base_url=None):
        """
        Checking if net location matches the one in base url.
        Checking scheme whether it is http or https
        Removing parameters.
        :param url: url to sanitize
        :param base_url: base  of the url
        :return: Sanitized URL. If URL cannot be sanitized returns None.
        """

        # if the URL is root URL
        if base_url is None:
            pass
            # check if the scheme is present
            # check if making request is possible

        # extracting domain, url and scheme from the base url
        url_parsed = urlsplit(url.strip())._asdict()
        base_url_parsed = urlsplit(base_url)._asdict()

        # allowed schemes (in case of '/home' there is no scheme, and it is valid)
        allowed_schemes = ['http', 'https', '']
        allowed_netloc = [base_url_parsed['netloc'], '']

        # check the scheme if there is one, or it is http or https
        if url_parsed['scheme'] not in allowed_schemes:
            # print("Scheme not allowed")
            return None

        # check if netloc is the same in url and base url
        if url_parsed['netloc'] not in allowed_netloc:
            # print("Netloc different from the base one")
            return None

        if URLSanitizer.is_email(url):
            # print("It is email.")
            return None

        # remove any parameters or queries
        url_parsed['query'] = ''
        url_parsed['fragment'] = ''

        # canonicalization of URLs, so that all of them ends with backslash
        # if ((url_parsed['path'] == '') or (url_parsed['path'][-1] != '/')) and not (URLSanitizer.is_file(url)):
        #     url_parsed['path'] += '/'

        sanitized_url = urljoin(base_url, urlunsplit(url_parsed.values()))

        return sanitized_url
