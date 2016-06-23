import requests
import json
from ss_viewer.forms import SearchByTranscriptionFactorForm
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.shortcuts import redirect

from ss_viewer.views.shared import PValueFromForm
from ss_viewer.views.shared import Paging
from ss_viewer.views.shared import MotifTransformer, TFTransformer
from ss_viewer.views.shared import APIUrls 
from ss_viewer.views.shared import StandardFormset 
from ss_viewer.views.shared import APIResponseHandler 

def copy_valid_form_data_into_hidden_fields(form_data):
    fields_to_copy = ['pvalue_rank_cutoff', 'trans_factor']
    for form_field in fields_to_copy:
        form_data['prev_search_'+form_field] = form_data[form_field]
    return form_data


def handle_search_by_trans_factor(request):
    if request.method != 'POST':
        return redirect(reverse('ss_viewer:multi-search'))

    tf_search_form = SearchByTranscriptionFactorForm(request.POST)

    if not tf_search_form.is_valid() and not request.POST['action'] == 'Download Results':
        context = StandardFormset.setup_formset_context(tf_form=tf_search_form)
        return StandardFormset.handle_invalid_form(request, context)

    form_data = tf_search_form.cleaned_data

    #offer a download of results currently shown, use the values copied into the 
    #hidden controls on the previous form POST.
    if request.POST['action'] == 'Download Results':
        motif_value = tft.lookup_motifs_by_tf(form_data['prev_search_trans_factor'])
        pvalue_rank = form_data['prev_search_pvalue_rank']
        previous_search_params = {'motif' : motif_value, 'pvalue_rank':   pvalue_rank}
        return APIResponseHandler.handle_download_request(previous_search_params, 'search-by-tf')

    tft = TFTransformer()
    motif_value = tft.lookup_motifs_by_tf(form_data['trans_factor'])

    pvalue_rank = PValueFromForm.get_pvalue_rank_from_form(tf_search_form)

    search_request_params = Paging.get_paging_info_for_request(request,
                                                form_data['page_of_results_shown'])

    api_search_query = {'motif' : motif_value, 'pvalue_rank':   pvalue_rank}
    api_search_query.update({'from_result' : search_request_params['search_result_offset']})

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
