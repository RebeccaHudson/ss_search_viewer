from django import forms

class ScoresSearchForm(forms.Form):
   raw_requested_snpids = forms.CharField(widget=forms.Textarea,
                                          max_length=100000, strip=True)
   #OTHER FIELDS WILL APPEAR HERE...
