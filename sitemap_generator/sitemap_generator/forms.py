from django import forms
# from .models import Post


class SitemapForm(forms.Form):
    url = forms.CharField(label='Provide URL', required=True)
    max_pages = forms.IntegerField(label='Maximum number of pages bot will crawl', initial=10)

# class SitemapFormModel(forms.ModelForm):
#
#     class Meta:
#         model = Post
#         fields = ('title', 'text')