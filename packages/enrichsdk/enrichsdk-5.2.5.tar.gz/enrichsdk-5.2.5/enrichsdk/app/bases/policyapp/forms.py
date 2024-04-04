from django import forms
from .models import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout

class AppPolicyFormBase(forms.ModelForm):
    notes = forms.CharField( widget=forms.Textarea, required=False)
    class Meta:
        model = AppPolicyBase
        exclude = ('appname', 'namespace', 'created_by', 'modified_by')
        widgets = {
          'config': forms.Textarea(attrs={'rows':150, 'cols':200}),
        }
