from django import forms

class ScoresSearchForm(forms.Form):
   some_fake_snpids = "rs376201521  rs762269735   rs376019116"
   raw_requested_snpids = forms.CharField(widget=forms.Textarea,
                                    max_length=100000,
                                    strip=True,
                                    required=True,
                                    initial=some_fake_snpids)
   #OTHER FIELDS WILL APPEAR HERE...
