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
            links = ss1.dfs_scraper()

            return render(request, 'sitemap.html', {'links': links})