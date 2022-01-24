from django import forms
from .models import Image

'''
class ImageForm(forms.ModelForm):
    """Form for the image model"""
    class Meta:
        model = Image
        fields = ('title','image')
'''
class ImageForm(forms.Form):
    """Form for the image model"""
    #title = forms.CharField(max_length=50)
    image = forms.ImageField()

class LogoForm(forms.Form):
    image = forms.ImageField()
    image.widget.attrs.update({'id' : 'img_cls'})
    logo = forms.ImageField()
    logo.widget.attrs.update({'id' : 'img_cls'})
    '''
    x = forms.IntegerField()
    x.widget.attrs.update({'id' : 'x_cls'})
    y = forms.IntegerField()
    y.widget.attrs.update({'id' : 'x_cls'})
    '''
