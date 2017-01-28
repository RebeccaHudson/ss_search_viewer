import requests
import json
from ss_viewer.forms import SearchByTranscriptionFactorForm
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.shortcuts import redirect

from ss_viewer.views.shared import PValueFromForm
from ss_viewer.views.shared import PValueDictFromForm
from ss_viewer.views.shared import Paging
from ss_viewer.views.shared import MotifTransformer, TFTransformer
from ss_viewer.views.shared import APIUrls 
from ss_viewer.views.shared import StandardFormset 
from ss_viewer.views.shared import APIResponseHandler 
from ss_viewer.views.shared import StreamingCSVDownloadHandler 

def copy_valid_form_data_into_hidden_fields(form_data):
    fields_to_copy = ['pvalue_rank_cutoff', 'pvalue_ref_cutoff', 'pvalue_snp_cutoff','trans_factor', 'encode_trans_factor', 'tf_library']
    for form_field in fields_to_copy:
        if form_field in form_data:
            form_data['prev_search_'+form_field] = form_data[form_field]
    return form_data

def copy_hidden_fields_into_form_data(form_data):
    fields_to_copy = ['pvalue_rank_cutoff', 'pvalue_ref_cutoff', 'pvalue_snp_cutoff', 'trans_factor', 'encode_trans_factor', 'tf_library']
    for form_field in fields_to_copy:
       if 'prev_search_'+form_field in form_data: 
           print "copying " + form_field
           form_data[form_field]  = form_data['prev_search_'+form_field] 
    return form_data


def handle_search_by_trans_factor(request):
    if request.method != 'POST':
        return redirect(reverse('ss_viewer:multi-search'))

    #just take the previous_search values 
    # and copy them into a POST-like dictionary.
    # then pass that to the Form constructor.
    #translate the request.POST queryDict into a dict.
    tf_search_form = None
    if request.POST['action'] in ['Prev', 'Next']:
        #why isn't the transcription factor field being copied back?
        oneDict = request.POST.dict()
        oneDict = copy_hidden_fields_into_form_data(oneDict) 
        tf_search_form = SearchByTranscriptionFactorForm(oneDict)
    else: 
        tf_search_form = SearchByTranscriptionFactorForm(request.POST)

    if not tf_search_form.is_valid() and not request.POST['action'] == 'Download Results':
        context = StandardFormset.setup_formset_context(tf_form=tf_search_form)
        return StandardFormset.handle_invalid_form(request, context)

    form_data = tf_search_form.cleaned_data

    
    print "form data for tf search " + str(form_data)
    # ENCODE motifs are prefixes, JASPAR are actually mapped with TFTransformer
    if form_data['tf_library'] == 'encode':
        return handle_search_by_encode_trans_factor(request, form_data, pvalue_rank)   #this logic is inelegant because I need to 
                                                                   # finish it ASAP at this point.; consider tidying up.
    #otherwise, go with the previously-developed JASPAR library behavior (lookups for transcription factors)
    print "searching by jaspar.."

    tft = TFTransformer()
    #offer a download of results currently shown, use the values copied into the 
    #hidden controls on the previous form POST.
    if request.POST['action'] == 'Download Results':
        motif_value = tft.lookup_motifs_by_tf(form_data['prev_search_trans_factor'])
        pvalue_rank = form_data['prev_search_pvalue_rank_cutoff']
        previous_search_params = {'motif'  :  motif_value, 
                             'pvalue_rank' :  pvalue_rank,
                              'tf_library' : 'jaspar' }
        if form_data['prev_search_pvalue_ref_cutoff'] is not None:
            previous_search_params.update(
                         {'pvalue_ref'  : form_data['prev_search_pvalue_ref_cutoff']})
        if form_data['prev_search_pvalue_snp_cutoff'] is not None:
            previous_search_params.update(
                         {'pvalue_snp'  : form_data['prev_search_pvalue_snp_cutoff']})

        return StreamingCSVDownloadHandler.streaming_csv_view(request, 
                                                              previous_search_params, 
                                                              'search-by-tf')

    #if it's not the special paging actions, carry on as normal.
    motif_value = tft.lookup_motifs_by_tf(form_data['trans_factor'])
    search_request_params = Paging.get_paging_info_for_request(request,
                                                form_data['page_of_results_shown'])
    #pvalue_rank = PValueFromForm.get_pvalue_rank_from_form(tf_search_form)
    pvalue_dict = PValueDictFromForm.get_pvalues_from_form(tf_search_form)
    api_search_query = {'motif'       :  motif_value, 
                        'pvalue_rank' :  pvalue_dict['pvalue_rank_cutoff'],
                        'from_result' :  search_request_params['search_result_offset']}
    #onnly include pvalue_ref and pvalue_snp if they are present in the input.
    if 'pvalue_ref_cutoff' in pvalue_dict:
        api_search_query.update({'pvalue_ref'  : pvalue_dict['pvalue_ref_cutoff']})
    if 'pvalue_snp_cutoff' in pvalue_dict:
        api_search_query.update({'pvalue_snp'  : pvalue_dict['pvalue_snp_cutoff']})

    shared_context = APIResponseHandler.handle_search(api_search_query, 
                                                      'search-by-tf',
                                                       search_request_params)
    form_data = copy_valid_form_data_into_hidden_fields(form_data) 
    #the next line of code 'turns the page'
    form_data['page_of_results_shown'] = search_request_params['page_of_results_to_display']

    tf_search_form = SearchByTranscriptionFactorForm(form_data)
    context = StandardFormset.setup_formset_context(tf_form=tf_search_form)
    context.update(shared_context)

    return render(request, 
                 'ss_viewer/multi-searchpage.html',
                  context)




# Note/remember for ENCODE, the transcription factor is ABC the motif value is ABC-omg-why-is-this-name-so-long
def  handle_search_by_encode_trans_factor(request, form_data, pvalue_rank): 
    print "Searching by encode"
    if request.POST['action'] == 'Download Results':
        motif_prefix = form_data['prev_search_encode_trans_factor']
        pvalue_rank = form_data['prev_search_pvalue_rank_cutoff']
        previous_search_params = {'tf_library' :  'encode',
                                  'motif'      :  motif_prefix,
                                  'pvalue_rank':  pvalue_rank}
        return StreamingCSVDownloadHandler.streaming_csv_view(request, 
                                                              previous_search_params, 
                                                              'search-by-tf')

    motif_prefix = form_data['encode_trans_factor']
    #pvalue_rank = PValueFromForm.get_pvalue_rank_from_form(tf_search_form)
    search_request_params = Paging.get_paging_info_for_request(request,
                                                form_data['page_of_results_shown'])
    api_search_query = {'tf_library'  :  'encode', 
                        'motif'       :  motif_prefix, 
                        'pvalue_rank' :  pvalue_rank,
                        'from_result' :  search_request_params['search_result_offset']}

    shared_context = APIResponseHandler.handle_search(api_search_query, 
                                                      'search-by-tf',
                                                      search_request_params)

    form_data = copy_valid_form_data_into_hidden_fields(form_data) 
    #the next line of code 'turns the page'
    form_data['page_of_results_shown'] = search_request_params['page_of_results_to_display']

    tf_search_form = SearchByTranscriptionFactorForm(form_data)
    context = StandardFormset.setup_formset_context(tf_form=tf_search_form)
    context.update(shared_context)

    return render(request, 
                 'ss_viewer/multi-searchpage.html',
                  context)
