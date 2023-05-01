import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunsplit, urlsplit, urljoin
import urllib.error
import re
import time
from datetime import datetime
from random import randint
import os

from .RobotsHandler import RobotsHandler
from .Logging import Logging
from .URLTree import URLTree
from .URLSanitizer import URLSanitizer

from django.conf import settings as django_settings


class SiteScraper:
    """
    This class implements the crawler for Sitemap Generator Tool.
    It consists of following methods:
        - bfs_scraper - implementation of BFS web traversal
        - dfs_scraper - implementation of DFS web traversal
        - make_request - helper function to perform requests
        - mini_search_engine - finding the word/phrase specified by user
        - create_report - saves all the visited links to a txt file
    """

    def __init__(self, url, max_nodes=None, max_depth=None, sitemap_type='structured', parser='html', to_search=None,
                 crawl_delay=False):
        """

        :param url: root URL
        :param max_nodes: maximum number of nodes to crawl
        :param max_depth: maximum site depth the crawler will get to
        :param sitemap_type: flat (list of links) or structured (showing hierarchy)
        :param parser: type of parser used by crawler
        :param to_search: word/phrase specified by user to search for
        :param crawl_delay: whether to include crawl delay ('politeness' policy)
        """
        self._base_url = url
        self._base_url_parsed = urlsplit(url)._asdict()  # url split into scheme, netloc, path and so on
        self._max_nodes_visited = max_nodes
        self._max_depth = max_depth
        self._sitemap_type = sitemap_type
        self._pages_scanned_no = 0
        self._no_pages_excluded = 0
        self._to_search = to_search
        self._craw_delay = crawl_delay
        self._search_results = {'locations': [], 'occurrences': 0, 'to_search': to_search}
        self._collected = []  # all collected URLs
        self._images = []  # all collected images
        self._docs = []  # all collected documents
        self._visited = set()  # all visited URLs
        self._url_tree = None  # tree to keep the structure of the website

        # creating base filepath, unique for every crawling
        self._base_filepath = self._base_url_parsed['netloc'].split(".")[0] + datetime.now().strftime("%d%m%Y%H%M%S")
        self._logs = Logging(self._base_filepath)

        # creating new session
        self._crawling_session = requests.Session()
        self._crawling_session.max_redirects = 3

        # checking if it is possible to make a request to URL provided by user
        try:
            source = self._crawling_session.get(url, allow_redirects=True, timeout=5)
            print('INIT::STATUS CODE: ', source.status_code)
            # print('INIT::SOURCE: ', source.text)
            print('INIT::HISTORY: ', source.history)
            # print('INIT::HEADERS: ', source.headers)
            print('INIT::URL: ', source.url)

            # check for returned code
            if source.status_code >= 400:
                self._logs.log_exception(("ERROR CODE: " + source.status_code + "."))
                raise ValueError("COULDNT PERFORM REQUEST TO URL: ", url)

        except requests.exceptions.Timeout:
            self._logs.log_exception("REQUEST TIMETOUT!")
            raise ValueError("COULDNT PERFORM REQUEST TO URL: ", url)

        except Exception as e:
            print("COULDNT PERFORM REQUEST TO URL: ", url)
            self._logs.log_exception(e)
            raise ValueError("COULDNT PERFORM REQUEST TO URL: ", url)
            # exit(-1)

        # robots.txt file parser
        rh = RobotsHandler(url)
        self._robotstxt_parser = rh.parser

        # checking sitemap type
        if sitemap_type in ['flat', 'structured']:
            self._sitemap_type = sitemap_type
        else:
            print('Incorrect sitemap type! You can choose flat or structured type')
            exit(-1)

        # checking parser
        if parser == 'html':
            self.parser = 'html.parser'
        elif parser == 'lxml':
            # self.parser = 'lxml-xml'
            self.parser = 'lxml'
        else:
            print("Provide correct parser like xml or html")
            exit(-1)

        # checking thing to search
        if to_search == "":
            self._to_search = None

        print('INIT SUCCESSFUL')

    def bfs_scraper(self):
        """
        Traversing the website with BFS algorithm.
        Includes checks like:
            1. The code returned by the request
            2. Header to determine if the resource is text, image or document
            3. Whether the content contains the word/phrase specified by user to be searched for
            4. Whether the link was already visited
            5. Whether the link can be visited by the crawler (robots.txt)

        :return: set of crawled URL of the website
        """

        self._collected.clear()
        queue = []  # URLs (with attributes) to be crawled
        queue_set = set()  # URLs to be crawled set to prevent duplicates
        self._url_tree = URLTree()  # tree storing all the URLs and related metadata
        excluded_no = 0

        current_node = {'url': self._base_url, 'level': 0}

        # add root to the tree
        self._url_tree.create_node(current_node['url'], current_node['url'], data=current_node)
        print("START NODE: ", current_node)
        print("ROOT: ", self._url_tree.root)

        try:
            # crawling through the website till queue is not empty
            while len(queue) >= 0:

                # register iteration time
                iteration_st = time.time()

                # marking crawled URL as VISITED
                self._visited.add(current_node['url'])
                print("NODE VISITED: ", len(self._visited), ' ', current_node['url'])

                # terminating crawling if max_nodes value is reached
                if len(self._collected) == self._max_nodes_visited:
                    break

                # making request
                website_source, website_headers = self.make_request(current_node['url'])
                if website_source is None:
                    current_node = queue.pop(0)
                    continue

                # check if URL is image
                if URLSanitizer.is_image_by_header(website_headers) or \
                        URLSanitizer.is_image_by_extension(current_node['url']):
                    self._images.append(current_node['url'])
                    current_node = queue.pop(0)
                    continue

                # check if URL is document
                elif URLSanitizer.is_doc_by_header(website_headers) or \
                        URLSanitizer.is_doc_by_extension(current_node['url']):
                    self._docs.append(current_node['url'])
                    current_node = queue.pop(0)
                    continue
                else:
                    # adding the URL to collected
                    self._collected.append(current_node)

                # parsing the website
                soup = BeautifulSoup(website_source, self.parser)

                # searching for the word/phrase specified by user
                self.mini_search_engine(soup, current_node['url'])

                # if the depth level of current is node is max depth
                if self._max_depth is not None:
                    if current_node['level'] == self._max_depth:
                        self._logs.log_info(('MAX LEVEL: ' + str(self._max_depth) + ' REACHED.'))
                        current_node = queue.pop(0)  # getting next to be crawled
                        continue

                # stop discovering new links if visited+queue is already equal to specified max_nodes
                elif self._max_nodes_visited is not None:
                    if (len(self._visited) + len(queue)) >= self._max_nodes_visited * 1.1:
                        current_node = queue.pop(0)  # getting next to be crawled
                        continue

                # extracting all links within <a> tags
                links = soup.find_all('a')

                # if no links extracted
                if len(links) == 0:
                    print("No new links extracted")
                    current_node = queue.pop(0)  # getting next to be crawled
                    continue

                for link in links:
                    # stop discovering new links if max depth is reached
                    if self._max_depth is not None:
                        if current_node['level'] == self._max_depth:
                            self._logs.log_info(('MAX LEVEL: ' + str(self._max_depth) + ' REACHED.'))
                            break

                    # stop discovering new links if visited+queue is already equal to specified max_nodes
                    if self._max_nodes_visited is not None:
                        if (len(self._visited) + len(queue)) >= self._max_nodes_visited * 1.1:
                            self._logs.log_info(('MAX NUMBER OF NODES: ' + str(self._max_depth) + ' REACHED.'))
                            break

                    self._pages_scanned_no += 1

                    if link.get('href') is None:
                        continue

                    # extracting URL and sanitizing it
                    url_prepared = URLSanitizer.sanitize_url(link.get('href'), self._base_url)

                    # checking the URLs for already being visited and robots.txt
                    if url_prepared is not None:    # if sanitized correctly
                        if url_prepared not in self._visited.union(queue_set):  # duplicates
                            if self._robotstxt_parser.can_fetch("*", url_prepared):     # robots.txt

                                # adding child URL to the queue, queue set and tree
                                child_node = {'url': url_prepared, 'level': (current_node['level'] + 1)}
                                queue.append(child_node)
                                queue_set.add(url_prepared)
                                self._url_tree.create_node(url_prepared,
                                                           url_prepared,
                                                           parent=current_node['url'],
                                                           data=child_node)
                                print("ADDED LINK: ", len(queue_set), ' ', url_prepared)
                                self._logs.log_info(("URL NO." + str(len(queue_set)) + "ADDED: " + url_prepared))
                            else:
                                self._no_pages_excluded += 1
                                self._logs.log_info(("ROBOT EXCLUDED: " + url_prepared))
                                #print("ROBOT EXCLUDED: ", url_prepared)

                # getting next URL from the queue
                current_node = queue.pop(0)

                iteration_et = time.time()
                self._logs.log_info(('SINGLE ITERATION TIME: ' + str(round((iteration_et - iteration_st), 2))))

        # handling errors
        except urllib.error.HTTPError as e:
            print('HTTP error occurred. Might resource not found or smth else.')
            self._logs.log_exception(e)
            print(e)
        except urllib.error.URLError as e:
            print('URL error occurred. Might be server couldnt be found or some typo in URL')
            self._logs.log_exception(e)
            print(e)
        except Exception as e:
            print(e)
            self._logs.log_exception(e)
        finally:
            self._logs.log_info(("VISITED LINKS: " + str(len(self._visited))))
            self._logs.log_info(("COLLECTED LINKS: " + str(len(self._collected))))
            self._logs.log_info(("QUEUED LINKS: " + str(len(queue_set))))

            self._create_report()
            self._url_tree.tree_structure_to_file(self._base_filepath)
            self._url_tree.tree_to_graphviz(self._base_filepath)
            self._url_tree.save_xml_sitemap(self._base_filepath, self._sitemap_type)
            self._url_tree.tree_to_svg(self._base_filepath)
            self._logs.log_info(("ROBOT.TXT EXLUDED LINKS NO: " + str(excluded_no)))

            return self._collected

    # TODO: refactoring and checking
    def dfs_scraper(self):
        """
        Traversing the website in DFS manner. Alternative for BFS.

        :return: None
        """
        stack = []  # URLs to be crawled
        stack_set = set()  # URLs to be crawled
        self._url_tree = URLTree()  # tree storing all the URLs and related metadata
        counter_queue = 0
        current_depth = 0

        # add root to the tree
        root_node = {'url': self._base_url, 'level': 0}

        # add root to the tree
        self._url_tree.create_node(root_node['url'], root_node['url'], data=root_node)
        self._visited.add(root_node['url'])
        print("START NODE: ", root_node)

        def perform_dfs(node, parent=None):
            """
            Helper function that invoked recursively to perform DFS web traversal.

            :param node: The node to be visited
            :param parent: Parent of the node to be visited
            :return: None
            """

            nonlocal counter_queue
            nonlocal current_depth

            # stop crawling if maximum depth is reached
            if current_depth > self._max_depth:
                return

            # terminating crawling if max_nodes value is reached
            if len(self._visited) == self._max_nodes_visited:
                return

            current_node = {'url': node['url'], 'level': current_depth}

            # marking crawled URL as VISITED
            print("NODE VISITED: ", len(self._visited), ' ', node['url'])
            self._visited.add(node['url'])
            self._collected.append(node)

            if parent is not None:
                self._url_tree.create_node(node['url'], node['url'], data=node, parent=parent['url'])

            try:
                # making request
                website_req_result = requests.get(node['url'])
                website_source = website_req_result.text
                website_headers = website_req_result.headers

                # check if URL is image or document
                if URLSanitizer.is_image_by_header(website_headers) or \
                        URLSanitizer.is_image_by_extension(current_node['url']):
                    self._images.append(current_node['url'])
                    return

                elif URLSanitizer.is_doc_by_header(website_headers) or \
                        URLSanitizer.is_doc_by_extension(current_node['url']):
                    self._docs.append(current_node['url'])
                    return

                else:
                    # adding the URL to collected
                    print("CURRENT NODE:", current_node['url'])
                    self._collected.append(current_node)

                    # soup of the website
                    soup = BeautifulSoup(website_source, self.parser)

                    # search for a specified word/phrase
                    self.mini_search_engine(soup, current_node['url'])

                    # extracting all links <a> tags
                    links = soup.find_all('a')

                    current_depth += 1
                    print('current depth: ', current_depth)
                    for link in links:

                        self._pages_scanned_no += 1

                        url = link.get('href')
                        if url is not None:
                            url_prepared = URLSanitizer.sanitize_url(url, self._base_url)
                        else:
                            continue

                        # checking the URLs for already being visited and robots.txt
                        if url_prepared is not None:    # if sanitized correctly
                            if url_prepared not in self._visited:   # if already visited
                                if self._robotstxt_parser.can_fetch("*", url_prepared):     # robots.txt
                                    child_node = {'url': url_prepared, 'level': (current_node['level'] + 1)}

                                    try:
                                        perform_dfs(child_node, current_depth, node)
                                    except Exception as e:
                                        continue
                                else:
                                    self._no_pages_excluded += 1
                                    self._logs.log_info(("ROBOT EXCLUDED: " + url_prepared))
                            else:   # URL already visited
                                continue
                        else:   # URL could not be sanitized
                            continue

                current_depth -= 1

            # handling errors
            except urllib.error.HTTPError as e:
                print('HTTP error occurred. Might resource not found or smth else.')
                print(e)
                return e

            except urllib.error.URLError as e:
                print('URL error occurred. Might be server couldnt be found or some typo in URL')
                print(e)
                return e

            except Exception as e:
                print(e)
                return e

        try:
            perform_dfs(root_node, 0)
        except Exception as e:
            print(e)
            return e
        finally:
            self._logs.log_info(("VISITED LINKS: " + str(len(self._visited))))
            self._logs.log_info(("COLLECTED LINKS: " + str(len(self._collected))))
            # self._logs.log_info(("QUEUED LINKS: " + str(len(queue_set))))

            self._create_report()
            self._url_tree.tree_structure_to_file(self._base_filepath)
            self._url_tree.tree_to_graphviz(self._base_filepath)
            self._url_tree.save_xml_sitemap(self._base_filepath, self._sitemap_type)
            self._url_tree.tree_to_svg(self._base_filepath)
            # self._logs.log_info(("ROBOT.TXT EXLUDED LINKS NO: " + str(excluded_no)))

            return self._collected

    @property
    def base_url(self):
        return self._base_url

    @property
    def collected_images(self):
        return self._images

    @property
    def base_filepath(self):
        return self._base_filepath

    @property
    def collected_docs(self):
        return self._docs

    @property
    def search_results(self):
        return self._search_results

    @property
    def no_pages_excluded(self):
        return self._no_pages_excluded

    @property
    def no_pages_scanned(self):
        return self._pages_scanned_no

    def make_request(self, url):
        """
        Performing request to the specified URL.
        It also applies crawl delay if crawl_delay is set to True.

        :param url: the URL to be make request to
        :return: If the request was successful, page source code and headers are returned.
        Otherwise, None is returned.
        """

        # setting random value of the crawl delay if set craw_delay set to True
        if self._craw_delay:
            seconds = randint(1, 3)
            time.sleep(seconds)

        # make request
        req_stime = time.time()  # register time of the request
        try:
            website_req_result = self._crawling_session.get(url,
                                                            allow_redirects=True,
                                                            timeout=5)
            # check returned status code
            try:
                if (int(website_req_result.status_code) >= 200) and (int(website_req_result.status_code) < 400):
                    return website_req_result.text, website_req_result.headers
                else:
                    return None, None
            except Exception as e:
                self._logs.log_exception(e)
                print(e)
                return None, None

        except requests.exceptions.Timeout:
            self._logs.log_exception(("TIMEOUT: " + url))
            return None, None
        except requests.exceptions.TooManyRedirects:
            self._logs.log_exception(("TOO MANY REDIRECTS: " + url))
            return None, None
        except Exception as e:
            self._logs.log_exception(e)
            return None, None

        req_etime = time.time()  # register time of the request

        # log request time
        self._logs.log_info(('REQUEST TIME: ' + str(round((req_etime - req_stime), 2))))

    def mini_search_engine(self, soup, url):
        """
        Looking for a word/phrase specified by user.
        If the word/phrase is found, it is added to dictionary 'search_results'
        that contains locations and number of occurrences.

        :param soup: parsed HTML file content
        :param url: URL under which the HTML content is accessible
        :return:
        """

        # searching for the word/phrase specified by user
        if self._to_search is not None:
            search_results = soup.body.find_all(string=re.compile('.*{0}.*'.format(self._to_search)),
                                                recursive=True)
            if len(search_results) > 0:
                self.search_results['locations'].append(url)
                self.search_results['occurrences'] += len(search_results)


    def _create_report(self):
        """
        Create report with all collected links (backup in case of bot crash),
        Report is saved in plain txt file.

        :return: None
        """
        filepath = os.path.join(django_settings.REPORTS_ROOT, (self._base_filepath + '-report.txt'))
        try:
            with open(filepath, "w", encoding="utf-8") as fp:
                for link in self._collected:
                    fp.write(str(link['url']) + ',' + str(link['level']) + '\n')
        except Exception as e:
            print('CREATE REPORT ERROR!')
            self._logs.log_exception(e)
            print(e)
