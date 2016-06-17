import requests
import json
from django.shortcuts import redirect
from ss_viewer.forms import SearchByGenomicLocationForm
from django.core.urlresolvers import reverse
from django.shortcuts import render
from ss_viewer.views.shared import Paging
from ss_viewer.views.shared import MotifTransformer
from ss_viewer.views.shared import APIUrls 
from ss_viewer.views.shared import StandardFormset
from ss_viewer.views.shared import APIResponseHandler


def handle_search_by_genomic_location(request):
    if request.method != 'POST':
        return redirect(reverse('ss_viewer:multi-search'))

    gl_search_form = SearchByGenomicLocationForm(request.POST)

    if not gl_search_form.is_valid():
         context = StandardFormset.setup_formset_context(gl_form=gl_search_form)
         return StandardFormset.handle_invalid_form(request, context)

    form_data = gl_search_form.cleaned_data
    search_request_params = Paging.get_paging_info_for_request(request,
                                                         form_data['page_of_results_shown'])
    api_search_query = { 'chromosome' : form_data['selected_chromosome'],
                         'start_pos'  : form_data['gl_start_pos'],
                         'end_pos'    : form_data['gl_end_pos'],
                         'pvalue_rank': form_data['pvalue_rank_cutoff'],
                         'from_result': search_request_params['search_result_offset'] }
    shared_context = APIResponseHandler.handle_search(api_search_query, 
                                                      'search-by-gl',
                                                      search_request_params)
    #this 'turns the page'
    form_data['page_of_results_shown'] = search_request_params['page_of_results_to_display']

    new_gl_form = SearchByGenomicLocationForm(form_data)
    context = StandardFormset.setup_formset_context(gl_form = new_gl_form)
    context.update(shared_context)
    return render(request, 
                  'ss_viewer/multi-searchpage.html',
                   context)

