import requests
import json
import re
from ss_viewer.forms import SearchBySnpidWindowForm
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
    fields_to_copy = [ 'snpid', 'window_size',\
                       'pvalue_rank_cutoff','pvalue_ref_cutoff','pvalue_snp_cutoff']
    for form_field in fields_to_copy:
        if form_field in form_data:
            form_data['prev_search_' + form_field] = form_data[form_field]
    return form_data

def copy_hidden_fields_into_form_data(form_data):
    fields_to_copy = [ 'snpid', 'window_size',\
                       'pvalue_rank_cutoff','pvalue_ref_cutoff','pvalue_snp_cutoff']
    for form_field in fields_to_copy:
        if 'prev_search_' + form_field in form_data:
            form_data[form_field] = form_data['prev_search_' + form_field]
    return form_data

def extract_snpid_from_textfield(text):
    gex = re.compile('(rs[0-9]+)')
    snpid = gex.search(text)
    if snpid is not None:
       return snpid.group(1)
    else:
       return None

def handle_snpid_window_search(request):
    if request.method != 'POST':
        return redirect(reverse('ss_viewer:multi-search'))
    snpid_window_search_form = None
    if request.POST['action'] in ['Prev', 'Next']:
        oneDict = copy_hidden_fields_into_form_data(request.POST.dict()) 
        snpid_window_search_form = SearchBySnpidWindowForm(oneDict)   
    else:
        snpid_window_search_form = SearchBySnpidWindowForm(request.POST)

    if not snpid_window_search_form.is_valid():
        errs = snpid_window_search_form.errors
        context = StandardFormset.setup_formset_context(
                                     snpid_window_form=snpid_window_search_form)
        context['form_errors'] =\
           [ str(item) for one_error in errs.values() for item in one_error ]
        return StandardFormset.handle_invalid_form(request, context)

    form_data = snpid_window_search_form.cleaned_data

    requested_snpid = extract_snpid_from_textfield(form_data['snpid'])
    if requested_snpid is None:
        context = StandardFormset.setup_formset_context(
                                     snpid_window_form=snpid_window_search_form)
        context.update({'form_errors': ["SNPid not properly formatted."]})
        return StandardFormset.handle_invalid_form(request,
                                              context, 
                                              status_message="Invalid search"\
                                                     + "; see error(s) below:") 

    if request.POST['action'] == 'Download Results':
        pvalue_rank = form_data['prev_search_pvalue_rank_cutoff']
        window_size = form_data['prev_search_window_size']
        snpid = form_data['prev_search_snpid']
        previous_search_params = { 'snpid'       : snpid, 
                                   'window_size' : window_size, 
                                   'pvalue_rank' : pvalue_rank  } 
        if form_data['prev_search_pvalue_ref_cutoff'] is not None:
            previous_search_params.update(
                         {'pvalue_ref'  : form_data['prev_search_pvalue_ref_cutoff']})
        if form_data['prev_search_pvalue_snp_cutoff'] is not None:
            previous_search_params.update(
                         {'pvalue_snp'  : form_data['prev_search_pvalue_snp_cutoff']})
        return StreamingCSVDownloadHandler.streaming_csv_view(request, 
                                                              previous_search_params, 
                                                              'search-by-window-around-snpid')

    window_size = form_data['window_size']
    #pvalue_rank = PValueFromForm.get_pvalue_rank_from_form(snpid_window_search_form)
    pvalue_dict = PValueDictFromForm.get_pvalues_from_form(snpid_window_search_form)
    search_request_params = Paging.get_paging_info_for_request(request,
                                                form_data['page_of_results_shown'])

    api_search_query =  {'snpid'       : requested_snpid, 
                         'window_size' : window_size,
                         'pvalue_rank' : pvalue_dict['pvalue_rank_cutoff'],
                         'from_result' : search_request_params['search_result_offset']}
    #Only include pvalue_ref and pvalue_snp if they are present in the input.
    if 'pvalue_ref_cutoff' in pvalue_dict:
        api_search_query.update({'pvalue_ref'  : pvalue_dict['pvalue_ref_cutoff']})
    if 'pvalue_snp_cutoff' in pvalue_dict:
        api_search_query.update({'pvalue_snp'  : pvalue_dict['pvalue_snp_cutoff']})


    shared_context = APIResponseHandler.handle_search(api_search_query, 
                                                      'search-by-window-around-snpid',
                                                      search_request_params)
    #the next line of code 'turns the page'
    form_data['snpid'] = requested_snpid
    form_data = copy_valid_form_data_into_hidden_fields(form_data)
    form_data['page_of_results_shown'] = search_request_params['page_of_results_to_display']
    snpid_window_search_form = SearchBySnpidWindowForm(form_data)
    context = StandardFormset.setup_formset_context(
                                           snpid_window_form=snpid_window_search_form)
    context.update(shared_context)
    return render(request, 
                 'ss_viewer/multi-searchpage.html',
                  context)

