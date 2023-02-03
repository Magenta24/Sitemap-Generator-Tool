import urllib.parse

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import pprint


class SiteScraper:

    @staticmethod
    def simple_bfs_scraper(base_url):
        visited = []
        # preventing duplicates and loops
        queue = []
        queue_set = set()
        visited_set = set()

        # extracting domain, url and scheme from the base url
        base_url_parsed = urlparse(base_url)
        base_scheme = base_url_parsed.scheme
        base_url_address = base_url_parsed.netloc
        base_path = base_url_parsed.path
        print('URL DATA: ')
        print('\tscheme: ', base_scheme)
        print('\tnetloc: ', base_url_address)
        print('\tpath: ', base_path)
        print()

        current_node = {"url": base_url, "level": 0}
        print("Current node: ", current_node["url"])

        try:
            # crawling through the website till queue is not empty
            while (len(queue) >= 0):

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
                            queue.append({"url": SiteScraper.add_url_to_base(base_url, url),
                                          "level": current_node["level"] + 1,
                                          "parent": current_node["url"]})

                visited.append(current_node)
                print("node visited: ", current_node["url"])
                visited_set.add(current_node["url"])
                current_node = queue.pop(0)

            return visited
        except UnboundLocalError:
            print("Przyps")
            return visited
        finally:
            return visited

    @staticmethod
    def bfs_scraper_paths_only(base_url):
        """
        Registers only URLs without any additional information like level or children
        :param base_url: root URL
        :return: set of crawled URL of the website
        """
        # preventing duplicates and loops
        queue = set()
        visited = set()

        # extracting domain, url and scheme from the base url
        base_url_parsed = urlparse(base_url)
        base_scheme = base_url_parsed.scheme
        base_url_address = base_url_parsed.netloc
        base_path = base_url_parsed.path
        print('URL DATA: ')
        print('\tscheme: ', base_scheme)
        print('\tnetloc: ', base_url_address)
        print('\tpath: ', base_path)
        print()

        current_node = base_url
        print("Current node: ", current_node)

        try:
            # crawling through the website till queue is not empty
            while (len(queue) >= 0):

                # making request
                website_source = requests.get(current_node).text
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

                        # check if the URL is already in the visited or queue set
                        if url not in visited.union(queue):
                            print("added to queue: ", url)
                            queue.add(SiteScraper.add_url_to_base(base_url, url))
                            print("Queue counter: ", len(queue))


                print("node visited: ", current_node)
                visited.add(current_node)
                current_node = queue.pop()

            print("Visited counter: ", len(visited))
            return visited
        except UnboundLocalError:
            print("Przyps")
            return visited
        except Exception as e:
            print(e)
            return visited
        finally:
            return visited

    @staticmethod
    def dfs_scraper(base_url):
        pass

    @staticmethod
    def scrap_pdf(base_url):
        pass

    @staticmethod
    def scrap_images():
        pass

    @staticmethod
    def is_email(url):
        checker = re.compile("^.+[@].+[.][a-z]{2,3}$")

        if checker.search(url) is not None:
            return True

        return False

    @staticmethod
    def add_url_to_base(base, url):
        return urllib.parse.urljoin(base, url)

    """
    checking if the URI is html file or any other file (e.g. PDF, JPEG, Excel sheet)
    """
    @staticmethod
    def is_file(url):
        checker = re.compile("^.+[.].+$")

        if checker.search(url) is not None:
            return True

        return False

