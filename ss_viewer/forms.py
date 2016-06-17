from django import forms
from django.conf import settings
import os
import pickle


#Each form type has a p-value cutoff and a page number of results shown.
class GenericSearchForm(forms.Form):
    default_cutoff = 0.05
    pvalue_tip = 'Show results with pvalues less than or equal to this '
    styled_widget = forms.NumberInput(attrs={'class':'form-control','step':"0.0000001", 
                                             'title': pvalue_tip }) 
    pvalue_rank_cutoff = forms.FloatField(widget=styled_widget,
                                          max_value=1, 
                                          min_value=0, 
                                          initial=default_cutoff,
                                          )
    page_of_results_shown = forms.IntegerField(widget = forms.HiddenInput(), required = False)
    

class SearchBySnpidForm(GenericSearchForm):
    default_dummy_search = ("rs539483321, rs576894892, \
                             rs553761389, rs757299236, rs770590115")
    text_to_explain_snpbox = "Enter snpids to lookup scores data for"
    snpid_tip = "Enter a list of snpids to search for."
    styled_widget = forms.Textarea(attrs={'class':'form-control', 
                                          'title': snpid_tip})
    raw_requested_snpids = forms.CharField(widget=styled_widget,
                                     max_length=100000,
                                     strip=True,
                                     required=False,
                                     label=text_to_explain_snpbox,
                                     initial=default_dummy_search,
                                     )
    file_of_snpids = forms.FileField(required=False) #standard everything
    default_cutoff = 0.05
    pvalue_tip = 'Show results with pvalues less than or equal to this '
    styled_widget = forms.NumberInput(attrs={'class':'form-control','step':"0.0001", 
                                             'title': pvalue_tip }) 
    field_order =  ('raw_requested_snpids', 'file_of_snpids', 'pvalue_rank_cutoff', 'page_of_results_shown')
 
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
class SearchByGenomicLocationForm(GenericSearchForm):
    default_data = None   #don't need this.

    gl_pos_label_text = { 'start' : 'Start position on chromosome',
                          'end'   : 'End position on chromosome.' }

    # These defaults are here because I know there's development subset 
    # data in this range.
    default_start_pos = 10000;    default_end_pos = 10500

    # TODO: is there a way to put meaningful maximum values on these here?
    styled_widget = forms.NumberInput(attrs={"class":'form-control','step':1})
    gl_start_pos = forms.IntegerField(widget = styled_widget,
                                      label = gl_pos_label_text['start'], 
                                      required = True,
                                      initial = default_start_pos,
                                      min_value = 0 )

    gl_end_pos = forms.IntegerField(widget = styled_widget,
                                    label = gl_pos_label_text['end'],
                                    required = False, 
                                    initial = default_end_pos,
                                    min_value = 1)

    choices_for_chromosome =  ( ('ch1', 'ch1' ), ) 
    styled_widget = forms.Select(attrs={"class":"form-control"})
    selected_chromosome = forms.ChoiceField(widget=styled_widget,
                                            choices=choices_for_chromosome,
                                            label="Select a chromosome.")

    field_order =  ('gl_start_pos', 'gl_end_pos', 'selected_chromosome', 'pvalue_rank_cutoff', 'page_of_results_shown')
  

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
                                        ' to the end position.'),
                                        code='region-size-0'  )
         
        max_size_of_region = settings.HARD_LIMITS['MAX_NUMBER_OF_SNPIDS_ALLOWED_TO_REQUEST']
        if end_pos - start_pos > max_size_of_region: 
            raise forms.ValidationError(('The size of the specified region must be'
                                       'less than or equal to.' + 
                                        str(max_size_of_region)   ),
                                       code='region-size-too-large' )

 
class SearchByTranscriptionFactorForm(GenericSearchForm):
 
    lut = None
    fpath = os.path.dirname(__file__) + '/lookup-tables' +\
             '/lut_tfs_by_jaspar_motif.pkl'

    with open(fpath, 'r') as f:
        lut = pickle.load(f)

    tf_choices = tuple(lut.items())

    #tf_choices = tuple(sorted(set(lut.values())))
    tf_choices = sorted(tf_choices, key=lambda x:(x[1], x[0]))
    use_these_choices = []

    for c in set(lut.values()):
        use_these_choices.append((c, c)) 

    use_these_choices = sorted(tuple(use_these_choices))
   
    styled_widget = forms.Select(attrs={"class":"form-control"})
    trans_factor = forms.ChoiceField(widget = styled_widget,
                                     choices = use_these_choices, 
                                     label = "Select a transcription factor.")

    field_order =  ('trans_factor', 'pvalue_cutoff', 'page_of_results_shown')
