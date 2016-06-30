import requests
import json
import re
from ss_viewer.forms import SearchBySnpidWindowForm
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.shortcuts import redirect

from ss_viewer.views.shared import PValueFromForm
from ss_viewer.views.shared import Paging
from ss_viewer.views.shared import MotifTransformer, TFTransformer
from ss_viewer.views.shared import APIUrls 
from ss_viewer.views.shared import StandardFormset 
from ss_viewer.views.shared import APIResponseHandler 

from ss_viewer.views.shared import StreamingCSVDownloadHandler 

def copy_valid_form_data_into_hidden_fields(form_data):
    fields_to_copy = ['pvalue_rank_cutoff', 'snpid', 'window_size']
    for form_field in fields_to_copy:
        form_data['prev_search_' + form_field] = form_data[form_field]
    return form_data

def extract_snpid_from_textfield(text):
    gex = re.compile('(rs[0-9]+)')
    snpid = gex.search(text)
    return snpid.group(0)

def handle_snpid_window_search(request):
    if request.method != 'POST':
        return redirect(reverse('ss_viewer:multi-search'))

    snpid_window_search_form = SearchBySnpidWindowForm(request.POST)

    if not snpid_window_search_form.is_valid():
        context = StandardFormset.setup_formset_context(
                                     snpid_window_form=snpid_window_search_form)
        return StandardFormset.handle_invalid_form(request, context)

    form_data = snpid_window_search_form.cleaned_data

    requested_snpid = extract_snpid_from_textfield(form_data['snpid'])
    if requested_snpid is None:
        context = StandardFormset.setup_formset_context(
                                     snpid_window_form=snpid_window_search_form)
        return StandardFormset.handle_invalid_form(request,
                                              context, 
                                              status_message = "SNPid not properly formatted.")


    window_size = form_data['window_size']
    pvalue_rank = PValueFromForm.get_pvalue_rank_from_form(snpid_window_search_form)


      
    if request.POST['action'] == 'Download Results':
        pavlue_rank = form_data['prev_search_pvalue_rank_cutoff']
        window_size = form_data['prev_search_window_size']
        snpid = form_data['prev_search_snpid']
        previous_search_params = { 'snpid'       : snpid, 
                                   'window_size' : window_size, 
                                   'pvalue_rank' : pvalue_rank  } 
        return StreamingCSVDownloadHandler.streaming_csv_view(request, 
                                                              previous_search_params, 
                                                              'search-by-window-around-snpid')

    search_request_params = Paging.get_paging_info_for_request(request,
                                                form_data['page_of_results_shown'])

    api_search_query =  {'snpid'       : requested_snpid, 
                         'window_size' : window_size,
                         'pvalue_rank' :   pvalue_rank,
                         'from_result' : search_request_params['search_result_offset']}
    shared_context = APIResponseHandler.handle_search(api_search_query, 
                                                      'search-by-window-around-snpid',
                                                      search_request_params)
    #the next line of code 'turns the page'
    form_data = copy_valid_form_data_into_hidden_fields(form_data)
    form_data['page_of_results_shown'] = search_request_params['page_of_results_to_display']
    snpid_window_search_form = SearchBySnpidWindowForm(form_data)
    context = StandardFormset.setup_formset_context(
                                           snpid_window_form=snpid_window_search_form)
    context.update(shared_context)
    return render(request, 
                 'ss_viewer/multi-searchpage.html',
                  context)

