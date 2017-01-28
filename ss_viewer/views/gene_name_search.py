import requests
import json
from ss_viewer.forms import SearchByGeneNameForm 
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
    fields_to_copy = ['gene_name', 'window_size', 'pvalue_rank_cutoff',\
                     'pvalue_ref_cutoff', 'pvalue_snp_cutoff'  ]
    for form_field in fields_to_copy:
        if form_field in form_data:
            form_data['prev_search_'+form_field] = form_data[form_field]
    return form_data

def copy_hidden_fields_into_form_data(form_data):
    fields_to_copy = ['gene_name', 'window_size', 'pvalue_rank_cutoff',\
                      'pvalue_ref_cutoff', 'pvalue_snp_cutoff' ]
    for form_field in fields_to_copy:
        if 'prev_search_' + form_field in form_data:       
            form_data[form_field] = form_data['prev_search_'+form_field] 
    return form_data

def handle_gene_name_search(request):
    if request.method != 'POST':
        return redirect(reverse('ss_viewer:multi-search'))
    gene_name_search_form = None
    if request.POST['action'] in ['Prev', 'Next']:
        oneDict = copy_hidden_fields_into_form_data(request.POST.dict())
        gene_name_search_form = SearchByGeneNameForm(oneDict)
    else:
        gene_name_search_form = SearchByGeneNameForm(request.POST)

    if not gene_name_search_form.is_valid():
        context = StandardFormset.setup_formset_context(
                                     gene_name_form = gene_name_search_form)
        errs  = gene_name_search_form.errors
        context['form_errors'] = \
           [ str(item) for one_error in errs.values() for item in one_error]
        return StandardFormset.handle_invalid_form(request, context)

    form_data = gene_name_search_form.cleaned_data


    if request.POST['action'] == 'Download Results':
        gene_name = form_data['prev_search_gene_name']
        pvalue_rank = form_data['prev_search_pvalue_rank_cutoff']
        window_size = form_data['prev_search_window_size']
        previous_search_params = { 'gene_name'   :  gene_name,
                                   'pvalue_rank' :  pvalue_rank,
                                   'window_size' :  window_size  }
        if form_data['prev_search_pvalue_ref_cutoff'] is not None:
            previous_search_params.update(
                         {'pvalue_ref'  : form_data['prev_search_pvalue_ref_cutoff']})
        if form_data['prev_search_pvalue_snp_cutoff'] is not None:
            previous_search_params.update(
                         {'pvalue_snp'  : form_data['prev_search_pvalue_snp_cutoff']})
        return StreamingCSVDownloadHandler.streaming_csv_view(request,
                                                              previous_search_params, 
                                                              'search-by-gene-name')
    search_request_params = Paging.get_paging_info_for_request(request,
                                                form_data['page_of_results_shown'])

    pvalue_dict = PValueDictFromForm.get_pvalues_from_form(gene_name_search_form)
    api_search_query  =  {'gene_name'   : form_data['gene_name'], 
                          'window_size' : form_data['window_size'],
                          'pvalue_rank' : pvalue_dict['pvalue_rank_cutoff'],
                          'from_result' : search_request_params['search_result_offset']}
    #Only include pvalue_ref and pvalue_snp if they are present in the input.
    if 'pvalue_ref_cutoff' in pvalue_dict:
        api_search_query.update({'pvalue_ref'  : pvalue_dict['pvalue_ref_cutoff']})
    if 'pvalue_snp_cutoff' in pvalue_dict:
        api_search_query.update({'pvalue_snp'  : pvalue_dict['pvalue_snp_cutoff']})

    #is the gene not showing up in the database reported correctly?
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

