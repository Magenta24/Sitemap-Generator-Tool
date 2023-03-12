from django import forms


class SitemapForm(forms.Form):
    url = forms.CharField(label='Provide URL', required=True)
    max_pages = forms.IntegerField(label='Maximum number of pages bot will crawl', initial=10)
    max_depth = forms.IntegerField(label='Maximum depth', initial=10)

    sitemap_choices = [
        ('1', 'Everything sitemap'),
        ('2', 'Image sitemap'),
        ('3', 'PDF sitemap')
    ]
    sitemap_type = forms.ChoiceField(label='Sitemap type', widget=forms.RadioSelect, choices=sitemap_choices,
                                     required=True)

    xml_format_choices = [
        ('1', 'Flat'),
        ('2', 'Structured')
    ]
    xml_format = forms.ChoiceField(label='XML format', widget=forms.RadioSelect, choices=xml_format_choices,
                                   required=True)
