from django.shortcuts import render
from django.http import HttpResponse, FileResponse, Http404
from django.template import loader
from .forms import SitemapForm
from django.conf import settings as django_settings
import os

from .SiteScraper import SiteScraper
import datetime
import json

# Create your views here.
def main(request):

    # specifying for to render and initial value for radio button
    sitemap_settings_form = SitemapForm(initial={'sitemap_type': 'None', 'xml_format': 'structured'})

    if request.method == 'GET':
        return render(request, "index.html", {'form': sitemap_settings_form})

    if request.method == 'POST':

        form = SitemapForm(request.POST)
        print(form.errors)

        if form.is_valid():
            root_url = form.cleaned_data['url']
            max_pages = form.cleaned_data['max_pages']
            sitemap_mode = form.cleaned_data['sitemap_type']
            sitemap_type = form.cleaned_data['xml_format']
            include_visual_sitemap = form.cleaned_data['include_visual_sitemap']

            # creating instance of sitescraper
            ss1 = SiteScraper(url=root_url, max_nodes=max_pages, mode='None', sitemap_type=sitemap_type)
            links = ss1.bfs_scraper()
            print('COLLECTED LINKS (NUMBER)')
            print(len(links))

            # reading file with URL tree structure
            url_tree_path = os.path.join(django_settings.STATIC_ROOT, 'tree_structure', 'url_tree.txt').replace("\\", "/")
            f = open(url_tree_path, 'r', encoding='utf-8')
            file_content = f.read()
            f.close()

            # read the sitemap image
            image_path = os.path.join(django_settings.MEDIA_ROOT, 'plotka.PNG')

            # Open the image file and create a FileResponse object
            with open(image_path, 'rb') as f:
                sitemap_image = FileResponse(f)

            # Set the content type of the response to 'image/png' (or the appropriate type)
            sitemap_image['Content-Type'] = 'image/svg+xml'
            # sitemap_image['Content-Type'] = 'image/png'

            return render(request,
                          'sitemap.html',
                          {'links': links,
                           'url_tree_structure': file_content,
                           'sitemap_image': sitemap_image,
                           'to_include_sitemap_img': include_visual_sitemap})

    # return HttpResponse('xdd')


def download_xml_sitemap(request):
    file_path = os.path.join(django_settings.XML_SITEMAP_ROOT, 'sitemap.xml')

    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="text/xml")
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
            return response
    raise Http404

def download_diagram_sitemap(request):
    file_path = os.path.join(django_settings.MEDIA_ROOT, 'diagram.svg')

    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="image/svg+xml")
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
            return response
    raise Http404

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