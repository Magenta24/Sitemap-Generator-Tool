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

    def __init__(self, url, max_nodes=None, mode='None', sitemap_type='structured', parser='html', to_search=None,
                 crawl_delay=False):
        """
        :param url: root URL
        :param max_nodes: maximum number of nodes to crawl
        :param mode: might be img , pdf or None (registering images, pdf documents or everything respectively)
        :param parser: type of parser used by crawler
        """
        self._base_url = url
        self._base_url_parsed = urlsplit(url)._asdict()  # url split into scheme, netloc, path and so on
        self._max_nodes_visited = max_nodes
        self._mode = mode
        self._sitemap_type = sitemap_type
        self.pages_visited_no = 0
        self.pages_queued_no = 0
        self.pages_collected_no = 0
        self._to_search = to_search
        self._craw_delay = crawl_delay
        self.search_results = {'locations': [], 'occurrences': 0, 'to_search': to_search}
        self._collected = []  # all collected URLs
        self.images = []  # all collected images
        self.docs = []  # all collected documents
        self._visited = set()  # all visited URLs
        self._queue = []  # queue list
        self._url_tree = None  # tree to keep the structure of the website
        self._search_results = []  # stores the locations of the provided word/phrase

        now = datetime.now()
        self.base_filepath = self._base_url_parsed['netloc'].split(".")[0] + now.strftime("%d%m%Y%H%M%S")
        self._logs = Logging(self.base_filepath)

        # checking if it is possible to make a request to URL provided by user
        try:
            source = requests.get(url, allow_redirects=True)
            print('INIT::STATUS CODE: ', source.status_code)
            # print('INIT::SOURCE: ', source.text)
            print('INIT::HISTORY: ', source.history)
            # print('INIT::HEADERS: ', source.headers)
            print('INIT::URL: ', source.url)
        except Exception as e:
            print("COULDNT PERFORM REQUEST TO URL: ", url)
            print(e)
            exit(-1)

        # robots.txt file parser
        rh = RobotsHandler(url)
        self._robotstxt_parser = rh.parser

        # using session to increase performance
        # self.session = requests.Session()

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
        Registers only URLs without any additional information like level or children

        :return: set of crawled URL of the website
        """

        self._collected.clear()
        queue = []  # URLs to be crawled
        queue_set = set()  # URLs to be crawled set to prevent duplicates
        visited = set()  # URLs visited
        self._url_tree = URLTree()  # tree storing all the URLs and related metadata

        current_node = {'url': self._base_url, 'level': 0}

        # add root to the tree
        self._url_tree.create_node(current_node['url'], current_node['url'], data=current_node)
        print("START NODE: ", current_node)
        print("ROOT: ", self._url_tree.root)

        try:
            # crawling through the website till queue is not empty
            while len(queue) >= 0:

                iteration_st = time.time()

                # marking crawled URL as VISITED
                visited.add(current_node['url'])
                print("NODE VISITED: ", len(visited), ' ', current_node['url'])

                # terminating crawling if max_nodes value is reached
                if len(self._collected) == self._max_nodes_visited:
                    break

                # making request and reading website source and headers
                # website_req_result = requests.get(current_node['url'])
                # setting random value of the crawl delay if set craw_delay set to True
                if self._craw_delay:
                    seconds = randint(1, 3)
                    print('SECONDS: ', seconds)
                    time.sleep(seconds)

                # make request
                req_stime = time.time()
                website_req_result = requests.get(current_node['url'], allow_redirects=True)
                req_etime = time.time()
                # log request time
                print('REQUEST TIME: ', str(round((req_etime-req_stime), 2)))
                self._logs.log_info(('REQUEST TIME: ' + str(round((req_etime - req_stime), 2))))

                website_source = website_req_result.text  # web source code
                website_headers = website_req_result.headers  # headers to check for images or docs

                # check if URL is image or document
                if URLSanitizer.is_image_by_header(website_headers) or \
                        URLSanitizer.is_image_by_extension(current_node['url']):
                    print('IMAGE')
                    self.images.append(current_node['url'])
                    current_node = queue.pop(0)
                    continue
                elif URLSanitizer.is_doc_by_header(website_headers) or \
                        URLSanitizer.is_doc_by_extension(current_node['url']):
                    print('DOCS')
                    self.docs.append(current_node['url'])
                    current_node = queue.pop(0)
                    continue
                else:
                    # adding the URL to collected
                    self._collected.append(current_node)

                # parsing the website
                soup = BeautifulSoup(website_source, self.parser)

                # extracting all links within <a> tags
                links = soup.find_all('a')
                if len(links) == 0:  # in case link is not an HTML page
                    print("No new links extracted")
                    current_node = queue.pop(0)  # getting next to be crawled
                    continue

                # looking for thing to search
                if self._to_search is not None:
                    search_results = soup.body.find_all(string=re.compile('.*{0}.*'.format(self._to_search)),
                                                        recursive=True)
                    # print(current_node['url'], ': ', search_results)
                    if len(search_results) > 0:
                        self.search_results['locations'].append(current_node['url'])
                        self.search_results['occurrences'] += len(search_results)

                for link in links:

                    # stop discovering new links if visited+queue is already equal
                    # to specified max_nodes
                    if (len(visited) + len(queue)) >= self._max_nodes_visited:
                        break

                    if link.get('href') is None:
                        continue

                    # extracting URL and sanitizing it
                    url_prepared = URLSanitizer.sanitize_url(link.get('href'), self._base_url)

                    if url_prepared is not None:  # register all subpages of the website (omitting externals (ex. twitter, instagram etc.))
                        if url_prepared not in visited.union(
                                queue_set):  # check if the URL is already in the visited or queue set
                            if self._robotstxt_parser.can_fetch("*",
                                                                url_prepared):  # check if the page is allowed to be crawled
                                print("added to queue: ", url_prepared)
                                # adding child URL to the queue, queue set and tree
                                child_node = {'url': url_prepared, 'level': (current_node['level'] + 1)}
                                queue.append(child_node)
                                queue_set.add(url_prepared)
                                self._url_tree.create_node(url_prepared, url_prepared, parent=current_node['url'],
                                                           data=child_node)
                                print(len(queue_set), ' ', url_prepared)
                                # print(queue)
                                # print("Queue counter: ", len(queue))
                                # print("Visited counter: ", len(visited))

                # getting next to be crawled
                current_node = queue.pop(0)

                iteration_et = time.time()
                self._logs.log_info(('SINGLE ITERATION TIME: ' + str(round((iteration_et-iteration_st), 2))))


            print("Final Visited counter: ", len(visited))
            print("Final Collected counter: ", len(self._collected))
            print("Final Queued counter: ", len(queue))

        # handling errors
        except urllib.error.HTTPError as e:
            print('HTTP error occurred. Might resource not found or smth else.')
            # self._logs.log_exception(e)
            print(e)
        except urllib.error.URLError as e:
            print('URL error occurred. Might be server couldnt be found or some typo in URL')
            # self._logs.log_exception(e)
            print(e)
        except Exception as e:
            # self._logs.log_exception(e)
            print(e)
        finally:
            self.pages_visited_no = len(visited)
            self.pages_collected_no = len(self._collected)
            self.pages_queued_no = len(queue_set)

            self._create_report()
            self._url_tree.tree_structure_to_file(self.base_filepath)
            self._url_tree.tree_to_graphviz(self.base_filepath)
            self._url_tree.save_xml_sitemap(self.base_filepath, self._sitemap_type)
            self._url_tree.tree_to_svg(self.base_filepath)
            self._url_tree.show()

            return self._collected

    # TODO: refactoring and checking
    def dfs_scraper(self):

        stack = []  # URLs to be crawled
        stack_set = set()  # URLs to be crawled
        visited = set()  # URLs visited
        collected = []  # URLs to be returned to the user
        self._url_tree = URLTree()  # tree storing all the URLs and related metadata
        counter_queue = 0
        current_depth = 0

        # add root to the tree
        root_node = {'url': self._base_url, 'level': 0}
        # add root to the tree
        self._url_tree.create_node(root_node['url'], root_node['url'], data=root_node)
        visited.add(root_node['url'])
        print("START NODE: ", root_node)

        def perform_dfs(node, depth, parent=None):
            nonlocal counter_queue
            nonlocal current_depth

            # stop crawling if maximum depth is reached
            if current_depth > 5:
                return

            # terminating crawling if max_nodes value is reached
            if len(visited) == self._max_nodes_visited:
                return

            current_node = {'url': node['url'], 'level': current_depth}

            # marking crawled URL as VISITED
            print("NODE VISITED: ", len(visited), ' ', node['url'])
            visited.add(node['url'])
            collected.append(node)

            if parent is not None:
                print("NODE ", len(visited), ": ", node['url'], ", PARENT: ", parent['url'])
                self._url_tree.create_node(node['url'], node['url'], data=node, parent=parent['url'])

            try:
                # making request
                website_req_result = requests.get(node['url'])
                website_source = website_req_result.text
                website_headers = website_req_result.headers

                # checking for image and pdf
                if not (URLSanitizer.is_image(website_headers) and URLSanitizer.is_pdf(website_headers)):
                    # soup of the website
                    soup = BeautifulSoup(website_source, self.parser)  # faster than html.parser

                    # extracting all links <a> tags
                    links = soup.find_all('a')

                    current_depth += 1
                    print('current depth: ', current_depth)
                    for link in links:

                        url = link.get('href')
                        url_prepared = URLSanitizer.sanitize_url(url)

                        # register all subpages of the website (omitting externals like twitter)
                        if url_prepared is not None:
                            # check if the URL is already in the visited or queue set
                            if url_prepared not in visited.union(stack_set):
                                child_node = {'url': url_prepared, 'level': (current_node['level'] + 1)}
                                stack.append(child_node)
                                print(len(stack), "NODE ADDED: ", child_node)
                                stack_set.add(url_prepared)

                                print(counter_queue, ' ', url_prepared)
                                counter_queue += 1
                                # recursively crawl the link
                                perform_dfs(child_node, current_depth, node)
                            else:
                                continue
                        else:
                            continue

                else:
                    return

                # deciding whether include given URL in the sitemap
                # if (self.is_image(website_headers) and self._mode == 'img') or \
                #         (self.is_pdf(website_headers) and self._mode == 'pdf') or \
                #         (self._mode == 'None'):
                #     self.collected.append(current_node)

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
            print("Final Visited counter: ", len(visited))
            print("Final collected counter: ", len(collected))

            self._collected = collected
            self._url_tree.tree_structure_to_file()
            self._url_tree.tree_to_graphviz()
            self._url_tree.save_xml_sitemap(self._sitemap_type)
            self._url_tree.tree_to_svg()
            self._url_tree.show()

            return self._collected

    def _get_link(self, url):

        try:
            # making request
            website_req_result = requests.get(url)
            website_source = website_req_result.text
            website_headers = website_req_result.headers

            # checking for image and pdf
            # soup of the website
            soup = BeautifulSoup(website_source, self.parser)

            # extracting all links <a> tags
            links = soup.find_all('a')

            return links

        # handling errors
        except urllib.error.HTTPError as e:
            print('HTTP ERROR. Might resource not found or smth else.')
            print(e)

            return e

        except urllib.error.URLError as e:
            print('URL ERROR. Might be server couldnt be found or some typo in URL')
            print(e)

            return e

        except Exception as e:
            print(e)

    def _create_report(self):
        filepath = os.path.join(django_settings.REPORTS_ROOT, (self.base_filepath + '-report.txt'))
        try:
            with open(filepath, "w") as fp:
                for link in self._collected:
                    fp.write(str(link) + '\n')
        except Exception as e:
            print('CREATE REPORT ERROR!')
            print(e)
