import pprint
import datetime
from SiteScraper import SiteScraper


website = "http://web.pzjudo.pl/"
# website = "https://www.britishjudo.org.uk/"

# creating instance of sitescraper
ss1 = SiteScraper(website, 10, 'img')
# links = ss1.bfs_scraper_paths_only()
links = ss1.dfs_scraper()

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

fp = open(filename, "w")

for x in links:
    fp.write(x + '\n')

fp.close()
