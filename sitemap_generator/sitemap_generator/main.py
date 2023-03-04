import pprint
import datetime
from SiteScraper import SiteScraper


website = "http://web.pzjudo.pl/"
# website = "https://www.britishjudo.org.uk/"

# creating instance of sitescraper
ss1 = SiteScraper(website, 10)
# links = ss1.bfs_scraper_paths_only()
links = ss1.dfs_scraper()

# pprint.pprint(links)


current_time = datetime.datetime.now()

filename = "website_links-"
filename += str(current_time.date())
filename += "-"
filename += str(current_time.time().hour)
filename += "-"
filename += str(current_time.time().minute)
filename += ".txt"

fp = open(filename, "w")

print('all links: ', str(links))
print('writing to file ', filename)
for x in links:
    print(x)
    fp.write(x + '\n')

fp.close()
