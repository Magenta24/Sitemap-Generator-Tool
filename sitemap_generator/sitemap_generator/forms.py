from django import forms
# from .models import Post


class SitemapForm(forms.Form):
    url = forms.CharField(label='Provide URL', required=True)

# class SitemapFormModel(forms.ModelForm):
#
#     class Meta:
#         model = Post
#         fields = ('title', 'text')