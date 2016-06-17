import requests
import json
from ss_viewer.forms import SearchByTranscriptionFactorForm
from django.core.urlresolvers import reverse
from django.shortcuts import render
from ss_viewer.views.shared import Paging
from ss_viewer.views.shared import MotifTransformer, TFTransformer
from ss_viewer.views.shared import APIUrls 
from ss_viewer.views.shared import StandardFormset 


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
    api_search_query = { 'motif' : motif_value,
                         'pvalue_rank': form_data['pvalue_rank_cutoff'],
                         'from_result' : search_request_params['search_result_offset']
                       }

    api_response = requests.post( APIUrls.setup_api_url('search-by-tf'),
             json=api_search_query, headers={'content-type':'application/json'})

    response_json = None
    if api_response.status_code == 204:
        status_message = 'No matching rows.'
    else:
        response_json = json.loads(api_response.text)

        mt = MotifTransformer()
        response_data = mt.transform_motifs_to_transcription_factors(response_json['data'])

        status_message = 'Got ' + str(response_json['hitcount']) + ' rows back from API.'
        status_message += ' page shown ' + str(search_request_params['page_of_results_to_display'])
        form_data['page_of_results_shown'] = search_request_params['page_of_results_to_display']

        hitcount = response_json['hitcount']
        search_paging_info = Paging.get_paging_info_for_display(hitcount,
                                           search_request_params['page_of_results_to_display'])

        tf_search_form = SearchByTranscriptionFactorForm(form_data)

    context = StandardFormset.setup_formset_context(tf_form=tf_search_form)
    context.update({'api_response' : response_data,
                    'search_paging_info' : search_paging_info,
                    'status_message'     : status_message})
    return render(request, searchpage_template, context)




