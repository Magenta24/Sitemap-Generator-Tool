import robots
from urllib.parse import urljoin

class RobotsHandler:
    def __init__(self, url):
        self.url = url
        self.parser = robots.RobotsParser.from_uri(RobotsHandler.join_robots_txt(url))

    @staticmethod
    def join_robots_txt(url):
        return urljoin(url, '/robots.txt')