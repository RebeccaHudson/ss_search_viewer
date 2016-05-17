from django import forms
from django.conf import settings

class ScoresSearchForm(forms.Form):
   some_fake_snpids = "rs559407913  rs557153083 rs9431596"
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


#This is just one way to specify what data you are looking for.
#TODO: this should replacde the ScoresSearch form; it needs to be renamed...
class SearchBySnpidForm(forms.Form):
   some_fake_snpids = "rs559407913  rs557153083 rs9431596"
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
     cleaned_data = super(SearchBySnpidForm, self).clean()
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




#A separate form for searching through the data by genomic location
class SearchByGenomicLocationForm(forms.Form):
  default_data = None   #don't need this.

  gl_pos_label_text = { 'start' : 'Start position on chromosome',
                        'end'   : 'End position on chromosome.' }

  gl_start_pos = forms.IntegerField(label = gl_pos_label_text['start'], 
                                    required = True,
                                    min_value = 1 )

  gl_end_pos = forms.IntegerField(label = gl_pos_label_text['end'],
                                  required = False, 
                                  min_value = 0)

  choices_for_chromosome =  ( ('ch1', 'ch1' ), ) 
  selected_chromosome = forms.ChoiceField(choices=choices_for_chromosome,
                                          label="Select a chromosome.")
   #ensure ranges are within hard limits.  
  def clean(self):
    cleaned_data = super(SearchByGenomicLocationForm, self).clean()
    
    start_pos = cleaned_data.get('gl_start_pos')
    end_pos = cleaned_data.get('gl_end_pos')

    if start_pos is None:
      raise forms.ValidationError('We shouldn\'t be here', code='bad-case')

    if end_pos is None:
      end_pos = start_pos + int(settings.QUERY_DEFAULTS['DEFAULT_REGION_SIZE'])
      cleaned_data['gl_end_pos'] = end_pos

    if start_pos > end_pos:
      raise forms.ValidationError(('Start position must be less than or equal'
                                    'to the end position.'),
                                    code='region-size-0'  )
     
    max_size_of_region = settings.HARD_LIMITS['MAX_NUMBER_OF_SNPIDS_ALLOWED_TO_REQUEST']
    if end_pos - start_pos > max_size_of_region: 
      raise forms.ValidationError(('The size of the specified region must be'
                                   'less than or equal to.' + 
                                    str(max_size_of_region)   ),
                                   code='region-size-too-large' )









