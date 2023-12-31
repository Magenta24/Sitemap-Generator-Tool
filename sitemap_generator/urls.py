"""sitemap_generator URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from sitemap_generator import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.main, name="main"),
    path("check_url/", views.check_url, name="check_url"),
    path("sanitize/", views.sanitize_url, name="sanitize"),
    path("download_xml_sitemap/", views.download_xml_sitemap, name="download_xml_sitemap"),
    path("download_diagram_sitemap/", views.download_diagram_sitemap, name="download_diagram_sitemap"),
    path("scrap/", views.scrap, name="scrap")
]
