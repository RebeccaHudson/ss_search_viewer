from django import forms
from django.conf import settings
import os
import pickle
import re

#Each form type has a p-value cutoff and a page number of results shown.
class GenericSearchForm(forms.Form):
    default_cutoff = 0.05
    pvalue_tip = 'Show results with pvalues less than or equal to this '
    styled_widget = forms.NumberInput(attrs={'class':'form-control','step':"0.0000001", 
                                             'title': pvalue_tip }) 

    page_of_results_shown = forms.IntegerField(widget = forms.HiddenInput(), required = False)


    pvalue_rank_cutoff = forms.FloatField(widget=styled_widget,
                                          max_value=1, 
                                          min_value=0, 
                                          initial=default_cutoff,
                                          label = "P-value cutoff",
                                          required=False 
                                          )

    pvalue_snp_cutoff = forms.FloatField(widget=styled_widget, 
                                           max_value=1,
                                           min_value=0, 
                                           initial=default_cutoff,
                                           label = "P-value SNP cutoff",
                                           required = False)
 
    pvalue_ref_cutoff = forms.FloatField(widget=styled_widget, 
                                           max_value=1,
                                           min_value=0, 
                                           initial=default_cutoff,
                                           label = "P-value Reference cutoff",
                                           required = False)
    
    use_these_choices = ( ("lt", "<"), ("gte", u"\u2265"))
    #"class":"form-control", 
    
    styled_widget = forms.Select(attrs={ "title" : "Select the cutoff direction.",
                                        "style" : "float:left; margin-top:5px;"  })
    pvalue_snp_direction  = forms.ChoiceField(widget=styled_widget,
                                     choices = use_these_choices, 
                                     required = False,
                                     label = "Select cutoff direction for pvalue SNP.")

    pvalue_ref_direction  = forms.ChoiceField(widget=styled_widget,
                                     choices = use_these_choices, 
                                     required = False,
                                     label = "Select cutoff direction for pvalue reference.")


    def clean(self):
        cleaned_data = super(GenericSearchForm, self).clean()
        if cleaned_data.get('pvalue_rank_cutoff') is None:
            cleaned_data['pvalue_rank_cutoff'] = 0.05
            print "assigned pvalue default"
        return cleaned_data
  
#Used for parsing out SNPids from text files uploaded on the SNPid search form.
class SnpidSearchUtils:
    @staticmethod
    def extract_snpids_from_textfield(text):
        gex = re.compile('(rs[0-9]+)', re.MULTILINE)  
        list_of_snpids = gex.findall(text)
        return list_of_snpids
    
    @staticmethod
    def clean_and_validate_snpid_text_input(text_input):
        snpids = SnpidSearchUtils.extract_snpids_from_textfield(text_input)
        deduped_snpids = list(set(snpids))  #don't allow any duplicate requests.
        if len(deduped_snpids) == 0:  
          raise forms.ValidationError("No valid SNPids have been included.")  
        return sorted(deduped_snpids)

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

    file_of_snpids = forms.FileField(required=False,
                                     label = "File of SNPids")
 
    def clean(self):
        cleaned_data = super(SearchBySnpidForm, self).clean()
        snpid_file = cleaned_data.get('file_of_snpids')
        snpid_textbox_contents = cleaned_data.get('raw_requested_snpids')
        snpid_list = None
   
        if (snpid_file and snpid_textbox_contents):
            raise forms.ValidationError(('Specify snpids in the textbox,'
                                        ' OR provide a file, not both.'),
                                         code='too-many-inputs')
        
        if (not(snpid_file or snpid_textbox_contents)):
            raise forms.ValidationError(('You must specify snpids in the textbox,'
                                        ' OR provide a file.'),
                                         code='missing-input')
        
        if not snpid_file:
            snpid_list  = \
                 SnpidSearchUtils.clean_and_validate_snpid_text_input(
                                                     snpid_textbox_contents)
        else:
            text_in_file = snpid_file.read()
            snpid_list =  \
                 SnpidSearchUtils.clean_and_validate_snpid_text_input(
                                                          text_in_file)
        if snpid_list is None: 
            raise forms.ValidationError(
                                ('No properly formatted SNPids in the text.'))
        cleaned_data['snpid_list'] = snpid_list
        cleaned_data['raw_requested_snpids'] = ", ".join(snpid_list)


#A separate form for searching through the data by genomic location
class SearchByGenomicLocationForm(GenericSearchForm):
    default_data = None   #don't need this.

    gl_pos_label_text = { 'start' : 'Start position on chromosome',
                          'end'   : 'End position on chromosome' }

    gl_start_pos = forms.IntegerField(widget=
                                        forms.NumberInput(attrs={"class":'form-control',
                                          'step':1, 
                                          "title": "Search for data in a region" +\
                                          " that begins at this position on the chromosome."}),
                                      label = gl_pos_label_text['start'], 
                                      required=False,
                                      min_value = 0 )

    gl_end_pos = forms.IntegerField(widget=
                                        forms.NumberInput(attrs={"class":'form-control',
                                          'step':1, 
                                          "title": "Search for data in a region" +\
                                          " that ends at this position on the chromosome."}),
                                    label = gl_pos_label_text['end'],
                                    required=False,
                                    min_value = 1)

    chromosomes = [ "ch" + str(x) for x in range(1, 23) ]
    chromosomes.extend(['chX', 'chY', 'chM'])
    #all of the choices look like this: choices_for_chromosome =  ( ('ch1', 'ch1' ), ) 
    styled_widget = forms.Select(attrs={"class":"form-control",
                                        "title": "Chromosome to search for data between the " +\
                                        "start and end positions specified."})
    selected_chromosome = forms.ChoiceField(widget=styled_widget,
                                            choices= zip(chromosomes,chromosomes),
                                            label="Select a chromosome")

    #ensure ranges are within hard limits.  
    def clean(self):
        cleaned_data = super(SearchByGenomicLocationForm, self).clean()
        start_pos = cleaned_data.get('gl_start_pos')
        end_pos = cleaned_data.get('gl_end_pos')

        if start_pos is None:
            start_pos = 0
            cleaned_data['gl_start_pos'] = start_pos

        if end_pos is None and start_pos is not None:
            end_pos = cleaned_data['gl_start_pos'] + \
                      int(settings.QUERY_DEFAULTS['DEFAULT_REGION_SIZE'])
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

    lut = None
    fpath = os.path.dirname(__file__) + '/lookup-tables' +\
             '/lut_tfs_by_jaspar_motif.pkl'
    with open(fpath, 'r') as f:
        lut = pickle.load(f)
 
    use_these_choices = []

    for c in set(lut.values()):
        use_these_choices.append((c, c)) 


    #lowercase the transcription factor name before alphabetizing.
    use_these_choices = sorted(tuple(use_these_choices), key=lambda x:(x[1].lower()))
  
    styled_widget = forms.Select(attrs={"class":"form-control",
                                        "title" : "Select the transcription factor here."})

    trans_factor = forms.ChoiceField(widget = styled_widget,
                                     choices = use_these_choices, 
                                     required = False,
                                     label = "Select JASPAR transcription factor")



    other_styled_widget = forms.Select(attrs={"class":"form-control",
                                              "title" : "Seelect an ENCODE transcription factor."})
    encode_lut = None
    fpath = os.path.dirname(__file__) + '/lookup-tables' +\
             '/lut_encode_prefixes.pkl'
    with open(fpath, 'r') as f:
        encode_lut = pickle.load(f)

    use_these_encode_choices = [ (c, c) for c in set(encode_lut.values() ) ]
    use_these_encode_choices = sorted(tuple(use_these_encode_choices))

    encode_trans_factor = forms.ChoiceField(widget = other_styled_widget,
                                            choices = use_these_encode_choices,
                                            label = "Select ENCODE transcription factor",
                                            required = False)

class SearchBySnpidWindowForm(GenericSearchForm):
    styled_widget = forms.TextInput(attrs={"class":"form-control",
                                           "title": "Search for data with a window "+\
                                                    "around the position of the "   +\
                                                    "snpid entered here." }) 
    snpid = forms.CharField(widget = styled_widget, 
                            label = "SNPid")
    snpid.error_messages = {'required': 'Missing SNPid (required).'}
    styled_widget = forms.NumberInput(attrs={"class"   : 'form-control',
                                             'step'    : 1,
                                             "title": "Search for data within + and - this "+\
                                                      "number of bases of the position of " +\
                                                      "the snpid."})
    #TODO: figure out what the max_value on this should actually be.
    window_size = forms.IntegerField(widget = styled_widget,
                                     label = "Window size",
                                     initial = 1000, 
                                     min_value = 0)
    window_size.error_messages = { 'required': 'Missing window size (required).'}



    def clean(self):
        cleaned_data = super(SearchBySnpidWindowForm, self).clean()
        gex = re.compile('(rs[0-9]+)')
        snpid = None
        if 'snpid' in cleaned_data:
          #this could be refactored.
          snpid = gex.search(cleaned_data['snpid'])
        else:
            raise forms.ValidationError('SNPid is missing.');       
 
        if snpid is not None:
            cleaned_data['snpid'] =  snpid.group(1)
        else:
            raise forms.ValidationError(('SNPid not properly formatted.'),
                                        code='bad-snpid'  )



class SearchByGeneNameForm(GenericSearchForm):
    styled_widget = forms.TextInput(attrs={"class":"form-control",
                                           "title" : "Name of the gene to search form."}) 
    gene_name = forms.CharField(widget = styled_widget,
                                label = "Gene Symbol",
                                required = True)

    styled_widget = forms.NumberInput(attrs={"class":'form-control',
                                             'step':1,
                                             "title" : "Search for data within the " +\
                                                       "region of the gene, as well " +\
                                                       " as + and - this many bases " +\
                                                       " of the gene's start and end position."})
    #TODO: figure out what the max_value on this should actually be.
    window_size = forms.IntegerField(widget = styled_widget,
                                     label = "Window size",
                                     required = True,
                                     initial = 1000, 
                                     min_value = 0)
    window_size.error_messages = { 'required': 'Missing window size (required).'}
