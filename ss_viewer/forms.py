from django import forms
from django.conf import settings
import os
import pickle
import re



#Each form type has a p-value cutoff and a page number of results shown.
#prefixes explained here: https://docs.djangoproject.com/en/1.11/ref/forms/api/#prefixes-for-forms
#IN PROGRESS: instead of having all of the forms have these contorls on them, 
# have all of the shared controls on one particular form.
class SharedSearchControlsForm(forms.Form):
    default_cutoff = 0.05
    pvalue_tip = 'Show results with pvalues less than or equal to this '
    styled_widget = forms.NumberInput(attrs={'class':'form-control','step':"0.0000001" }) 

    page_of_results_shown = forms.IntegerField(widget = forms.HiddenInput(), required = False)
    previous_version_of_sort_order = forms.CharField(widget = forms.HiddenInput(), required = False)

    #taking the word 'cutoff' off of these.
    pvalue_rank = forms.FloatField(widget=styled_widget,
                                          max_value=1, 
                                          min_value=0, 
                                          initial=default_cutoff,
                                          required=False)

    pvalue_snp = forms.FloatField(widget=styled_widget, 
                                           max_value=1,
                                           min_value=0, 
                                           required = False)
 
    pvalue_ref = forms.FloatField(widget=styled_widget, 
                                           max_value=1,
                                           min_value=0, 
                                           required = False)
   
    #TODO: try removing the follwoing 2 lines and see if anything bad happens. 
    #use_these_choices = ( ("lt", "<"), ("gte", u"\u2265"))
    #styled_widget = forms.Select(attrs={ "style" : "float:left; margin-top:5px;"  })

    pvalue_snp_direction = forms.CharField(widget = forms.HiddenInput(), required = False)
    pvalue_ref_direction = forms.CharField(widget = forms.HiddenInput(), required = False)

    sort_order = forms.CharField(widget = forms.HiddenInput(), required = False)

    ic_options = [('1','Low'), #Low degerneracy -> high information content.
                  ('2','Moderate'),
                  ('3','High'),
                  ('4','Very High'),]
    #Lifted from 
    #https://stackoverflow.com/questions/2229029/django-choicefield-with-
    #   checkboxselectmultiple-all-selected-by-default/14364035
    ic_filter = forms.MultipleChoiceField(choices=ic_options,
      required = False, 
      widget=forms.CheckboxSelectMultiple(attrs={"checked":"", 'class':'ic-filter'}))
    def clean(self):
        cleaned_data = super(SharedSearchControlsForm, self).clean()
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

class SearchBySnpidForm(forms.Form):
    prefix = 'snpid'
    styled_widget = forms.Textarea(attrs={'class':'form-control', 
                                          'cols': '25', 'rows': '3' } )
    raw_requested_snpids = forms.CharField(
                                     widget=styled_widget,
                                     max_length=100000,
                                     strip=True,
                                     required=False)

    file_of_snpids = forms.FileField(required=False,
                                     label = "File of SNPids",
                                     max_length=100000)
 
    def clean(self):
        cleaned_data = super(SearchBySnpidForm, self).clean()
        snpid_file = cleaned_data.get('file_of_snpids')
        snpid_textbox_contents = cleaned_data.get('raw_requested_snpids')
        snpid_list = None
   
        if (snpid_file and snpid_textbox_contents):
            raise forms.ValidationError(('Specify SNPids in the textbox,'
                                        ' OR provide a file, not both.'),
                                         code='too-many-inputs')
        
        if (not(snpid_file or snpid_textbox_contents)):
            raise forms.ValidationError(('You must specify SNPids in the textbox,'
                                        ' OR provide a file.'),
                                         code='missing-input')
        if not snpid_file:
            snpid_list  = \
                 SnpidSearchUtils.clean_and_validate_snpid_text_input(
                                                     snpid_textbox_contents)
        else:
            #TODO: clean this up down here.
            print "all methods available on snpid_file ; " + repr(dir(snpid_file))
            print "snpid_file size " + str(snpid_file.size)
            print "snpid_file content type " + snpid_file.content_type
            if not snpid_file.size <= 50000:
                raise forms.ValidationError(('File is too large. \
                   Submit a text file with at most 1,000 SNPids.'))
            if not snpid_file.content_type == 'text/plain':
                raise forms.ValidationError( 
                 ('File provided is not a text file. \
                   Submit a text file containing at most, 1,000 SNPids.') )
            text_in_file = snpid_file.read()
            snpid_list =  \
                 SnpidSearchUtils.clean_and_validate_snpid_text_input(
                                                          text_in_file)
        if snpid_list is None: 
            raise forms.ValidationError(
                                ('No properly formatted SNPids in the text.'))
        max_snpids = settings.HARD_LIMITS['MAX_NUMBER_OF_SNPIDS_ALLOWED']
        if len(snpid_list) > max_snpids:
            snpid_list = snpid_list[:max_snpids]
        cleaned_data['snpid_list'] = snpid_list
        cleaned_data['raw_requested_snpids'] = ", ".join(snpid_list)


#A separate form for searching through the data by genomic location
class SearchByGenomicLocationForm(forms.Form):
    prefix = 'gl_region'

    gl_start_pos = forms.IntegerField(widget=
                      forms.NumberInput(attrs={"class":'form-control', 'step':1}), 
                      required=False,
                      min_value = 0 )

    gl_end_pos = forms.IntegerField(widget=
                       forms.NumberInput(attrs={"class":'form-control', 'step':1}),
                       required=False,
                       min_value = 1)

    chromosomes = [ "ch" + str(x) for x in range(1, 23) ]
    chromosomes.extend(['chX', 'chY', 'chM'])
    #all of the choices look like this: 
    #choices_for_chromosome =  ( ('ch1', 'ch1' ), ) 
    styled_widget = forms.Select(attrs={"class":"form-control"})
    selected_chromosome = forms.ChoiceField(widget=styled_widget,
                                            choices= zip(chromosomes,chromosomes),
                                            label="Chromosome")
    #ensure ranges are within hard limits.  
    def clean(self):
        cleaned_data = super(SearchByGenomicLocationForm, self).clean()
        start_pos = cleaned_data.get('gl_start_pos')
        end_pos = cleaned_data.get('gl_end_pos')
        if start_pos is None or end_pos is None:
            raise forms.ValidationError(('Missing start or end coordinate or both.'))

        if start_pos > end_pos:
            raise forms.ValidationError(('Start position must be less than or equal'
                                        ' to the end position.'),
                                        code='region-size-0'  )
        max_size_of_region = \
          settings.HARD_LIMITS['MAX_NUMBER_OF_BASES_IN_GENOMIC_LOCATION_REQUEST']
        if end_pos - start_pos > max_size_of_region: 
            raise forms.ValidationError(
                        ('The size of the specified region must be'
                        'less than or equal to {:,}.'.format(max_size_of_region)
                                       ), code='region-size-too-large')

 
class SearchByTranscriptionFactorForm(forms.Form):
    prefix = 'trans_factor'
    tf_library_options=[('jaspar','JASPAR'),
                        ('encode','ENCODE')]
    styled_widget = forms.RadioSelect(attrs={"class" : "form-control"})
    tf_library = forms.ChoiceField(choices=tf_library_options,
                                   widget=styled_widget,
                                   initial='jaspar')
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
  
    styled_widget = forms.Select(attrs={"class":"form-control"})

    trans_factor = forms.ChoiceField(widget = styled_widget,
                                     choices = use_these_choices, 
                                     required = False)

    other_styled_widget = forms.Select(attrs={"class":"form-control" })

    encode_lut = None
    fpath = os.path.dirname(__file__) + '/lookup-tables' +\
             '/encode_family_prefixes_only.pkl'
    with open(fpath, 'r') as f:
        encode_lut = pickle.load(f)

    use_these_encode_choices = [ (c, c) for c in set(encode_lut.values() ) ]
    use_these_encode_choices = sorted(tuple(use_these_encode_choices))

    encode_trans_factor = forms.ChoiceField(widget = other_styled_widget,
                                            choices = use_these_encode_choices,
                                            required = False)

class SearchBySnpidWindowForm(forms.Form):
    prefix = 'snpid_window'
    styled_widget = forms.TextInput(attrs={"class":"form-control"})
    snpid = forms.CharField(widget = styled_widget) 
    snpid.error_messages = {'required': 'Missing SNPid (required).'}
    styled_widget = forms.NumberInput(
               attrs={"class"   : 'form-control',
                      "step"    : 1 })

    window_size = forms.IntegerField(
                   widget = styled_widget,
                   initial = 100, 
                   min_value = 0,
                   max_value =\
     settings.HARD_LIMITS['MAX_NUMBER_OF_BASES_IN_GENOMIC_LOCATION_REQUEST']/2 )
    window_size.error_messages =  \
           { 'required': 'Missing window size (required).'}

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



class SearchByGeneNameForm(forms.Form):
    prefix='gene_name'
    styled_widget = forms.TextInput(attrs={"class":"form-control"})
    gene_name = forms.CharField(widget = styled_widget,
                                required = True)

    styled_widget = forms.NumberInput(attrs={"class":'form-control', 'step':1})
    window_size = forms.IntegerField(
       widget = styled_widget,
       required = True,
       initial = 100, 
       min_value = 0, 
       max_value = \
        settings.HARD_LIMITS['MAX_NUMBER_OF_BASES_IN_GENOMIC_LOCATION_REQUEST']
                         / 2 )
    window_size.error_messages = { 'required': 'Missing window size (required).'}

    def clean(self):
        cleaned_data = super(SearchByGeneNameForm, self).clean()    
        if not 'gene_name' in cleaned_data:          
            raise forms.ValidationError('Gene name is missing.');       
        gene_nm = cleaned_data['gene_name'].decode('utf-8').upper()
        cleaned_data['gene_name'] = gene_nm.encode('utf-8') 


