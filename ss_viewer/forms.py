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
    prev_search_pvalue_rank_cutoff = forms.FloatField(widget = forms.HiddenInput(), required = False)

    page_of_results_shown = forms.IntegerField(widget = forms.HiddenInput(), required = False)
    

class SearchBySnpidForm(GenericSearchForm):
    text_to_explain_snpbox = "SNPids"
    snpid_tip = "Enter SNPids to search for."
    styled_widget = forms.Textarea(attrs={'class':'form-control', 
                                          'title': snpid_tip,
                                          'cols': '25', 'rows': '3'} )
    raw_requested_snpids = forms.CharField(
                                     widget=styled_widget,
                                     max_length=100000,
                                     strip=True,
                                     required=False,
                                     label=text_to_explain_snpbox,
                                     )

    prev_search_raw_requested_snpids = forms.CharField(widget = forms.HiddenInput(),
                                        required = False)
    file_of_snpids = forms.FileField(required=False) #standard everything
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
                          'end'   : 'End position on chromosome' }

    # These defaults are here because I know there's development subset 
    # data in this range.
    #default_start_pos = 10000;    default_end_pos = 100500
    # TODO: is there a way to put meaningful maximum values on these here?
    gl_start_pos = forms.IntegerField(widget=
                                        forms.NumberInput(attrs={"class":'form-control',
                                          'step':1, 
                                          "title": "Search for data in a region" +\
                                          " that begins at this position on the chromosome."}),
                                      label = gl_pos_label_text['start'], 
                                      required = True,
                                      min_value = 0 )
    prev_search_gl_start_pos = forms.IntegerField(widget = forms.HiddenInput(),
                                                required = False)
   

    gl_end_pos = forms.IntegerField(widget=
                                        forms.NumberInput(attrs={"class":'form-control',
                                          'step':1, 
                                          "title": "Search for data in a region" +\
                                          " that ends at this position on the chromosome."}),
                                    label = gl_pos_label_text['end'],
                                    required = False, 
                                    min_value = 1)

    prev_search_gl_end_pos = forms.IntegerField(widget = forms.HiddenInput(),
                                                required = False)

    chromosomes = [ "ch" + str(x) for x in range(1, 24) ]
    #all of the choices look like this: choices_for_chromosome =  ( ('ch1', 'ch1' ), ) 
    styled_widget = forms.Select(attrs={"class":"form-control",
                                        "title": "Chromosome to search for data between the " +\
                                        "start and end positions specified."})
    selected_chromosome = forms.ChoiceField(widget=styled_widget,
                                            choices= zip(chromosomes,chromosomes),
                                            label="Select a chromosome")

    prev_search_selected_chromosome = forms.CharField(widget = forms.HiddenInput(),
                                               required=False)
    field_order =  ('gl_start_pos', 'gl_end_pos', 
                    'selected_chromosome', 
                    'pvalue_rank_cutoff', 'page_of_results_shown')
  

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
 
    tf_library_options=[('jaspar','JASPAR'),
                        ('encode','ENCODE')]
    styled_widget = forms.RadioSelect(attrs={"class" : "form-control",
                                             "title" : "Select either the ENCODE or JASPAR motif library."})
    tf_library = forms.ChoiceField(choices=tf_library_options,
                                   widget=styled_widget,
                                   initial='jaspar',
                                   label = "Select a transcription factor library.")
    prev_search_tf_library = forms.CharField(widget = forms.HiddenInput(), required = False)




    lut = None
    fpath = os.path.dirname(__file__) + '/lookup-tables' +\
             '/lut_tfs_by_jaspar_motif.pkl'
    with open(fpath, 'r') as f:
        lut = pickle.load(f)
    tf_choices = tuple(lut.items())
    tf_choices = sorted(tf_choices, key=lambda x:(x[1], x[0]))
    use_these_choices = []

    for c in set(lut.values()):
        use_these_choices.append((c, c)) 

    use_these_choices = sorted(tuple(use_these_choices))
  
    styled_widget = forms.Select(attrs={"class":"form-control",
                                        "title" : "Select the transcription factor here."})
    trans_factor = forms.ChoiceField(widget = styled_widget,
                                     choices = use_these_choices, 
                                     required = False,
                                     label = "Select a transcription factor")




    other_styled_widget = forms.Select(attrs={"class":"form-control",
                                              "title" : "Seelect an ENCODE transcription factor."})
    encode_lut = None
    fpath = os.path.dirname(__file__) + '/lookup-tables' +\
             '/lut_encode_prefixes.pkl'
    with open(fpath, 'r') as f:
        encode_lut = pickle.load(f)

    encode_tf_choices = tuple(encode_lut.items())
    encode_tf_choices = sorted(encode_tf_choices, key=lambda x:(x[1], x[0]))
    
    use_these_encode_choices = [ (c, c) for c in set(encode_lut.values() ) ]
    use_these_encode_choices = sorted(tuple(use_these_encode_choices))

    encode_trans_factor = forms.ChoiceField(widget = other_styled_widget,
                                            choices = use_these_encode_choices,
                                            required = False)


    # hey there.    widget = forms.HiddenInput(), required = False)
    prev_search_trans_factor = forms.CharField(widget = forms.HiddenInput(),
                                               required=False)
    prev_search_encode_trans_factor = forms.CharField(widget = forms.HiddenInput(),
                                               required=False)



    field_order =  ('tf_library', 'trans_factor', 'pvalue_cutoff', 'page_of_results_shown')



class SearchBySnpidWindowForm(GenericSearchForm):
    styled_widget = forms.TextInput(attrs={"class":"form-control",
                                           "title": "Search for data with a window "+\
                                                    "around the position of the "   +\
                                                    "snpid entered here." }) 
    snpid = forms.CharField(widget = styled_widget)
    styled_widget = forms.NumberInput(attrs={"class"   : 'form-control',
                                             'step'    : 1,
                                             "title": "Search for data within + and - this "+\
                                                      "number of bases of the position of " +\
                                                      "the snpid."})
    prev_search_snpid = forms.CharField(widget = forms.HiddenInput(),
                                        required = False)
    #TODO: figure out what the max_value on this should actually be.
    window_size = forms.IntegerField(widget = styled_widget,
                                     label = "Window size",
                                     required = False,
                                     initial = 1000, 
                                     min_value = 0)

    prev_search_window_size = forms.IntegerField(widget = forms.HiddenInput(),
                                                required = False)
    field_order =  ('snpid', 'window_size', 'pvalue_cutoff', 'page_of_results_shown')



class SearchByGeneNameForm(GenericSearchForm):
    styled_widget = forms.TextInput(attrs={"class":"form-control",
                                           "title" : "Name of the gene to search form."}) 
    gene_name = forms.CharField(widget = styled_widget,
                                label = "Gene Symbol",
                                required = True)

    prev_search_gene_name = forms.CharField(widget = forms.HiddenInput(), 
                                            required = False)

    styled_widget = forms.NumberInput(attrs={"class":'form-control',
                                             'step':1,
                                             "title" : "Search for data within the " +\
                                                       "region of the gene, as well " +\
                                                       " as + and - this many bases " +\
                                                       " of the gene's start and end position."})
    #TODO: figure out what the max_value on this should actually be.
    window_size = forms.IntegerField(widget = styled_widget,
                                     label = "Window size",
                                     required = False,
                                     initial = 1000, 
                                     min_value = 0)

    prev_search_window_size = forms.IntegerField(widget = forms.HiddenInput(),
                                                required = False)
    field_order =  ('gene_name', 'window_size', 'pvalue_cutoff', 'page_of_results_shown')



