import requests
import json
from ss_viewer.forms import SearchByTranscriptionFactorForm
from django.core.urlresolvers import reverse
from django.shortcuts import render
from ss_viewer.views.shared import Paging
from ss_viewer.views.shared import MotifTransformer, TFTransformer
from ss_viewer.views.shared import APIUrls 
from ss_viewer.views.shared import StandardFormset 
from ss_viewer.views.shared import APIResponseHandler 


def handle_search_by_trans_factor(request):
    if request.method == 'GET':
        return redirect(reverse('ss_viewer:multi-search'))

    if request.method == 'POST':
        searchpage_template = 'ss_viewer/multi-searchpage.html'
        tf_search_form = SearchByTranscriptionFactorForm(request.POST)

    search_paging_info  = None
    status_message = ""
    response_data = None

    if not tf_search_form.is_valid():
        context = StandardFormset.setup_formset_context(tf_form=tf_search_form)
        context.update({'status_message': "Invalid search. Try agian."})
        return render(request, searchpage_template, context)

    form_data = tf_search_form.cleaned_data

    trans_factor = form_data['trans_factor']
    tft = TFTransformer()
    motif_value = tft.lookup_motifs_by_tf(trans_factor)

    search_request_params = Paging.get_paging_info_for_request(request,
                                                form_data['page_of_results_shown'])
    api_search_query = {'motif' : motif_value,
                        'pvalue_rank': form_data['pvalue_rank_cutoff'],
                        'from_result' : search_request_params['search_result_offset']
                       }
    shared_context = APIResponseHandler.handle_search(api_search_query, 
                                                      'search-by-tf',
                                                      search_request_params)
    #the next line of code 'turns the page'
    form_data['page_of_results_shown'] = search_request_params['page_of_results_to_display']
    tf_search_form = SearchByTranscriptionFactorForm(form_data)
    context = StandardFormset.setup_formset_context(tf_form=tf_search_form)
    context.update(shared_context)
    #context.update({'api_response' : response_data,
    #                'search_paging_info' : search_paging_info,
    #                'status_message'     : status_message})
    return render(request, searchpage_template, context)




