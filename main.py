import pprint
import datetime
from SiteScraper import SiteScraper

"""
TO-DO:
1. Extracting all links of the website
2. Storing  the links somehow
    maybe hash table ->
    hashing the links which will be used as keys of the dictionary
    the values of the dictionary will be another dictionary that stores
    (link, level, parent, children)
3. Going down the website 3 levels and registering all the links without duplicates
"""

website = "http://web.pzjudo.pl/"
# website = "https://www.britishjudo.org.uk/"

# creating instance of sitescraper
ss1 = SiteScraper(website, 100)

# links = SiteScraper.simple_bfs_scraper(base_url=website)
links = ss1.bfs_scraper_paths_only()

# print(SiteScraper.is_email("mailto:pzjudo@pzjudo.pl"))
# print(SiteScraper.is_email("pzjudo@pzjudo.pl"))
# print(SiteScraper.is_email("pzjudo.pl"))

# pprint.pprint(links)


current_time = datetime.datetime.now()

filename = "records/website_links-"
filename += str(current_time.date())
filename += "-"
filename += str(current_time.time().hour)
filename += "-"
filename += str(current_time.time().minute)
filename += ".txt"
print(filename)

ss1 = SiteScraper('pzjudo.pl')
ss2 = SiteScraper('britishjudo.org.uk')

# ss1.sanitize_url('webcal://www.britishjudo.org.uk/?tribe-bar-date=2023-02-08&ical=1&eventDisplay=list')
# ss1.sanitize_url('https://www.britishjudo.org.uk/?tribe-bar-date=2023-02-08&ical=1&eventDisplay=list')

fp = open(filename, "w")

for x in links:
    fp.write(x + '\n')

fp.close()
