import urllib.parse

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, urlunsplit, urlsplit, urljoin


# import pprint


class SiteScraper:

    _visited_counter = 0

    def __init__(self, url, max_nodes = None):
        self._base_url = url
        self._base_url_parsed = urlsplit(url)._asdict()
        self._max_nodes_visited = max_nodes

    def simple_bfs_scraper(self):
        visited = []
        # preventing duplicates and loops by using sets instead of arrays
        queue = []
        queue_set = set()
        visited_set = set()

        # extracting domain, url and scheme from the base url
        base_url_parsed = urlparse(self._base_url)
        base_scheme = base_url_parsed.scheme
        base_url_address = base_url_parsed.netloc
        base_path = base_url_parsed.path
        print('URL DATA: ')
        print('\tscheme: ', base_scheme)
        print('\tnetloc: ', base_url_address)
        print('\tpath: ', base_path)
        print()

        current_node = {"url": self._base_url, "level": 0}
        print("Current node: ", current_node["url"])

        try:
            # crawling through the website till queue is not empty
            while len(queue) >= 0:

                # making request
                website_source = requests.get(current_node["url"]).text
                print("Checked link: ", current_node)

                # soup of the website
                soup = BeautifulSoup(website_source, 'html.parser')  # html.parser is a default parser

                # extracting all links <a> tags
                links = soup.find_all('a')

                for link in links:
                    url = link.get('href')
                    # print(url)
                    # register all subpages of the website (omitting externals like twitter)
                    if ((urlparse(url).netloc == base_url_address) or (
                            urlparse(url).netloc == '' and urlparse(url).path != '' and urlparse(
                        url).path != '/')) and not SiteScraper.is_email(url):

                        # check if the URL is already in the visited set
                        if url not in visited_set.union(queue_set):
                            print("added to queue: ", url)
                            queue_set.add(url)
                            queue.append({"url": self.add_url_to_base(url),
                                          "level": current_node["level"] + 1,
                                          "parent": current_node["url"]})

                visited.append(current_node)
                print("node visited: ", current_node["url"])
                visited_set.add(current_node["url"])
                current_node = queue.pop(0)

            return visited
        except Exception as e:
            print(e)
        finally:
            return visited

    def bfs_scraper_paths_only(self):
        """
        Registers only URLs without any additional information like level or children
        :param base_url: root URL
        :return: set of crawled URL of the website
        """
        # preventing duplicates and loops
        queue = set()
        visited = set()

        current_node = self._base_url
        print("Current node: ", current_node)

        try:

            # crawling through the website till queue is not empty
            while len(queue) >= 0:

                # making request
                website_source = requests.get(current_node).text
                print("Checked link: ", current_node)

                # soup of the website
                # soup = BeautifulSoup(website_source, 'html.parser')  # html.parser is a default parser
                soup = BeautifulSoup(website_source, 'lxml-xml')  # faster than html.parser

                # extracting all links <a> tags
                links = soup.find_all('a')

                for link in links:
                    url = link.get('href')

                    url_prepared = self.sanitize_url(url)

                    # register all subpages of the website (omitting externals like twitter)
                    if url_prepared is not None:
                        # check if the URL is already in the visited or queue set
                        if url_prepared not in visited.union(queue):
                            print("added to queue: ", url_prepared)
                            queue.add(self.add_url_to_base(url_prepared))
                            print("Queue counter: ", len(queue))
                            print("Visited counter: ", len(visited))

                print("node visited: ", current_node)
                visited.add(current_node)
                self._visited_counter += 1

                if len(visited) == self._max_nodes_visited:
                    break

                current_node = queue.pop()

            print("Visited counter: ", len(visited))

            return visited
        except Exception as e:
            print(e)
        finally:
            return visited

    def dfs_scraper(self):
        pass

    def scrap_pdf(self):
        pass

    def scrap_images(self):
        pass

    @classmethod
    def is_email(cls, url):
        checker = re.compile("^.+[@].+[.][a-z]{2,3}$")

        if checker.search(url) is not None:
            return True

        return False

    def add_url_to_base(self, url):
        return urljoin(self._base_url, url)

    @classmethod
    def is_file(cls, url):
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

    def sanitize_url(self, url):
        """
        Checking if net location matches the one in base url.
        Checking scheme whether it is http or https
        Removing parameters.

        :param url: url to sanitize
        :param base_netloc: the root URL
        :return: Sanitized URL. If URL cannot be sanitized returns None.
        """
        # extracting domain, url and scheme from the base url
        url_parsed = urlsplit(url)._asdict()

        # allowed schemes (in case of '/home' there is no scheme, and it is valid)
        allowed_schemes = ['http', 'https', '']
        allowed_netloc = [self._base_url_parsed['netloc'], '']

        # check the scheme if there is one, or it is http or https
        if url_parsed['scheme'] not in allowed_schemes:
            # print("Scheme not allowed")
            return None

        # check if netloc is the same in url and base url
        if url_parsed['netloc'] not in allowed_netloc:
            # print("Netloc different from the base one")
            return None

        if SiteScraper.is_email(url):
            # print("It is email.")
            return None

        # remove any parameters or queries
        url_parsed['query'] = ''
        url_parsed['fragment'] = ''
        sanitized_url = urljoin(self._base_url, urlunsplit(url_parsed.values()))
        print(sanitized_url)

        return sanitized_url

