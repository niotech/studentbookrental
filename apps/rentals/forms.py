from django import forms
from django.contrib.auth import get_user_model

from .models import Rental, Book

User = get_user_model()

class RentalForm(forms.ModelForm):
    book = forms.ModelChoiceField(queryset=Book.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    user = forms.ModelChoiceField(queryset=User.objects.filter(is_staff=False), widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Rental
        fields = ['user', 'book']

    def __init__(self, *args, **kwargs):
        super(RentalForm, self).__init__(*args, **kwargs)
        self.fields['user'].label = "Student"