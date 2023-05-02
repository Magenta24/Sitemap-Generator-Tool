import re
from urllib.parse import urlparse, urlunsplit, urlsplit, urljoin


class URLSanitizer:
    """
    This class is responsible for canonicalization of URLs.
    It implements following methods:
        - is_doc_by_header - checking passed headers for documents
        - is_doc_by_extension - checking extension of passed URL for documents
        - is_image_by_header - checking passed headers for images
        - is_image_by_extension - checking extension of passed URL for images
        - is_email - checks if the passed link is an email
        - is_file - checks if the passed link is a file
        - check_url - printing and returning parsed URL
        - sanitize_url - canonicalizating passed URL

    """

    docs_extensions = ['pdf', 'docx', 'doc', 'xls', 'ppt', 'txt', 'zip', 'pptx', 'csv', 'msword', 'vnd.ms-excel']
    image_extensions = ['.jpg', '.jpeg', '.gif', '.png', '.svg']

    @classmethod
    def is_doc_by_header(cls, headers):
        """
        Checking if the resource is PDF file
        :param headers: website page headers
        :return: True if pdf file, False otherwise
        """

        content_type = headers.get('content-type')

        if content_type is None:
            return False

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

        if content_type is None:
            return False

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
        """
        Check whether the passed URL is an email.

        :param url: URL to check
        :return: True if email, False otherwise
        """
        checker = re.compile("^.+[@].+[.][a-z]{2,3}$")

        if checker.search(url) is not None:
            return True

        return False

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
        :return: parsed URL as dictionary
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
        Canonicalization of the passed URL.

        :param url: url to sanitize
        :param base_url: base  of the url
        :return: Sanitized URL. If URL cannot be sanitized returns None.
        """

        # extracting domain, url and scheme from the base url
        url_parsed = urlsplit(url.strip())._asdict()
        base_url_parsed = urlsplit(base_url)._asdict()

        # allowed schemes (in case of '/home' there is no scheme, and it is valid)
        allowed_schemes = ['http', 'https', '']
        allowed_netloc = [base_url_parsed['netloc'], '']

        # check the scheme
        if url_parsed['scheme'] not in allowed_schemes:
            return None

        # check if the url is internal or external URL
        if url_parsed['netloc'] not in allowed_netloc:
            return None

        # check for emails
        if URLSanitizer.is_email(url):
            return None

        # removing the trailing backslash if present
        if (len(url_parsed['path']) > 1) and (url_parsed['path'][-1] == '/'):
            url_parsed['path'] = url_parsed['path'][:-1]

        # remove parts that come after '#'
        url_parsed['fragment'] = ''

        if url == '/':
            return base_url

        sanitized_url = urljoin(base_url, urlunsplit(url_parsed.values()))
        return sanitized_url
