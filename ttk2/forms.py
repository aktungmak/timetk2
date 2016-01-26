from django import forms

class NewNetcodeForm(forms.Form):
    network = forms.CharField(required=True, max_length=100,
              widget=forms.TextInput(attrs={'placeholder': 'Network'}),
              label='')
    activity = forms.CharField(required=True, max_length=100,
              widget=forms.TextInput(attrs={'placeholder': 'Activity'}),
              label='')
    name = forms.CharField(required=True, max_length=100,
              widget=forms.TextInput(attrs={'placeholder': 'Name'}),
              label='')
    description = forms.CharField(required=True, max_length=500,
              widget=forms.TextInput(attrs={'placeholder': 'Description'}),
              label='')
