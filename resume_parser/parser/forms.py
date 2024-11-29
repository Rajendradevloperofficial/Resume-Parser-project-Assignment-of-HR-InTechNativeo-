from django import forms

class ResumeUploadForm(forms.Form):
    resume = forms.FileField()