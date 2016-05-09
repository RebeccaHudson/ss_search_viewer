from django import forms

class ScoresSearchForm(forms.Form):
   some_fake_snpids = "rs376201521  rs762269735   rs376019116"
   text_to_explain_snpbox = "Enter snpids to lookup scores data for"
   raw_requested_snpids = forms.CharField(widget=forms.Textarea,
                                    max_length=100000,
                                    strip=True,
                                    required=False,
                                    label=text_to_explain_snpbox,
                                    initial=some_fake_snpids)
   file_of_snpids = forms.FileField(required=False) #standard everything
   #validator changes will be needed to reflect the fact that 1 of these
   #must be specified, but I'll spit if you try to supply both.
   #OTHER FIELDS WILL APPEAR HERE...

   #This is where we specify relationships for 1-or-the-other form inputs.
   #A user can specify SNPids. EITHER with a file or with the textox.
   def clean(self):
     cleaned_data = super(ScoresSearchForm, self).clean()
     print(str(cleaned_data))
     snpid_file = cleaned_data.get('file_of_snpids')
     snpid_textbox_contents = cleaned_data.get('raw_requested_snpids')

     #form.errors contains any errors that have come up by this point.

     if (snpid_file and snpid_textbox_contents):
       raise forms.ValidationError(('Specify snpids in the textbox,'
                                   ' OR provide a file, not both.'),
                                    code='too-many-inputs')
     
     if (not(snpid_file or snpid_textbox_contents)):
       raise forms.ValidationError(('You must specify snpids in the textbox,'
                                   ' OR provide a file.'),
                                    code='missing-input')
     return cleaned_data
