import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, urlunsplit, urlsplit, urljoin
import urllib.error
from .URLTree import URLTree


class SiteScraper:
    _collected = []
    _visited = set()
    _queue = []
    _url_tree = None

    def __init__(self, url, max_nodes=None, mode='None', sitemap_type='structured', parser='html'):
        """
        :param url: root URL
        :param max_nodes: maximum number of nodes to crawl
        :param mode: might be img , pdf or None (registering images, pdf documents or everything respectively)
        :param parser: type of parser used by crawler
        """
        self._base_url = url
        self._base_url_parsed = urlsplit(url)._asdict()
        self._max_nodes_visited = max_nodes
        self._mode = mode
        self._sitemap_type = sitemap_type

        if sitemap_type in ['flat', 'structured']:
            self._sitemap_type = sitemap_type
        else:
            print('Incorrect sitemap type! You can choose flat or structured type')
            exit(-1)

        if parser == 'html':
            self.parser = 'html.parser'
        elif parser == 'lxml':
            # self.parser = 'lxml-xml'
            self.parser = 'xml'
        else:
            print("Provide correct parser like xml or html")
            exit(-1)

        print('INIT SUCCESSFUL')

    def bfs_scraper(self):
        """
        Registers only URLs without any additional information like level or children

        :return: set of crawled URL of the website
        """

        queue = []  # URLs to be crawled
        queue_set = set()  # URLs to be crawled
        visited = set()  # URLs visited
        collected = []  # URLs to be returned to the user
        self._url_tree = URLTree()  # tree storing all the URLs and related metadata
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

                        if (len(visited) + len(queue)) >= self._max_nodes_visited:
                            break

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
                if (self.is_image(website_headers) and self._mode == 'img') or \
                        (self.is_pdf(website_headers) and self._mode == 'pdf') or \
                        (self._mode == 'None'):
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
            self._url_tree.tree_structure_to_file()
            self._url_tree.tree_to_graphviz()
            self._url_tree.save_xml_sitemap(self._sitemap_type)
            self._url_tree.tree_to_svg()
            self._url_tree.show()

            print('ALL NODES FROM TREE')
            for node in self._url_tree.all_nodes():
                print(node.data['level'])
            return collected

    def dfs_scraper(self):

        stack = []  # URLs to be crawled
        stack_set = set()  # URLs to be crawled
        visited = set()  # URLs visited
        collected = []  # URLs to be returned to the user
        self._url_tree = URLTree()  # tree storing all the URLs and related metadata
        counter_queue = 0
        current_depth = 0

        # add root to the tree
        root_node = {'url': self.sanitize_url(self._base_url), 'level': 0}
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
                print("NODE ", len(visited),": ", node['url'], ", PARENT: ", parent['url'])
                self._url_tree.create_node(node['url'], node['url'], data=node, parent=parent['url'])

            try:
                # making request
                website_req_result = requests.get(node['url'])
                website_source = website_req_result.text
                website_headers = website_req_result.headers

                # checking for image and pdf
                if not (self.is_image(website_headers) and self.is_pdf(website_headers)):
                    # soup of the website
                    soup = BeautifulSoup(website_source, self.parser)  # faster than html.parser

                    # extracting all links <a> tags
                    links = soup.find_all('a')

                    current_depth += 1
                    print('current depth: ', current_depth)
                    for link in links:

                        url = link.get('href')
                        url_prepared = self.sanitize_url(url)

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
