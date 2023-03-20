import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, urlunsplit, urlsplit, urljoin
import xml.etree.ElementTree as ET
from xml.dom import minidom
import urllib.error

from treelib import Node, Tree
import graphviz
import os

from django.conf import settings as django_settings


class SiteScraper:
    _collected = []
    _visited = set()
    _queue = []
    _url_tree = None

    def __init__(self, url, max_nodes=None, mode=None, parser='html'):
        """
        :param url: root URL
        :param max_nodes: maximum number of nodes to crawl
        :param mode: might be img , pdf or None (registering images, pdf documents or everything respectively)
        :param parser: type of parser used by crawler
        """
        self._base_url = url
        self._base_url_parsed = urlsplit(url)._asdict()
        self._max_nodes_visited = max_nodes
        self.mode = mode

        if parser == 'html':
            self.parser = 'html.parser'
        elif parser == 'lxml':
            self.parser = 'lxml-xml'
        else:
            print("Provide correct parser like xml or html")
            exit(-1)

        print('INIT SUCCCESSFUL')

    def bfs_scraper_paths_only(self):
        """
        Registers only URLs without any additional information like level or children

        :return: set of crawled URL of the website
        """

        queue = []  # URLs to be crawled
        queue_set = set()  # URLs to be crawled
        visited = set()  # URLs visited
        collected = []  # URLs to be returned to the user
        self._url_tree = Tree()  # tree storing all the URLs and related metadata
        counter_queue = 0

        current_node = {'url': self.sanitize_url(self._base_url), 'level': 0}
        # add root to the tree
        self._url_tree.create_node(current_node['url'], current_node['url'], data=current_node)
        print("START NODE: ", current_node)

        try:

            # crawling through the website till queue is not empty
            while len(queue) >= 0:

                # marking crawled URL as VISITED
                visited.add(current_node['url'])
                print("NODE VISITED: ", len(visited), ' ', current_node['url'])

                # making request
                website_req_result = requests.get(current_node['url'])
                website_source = website_req_result.text
                website_headers = website_req_result.headers

                # checking for image and pdf
                if not (self.is_image(website_headers) and self.is_pdf(website_headers)):

                    # soup of the website
                    soup = BeautifulSoup(website_source, self.parser)

                    # extracting all links <a> tags
                    links = soup.find_all('a')

                    for link in links:

                        # extracting URL and sanitizing it
                        url_prepared = self.sanitize_url(link.get('href'))

                        if url_prepared is not None:  # register all subpages of the website (omitting externals (ex. twitter, instagram etc.))
                            if url_prepared not in visited.union(
                                    queue_set):  # check if the URL is already in the visited or queue set
                                # print("added to queue: ", url_prepared)
                                # adding URL to the queue
                                child_node = {'url': url_prepared, 'level': (current_node['level'] + 1)}
                                queue.append(child_node)
                                queue_set.add(url_prepared)
                                self._url_tree.create_node(url_prepared, url_prepared, parent=current_node['url'],
                                                           data=child_node)
                                print(counter_queue, ' ', url_prepared)
                                counter_queue += 1
                                # print(queue)
                                # print("Queue counter: ", len(queue))
                                # print("Visited counter: ", len(visited))

                # deciding whether include given URL in the sitemap
                if (self.is_image(website_headers) and self.mode == 'img') or \
                        (self.is_pdf(website_headers) and self.mode == 'pdf') or \
                        (self.mode is None):
                    collected.append(current_node)

                # terminating crawling if max_nodes value is reached
                if len(visited) == self._max_nodes_visited:
                    break

                # getting next to be crawled
                current_node = queue.pop(0)

            print("Final Visited counter: ", len(visited))
            print("Final Collected counter: ", len(collected))
            print("Final Queued counter: ", len(queue))

        # handling errors
        except urllib.error.HTTPError as e:
            print('HTTP error occurred. Might resource not found or smth else.')
            print(e)
        except urllib.error.URLError as e:
            print('URL error occurred. Might be server couldnt be found or some typo in URL')
            print(e)
        except Exception as e:
            print(e)
        finally:
            self._collected = collected
            self.save_url_tree_to_file()
            self.tree_to_graphviz()
            # self._url_tree.show()
            return collected

    def dfs_scraper(self):
        visited = set()
        collected = set()
        stack = []

        current_node = self._base_url
        print("Start node: ", current_node)

        try:

            # crawling through the website till queue is not empty
            while len(stack) >= 0:

                # making request
                website_req_result = requests.get(current_node)
                website_source = website_req_result.text
                website_headers = website_req_result.headers
                # website_req_result.raise_for_status()  # raising exception for error code 4xx or 5xx

                # checking for image and pdf
                if not (self.is_image(website_headers) and self.is_pdf(website_headers)):
                    # soup of the website
                    soup = BeautifulSoup(website_source, self.parser)  # faster than html.parser

                    # extracting all links <a> tags
                    links = soup.find_all('a')

                    for link in links:
                        url = link.get('href')

                        url_prepared = self.sanitize_url(url)

                        # register all subpages of the website (omitting externals like twitter)
                        if url_prepared is not None:
                            # check if the URL is already in the visited or queue set
                            if url_prepared not in visited.union(set(stack)):
                                print("added to queue: ", url_prepared)
                                stack.append(url_prepared)
                                print("Queue counter: ", len(stack))
                                print("Visited counter: ", len(visited))
                                print("Collected counter: ", len(collected))

                print("NODE VISITED: ", len(visited) + 1, ' ', current_node)
                visited.add(current_node)

                if (self.is_image(website_headers) and self.mode == 'img') or \
                        (self.is_pdf(website_headers) and self.mode == 'pdf') or \
                        (self.mode is None):
                    collected.add(current_node)

                if len(visited) == self._max_nodes_visited:
                    break

                # getting last most recent element
                current_node = stack.pop()

            print("Final Visited counter: ", len(visited))

            # return visited
        except Exception as e:
            print(e)
        finally:
            print(collected)
            return list(collected)

    def save_url_tree_to_file(self):
        filename = 'url_tree.txt'
        filepath = os.path.join(django_settings.STATIC_ROOT, 'tree_structure', filename).replace("\\", "/")

        # if tree file already exist - delete
        if os.path.exists(filepath):
            os.remove(filepath)

        self._url_tree.save2file(filepath)

    def tree_to_diagram(self):
        return self._url_tree.show(stdout=False)

    def tree_to_json(self):
        return self._url_tree.to_json()

    def tree_to_graphviz(self):
        filepath = os.path.join(django_settings.GRAPHVIZ_ROOT, 'tree-graph.gv').replace("\\", "/")

        # if gv file already exist - delete
        if os.path.exists(filepath):
            os.remove(filepath)

        # self._url_tree.to_graphviz('tree-graph.gv', shape='plaintext')
        self._url_tree.to_graphviz(filepath, shape='egg')

    def tree_to_svg(self):
        filepath = os.path.join(django_settings.GRAPHVIZ_ROOT, 'tree-graph.gv').replace("\\", "/")
        img_path = os.path.join(django_settings.MEDIA_ROOT, 'diagram').replace("\\", "/")

        # if image already exist - delete
        if os.path.exists(img_path):
            os.remove(img_path)
            os.remove(img_path + '.svg')

        dot = graphviz.Source.from_file(filepath)
        dot.render('diagram', format='svg', directory=django_settings.MEDIA_ROOT)

    def save_xml_sitemap(self):
        """
        Saving collected hyperlinks to XML sitemap.

        :param collected: hyperlinks
        :param path: location of XML sitemap
        :return: None
        """

        ET.register_namespace('', 'http://www.sitemaps.org/schemas/sitemap/0.9')
        root = ET.Element('{http://www.sitemaps.org/schemas/sitemap/0.9}urlset')

        for link in self._collected:
            url = ET.SubElement(root, 'url')

            loc = ET.SubElement(url, 'loc')
            loc.text = link['url']

            lastmod = ET.SubElement(url, 'lastmod')

            depth = ET.SubElement(url, 'depth')
            # depth.text = link['level']

        tree = ET.ElementTree(root)

        try:
            xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
            path = os.path.join(django_settings.XML_ROOT, 'sitemap.xml')

            with open(path, "w") as f:
                f.write(xmlstr)
        except Exception as e:
            print('Przyps')
            print(e)

    def is_pdf(self, headers):
        """
        Checking if the resource is PDF file
        :param headers: website page headers
        :return: True if pdf file, False otherwise
        """
        content_type = headers.get('content-type')

        if content_type.endswith("pdf"):
            return True

        return False

    def is_image(self, headers):
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

        return base_url_parsed._asdict()

    def sanitize_url(self, url):
        """
        Checking if net location matches the one in base url.
        Checking scheme whether it is http or https
        Removing parameters.
        :param url: url to sanitize
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

        # canonicalization of URLs, so that all of them ends with backslash
        if ((url_parsed['path'] == '') or (url_parsed['path'][-1] != '/')) and not (self.is_file(url)):
            url_parsed['path'] += '/'

        sanitized_url = urljoin(self._base_url, urlunsplit(url_parsed.values()))

        return sanitized_url
