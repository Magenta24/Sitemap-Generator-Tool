import requests
from bs4 import BeautifulSoup
import re

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

nodes = []
edges = []
level = 0

website_source = requests.get("http://web.pzjudo.pl/").text
print(website_source)

# soup of the website
soup = BeautifulSoup(website_source, 'html.parser') # html.parser is a default parser

# extracting all links <a> tags
links = soup.find_all('a')

# getting actual links (after href)
for link in links:
    url = link.get('href')
    print(url)
    nodes.append({link:url, level:levels, parent:None, children:[]})

# going 3 levels down the page
while level < 3:
    level += 1
    pass

