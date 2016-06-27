import requests
import json
from ss_viewer.forms import SearchByGeneNameForm 
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
    fields_to_copy = ['gene_name', 'window_size', 'pvalue_rank_cutoff']
    for form_field in fields_to_copy:
        form_data['prev_search_'+form_field] = form_data[form_field]
    return form_data


def handle_gene_name_search(request):
    if request.method != 'POST':
        return redirect(reverse('ss_viewer:multi-search'))

    gene_name_search_form = SearchByGeneNameForm(request.POST)

    if not gene_name_search_form.is_valid():
        context = StandardFormset.setup_formset_context(
                                     gene_name_form = gene_name_search_form)
        return StandardFormset.handle_invalid_form(request, context)

    form_data = gene_name_search_form.cleaned_data
    pvalue_rank = PValueFromForm.get_pvalue_rank_from_form(gene_name_search_form)

    if request.POST['action'] == 'Download Results':
        gene_name = form_data['prev_search_gene_name']
        pvalue_rank = form_data['prev_search_pvalue_rank_cutoff']
        window_size = form_data['prev_search_window_size']
        previous_search_params = { 'gene_name'   :  gene_name,
                                   'pvalue_rank' :  pvalue_rank,
                                   'window_size' :  window_size  }
        return StreamingCSVDownloadHandler.streaming_csv_view(request,
                                                              previous_search_params, 
                                                              'search-by-gene-name')
    search_request_params = Paging.get_paging_info_for_request(request,
                                                form_data['page_of_results_shown'])
    api_search_query  =  {'gene_name'   : form_data['gene_name'], 
                          'window_size' : form_data['window_size'],
                          'pvalue_rank' :  pvalue_rank, 
                          'from_result' : search_request_params['search_result_offset']}

    shared_context = APIResponseHandler.handle_search(api_search_query, 
                                                      'search-by-gene-name',
                                                      search_request_params)
    #the next line of code 'turns the page'
    form_data = copy_valid_form_data_into_hidden_fields(form_data)
    form_data['page_of_results_shown'] = search_request_params['page_of_results_to_display']
    gene_name_search_form = SearchByGeneNameForm(form_data)

    context = StandardFormset.setup_formset_context(
                                           gene_name_form=gene_name_search_form)
    context.update(shared_context)
    return render(request, 
                 'ss_viewer/multi-searchpage.html',
                  context)

