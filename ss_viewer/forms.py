from django import forms

class ScoresSearchForm(forms.Form):
   some_fake_snpids = "rs376201521  rs762269735   rs376019116"
   text_to_explain_snpbox = "Enter snpids to lookup scores data for"
   raw_requested_snpids = forms.CharField(widget=forms.Textarea,
                                    max_length=100000,
                                    strip=True,
                                    required=True,
                                    label=text_to_explain_snpbox,
                                    initial=some_fake_snpids)
   file_of_snpids = forms.FileField(required=False) #standard everything
   #validator changes will be needed to reflect the fact that 1 of these
   #must be specified, but I'll spit if you try to supply both.
   #OTHER FIELDS WILL APPEAR HERE...
