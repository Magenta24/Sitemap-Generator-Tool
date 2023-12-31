from django import forms


class SitemapForm(forms.Form):
    url = forms.CharField(label='Provide URL', required=True, widget=forms.TextInput
    (attrs={
        'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block  p-2.5'}))
    thing_to_search = forms.CharField(label='Provide a word/phrase you would like to search for', required=False,
                                      widget=forms.TextInput
                                      (attrs={
                                          'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block  p-2.5'}))
    max_pages = forms.IntegerField(label='Maximum number of URLs to visit', initial=10,
                                   widget=forms.NumberInput(attrs={'class': 'rounded border py-2 px-3'}))
    max_depth = forms.IntegerField(label='Maximum depth', initial=10,
                                   widget=forms.NumberInput(attrs={'class': 'rounded border py-2 px-3'}))

    xml_format_choices = [
        ('flat', 'Flat'),
        ('structured', 'Structured')
    ]
    xml_format = forms.ChoiceField(label='XML format', widget=forms.RadioSelect, choices=xml_format_choices,
                                   required=True)

    include_visual_sitemap = forms.BooleanField(label='Include visual sitemap?', required=False)
    apply_crawl_delay = forms.BooleanField(label='Apply crawl delay?', required=False)

    scraper_algo_choices = [
        ('dfs', 'DFS'),
        ('bfs', 'BFS')
    ]
    scraper_algo = forms.ChoiceField(label='Scraper algorithm', widget=forms.RadioSelect, choices=scraper_algo_choices,
                                     required=True)
