from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .forms import SitemapForm

from .SiteScraper import SiteScraper
import datetime
import json

# Create your views here.
def main(request):

    form = SitemapForm()

    if request.method == 'GET':
        return render(request, "index.html", {'form': form})

    if request.method == 'POST':
        form = SitemapForm(request.POST)

        if form.is_valid():
            root_url = form.cleaned_data['url']

            # creating instance of sitescraper
            ss1 = SiteScraper(root_url, 10)
            # links = ss1.simple_bfs_scraper()
            links = ss1.bfs_scraper_paths_only()

            return render(request, 'sitemap.html', {'links': links})

def check_url(request):
    xd = SiteScraper.check_url('http://web.pzjudo.pl/')
    res = ''
    res += ('scheme :' + xd['scheme'] + '<br>')
    res += ('netloc :' + xd['netloc'] + '<br>')
    res += ('path :' + xd['path'] + '<br>')
    res += ('query :' + xd['query'] + '<br>')
    res += ('fragment :' + xd['fragment'] + '<br>')

    return HttpResponse(res)

def sanitize_url(request):
    ss1 = SiteScraper('http://web.pzjudo.pl/', 10)
    xd = ss1.sanitize_url('')

    return HttpResponse(xd)