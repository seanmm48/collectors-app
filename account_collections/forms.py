from django import forms
from .models import Collection, Item

class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ['name', 'theme', 'description']

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'theme', 'description', 'purchased_price', 'retail_price', 'date_purchased', 'image']
