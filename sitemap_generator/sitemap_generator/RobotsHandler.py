import robots

class RobotsHandler:
    def __init__(self, url):
        self.url = url
        self.parser = robots.RobotsParser.from_uri(url)

