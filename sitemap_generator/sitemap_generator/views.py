from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .forms import SitemapForm
from django.conf import settings as django_settings
import os

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
            max_pages = form.cleaned_data['max_pages']

            # creating instance of sitescraper
            ss1 = SiteScraper(root_url, max_pages)
            links = ss1.bfs_scraper_paths_only()
            # sitemap_path = os.path.join(django_settings.STATIC_URL, f'sitemap.xml')
            ss1.save_XML_sitemap(links, 'sitemap.xml')

            return render(request, 'sitemap.html', {'links': links})

def check_url(request):
    url = request.GET.get('url')
    print(url)

    xd = SiteScraper.check_url(url)
    res = ''
    res += ('scheme :' + xd['scheme'] + '<br>')
    res += ('netloc :' + xd['netloc'] + '<br>')
    res += ('path :' + xd['path'] + '<br>')
    res += ('query :' + xd['query'] + '<br>')
    res += ('fragment :' + xd['fragment'] + '<br>')

    return HttpResponse(res)

def sanitize_url(request):
    url = request.GET.get('url')
    ss1 = SiteScraper(url, 10)
    xd = ss1.sanitize_url(url)

    return HttpResponse(xd)