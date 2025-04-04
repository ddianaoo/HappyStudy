from django import forms
from .models import *


class CreateSubjectForm(forms.ModelForm):
    title = forms.CharField(label='Назва', widget=forms.TextInput(attrs={'class': 'form-control'}))
    school_year = forms.ChoiceField(label='Клас', choices=CLASSES_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    image = forms.ImageField(label='Іконка предмета', widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Subject
        fields = ('title', 'school_year', 'image')
