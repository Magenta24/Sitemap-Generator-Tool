from django import forms
# from .models import Post


class SitemapForm(forms.Form):
    url = forms.CharField(label='Provide URL', required=True)
    max_pages = forms.IntegerField(label='Maximum number of pages bot will crawl', initial=10)
    max_depth = forms.IntegerField(label='Maximum depth', initial=10)
    img_sitemaps = forms.BooleanField()
    pdf_sitemaps = forms.BooleanField()
    all_sitemaps = forms.BooleanField()

    sitemap_choices = [
        ('1', 'Everythig sitemap'),
        ('2', 'Image sitemap'),
        ('3', 'PDF sitemap')
    ]
    sitemap_type = forms.ChoiceField(widget=forms.RadioSelect, choices=sitemap_choices, required=True)

# class SitemapFormModel(forms.ModelForm):
#
#     class Meta:
#         model = Post
#         fields = ('title', 'text')