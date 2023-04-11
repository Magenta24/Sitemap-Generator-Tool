from django.shortcuts import render
from django.http import HttpResponse, FileResponse, Http404
from django.template import loader
from .forms import SitemapForm
from django.conf import settings as django_settings
import os
import time
import asyncio

from .SiteScraper import SiteScraper
import datetime
import json


# Create your views here.
def main(request):
    # specifying for to render and initial value for radio button
    sitemap_settings_form = SitemapForm(
        initial={'sitemap_type': 'None', 'xml_format': 'structured', 'scraper_algo': 'bfs'})

    if request.method == 'GET':
        return render(request, "index.html", {'form': sitemap_settings_form})

    # return HttpResponse('xdd')


def scrap(request):
    if request.method == 'POST':

        form = SitemapForm(request.POST)
        print(form.errors)

        if form.is_valid():
            root_url = form.cleaned_data['url']
            max_pages = form.cleaned_data['max_pages']
            sitemap_mode = form.cleaned_data['sitemap_type']
            sitemap_type = form.cleaned_data['xml_format']
            include_visual_sitemap = form.cleaned_data['include_visual_sitemap']
            scraper_algo = form.cleaned_data['scraper_algo']
            thing_to_search = form.cleaned_data['thing_to_search']

            # creating instance of sitescraper
            ss1 = SiteScraper(url=root_url, max_nodes=max_pages, mode='None', sitemap_type=sitemap_type, parser='html',
                              to_search=thing_to_search, crawl_delay=False)

            st = time.time()

            # choosing algorithm for scraper
            if scraper_algo == 'bfs':
                links = ss1.bfs_scraper()
            elif scraper_algo == 'dfs':
                links = ss1.dfs_scraper()

            et = time.time()
            execution_time = round((et - st), 2)

            search_results = ss1.search_results

            print('COLLECTED LINKS (NUMBER)')
            print(len(links))

            # reading file with URL tree structure
            url_tree_path = os.path.join(django_settings.STATIC_ROOT, 'tree_structure',
                                         (ss1.base_filepath + '-url_tree.txt')).replace("\\", "/")
            f = open(url_tree_path, 'r', encoding='utf-8')
            file_content = f.read()
            f.close()

            return render(request,
                          'sitemap.html',
                          {'links': links,
                           'url_tree_structure': file_content,
                           'to_include_sitemap_img': include_visual_sitemap,
                           'collected_no': ss1.pages_collected_no,
                           'search_results': search_results,
                           'execution_time': execution_time,
                           'base_filepath': ss1.base_filepath,
                           'images': ss1.images,
                           'docs': ss1.docs}
                          )


def download_xml_sitemap(request):
    base_path = request.GET.get('base_filepath')
    file_path = os.path.join(django_settings.XML_SITEMAP_ROOT, (base_path + '-sitemap.xml'))

    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="text/xml")
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
            return response
    raise Http404


def download_diagram_sitemap(request):
    base_path = request.GET.get('base_filepath')
    file_path = os.path.join(django_settings.MEDIA_ROOT, (base_path + '-diagram.svg'))

    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="image/svg+xml")
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)

            return response
    raise Http404


async def loading_screen(request):
    return render(request, "loading.html")


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
