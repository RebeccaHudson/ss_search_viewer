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


def handle_search_by_trans_factor(request):
    if request.method != 'POST':
        return redirect(reverse('ss_viewer:multi-search'))

    tf_search_form = SearchByTranscriptionFactorForm(request.POST)

    if not tf_search_form.is_valid():
        context = StandardFormset.setup_formset_context(tf_form=tf_search_form)
        return StandardFormset.handle_invalid_form(request, context)

    form_data = tf_search_form.cleaned_data
    search_request_params = Paging.get_paging_info_for_request(request,
                                                form_data['page_of_results_shown'])

    trans_factor = form_data['trans_factor']
    tft = TFTransformer()
    motif_value = tft.lookup_motifs_by_tf(trans_factor)
    pvalue_rank = PValueFromForm.get_pvalue_rank_from_form(tf_search_form)
    api_search_query = {'motif' : motif_value,
                        'pvalue_rank':   pvalue_rank,
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

    return render(request, 
                 'ss_viewer/multi-searchpage.html',
                  context)




