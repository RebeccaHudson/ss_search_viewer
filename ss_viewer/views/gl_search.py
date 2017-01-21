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
from ss_viewer.views.shared import PValueFromForm
from django.core.urlresolvers import reverse
from ss_viewer.views.shared import StreamingCSVDownloadHandler

def copy_valid_form_data_into_hidden_fields(valid_form_data):
    fields_to_copy = ['selected_chromosome', 'gl_start_pos', 'gl_end_pos', 'pvalue_rank_cutoff'] 
    for form_field in fields_to_copy:
        valid_form_data['prev_search_'+form_field] = valid_form_data[form_field]
    return valid_form_data

def copy_hidden_fields_into_form_data(valid_form_data):
    fields_to_copy = ['selected_chromosome', 'gl_start_pos', 'gl_end_pos', 'pvalue_rank_cutoff'] 
    for form_field in fields_to_copy:
        valid_form_data[form_field] = valid_form_data['prev_search_'+form_field] 
    return valid_form_data


#There's validation, then More validation.
#better to have one round of validation if possible.
def handle_search_by_genomic_location(request):
    if request.method != 'POST':
        return redirect(reverse('ss_viewer:multi-search'))
    gl_search_form = None
    if request.POST['action'] in ['Prev', 'Next']:
        oneDict = copy_hidden_fields_into_form_data(request.POST.dict())
        gl_search_form = SearchByGenomicLocationForm(oneDict)
    else: 
        gl_search_form = SearchByGenomicLocationForm(request.POST)
 
    if not gl_search_form.is_valid() and not request.POST['action'] == 'Download Results':
         context = StandardFormset.setup_formset_context(gl_form=gl_search_form)
         errs = gl_search_form.errors
         print "Form errors: " + repr(gl_search_form.errors.values())
         context['form_errors'] = \
           [ str(item) for one_error in errs.values() for item in one_error]
         return StandardFormset.handle_invalid_form(request, context)

    print "is form valid? " + str(gl_search_form.is_valid()) 
    print "about to get cleaned data"  
    form_data = gl_search_form.cleaned_data
    print "just got cleaned form data " + str(form_data) 


    #download is offered for results currently displayed.
    if request.POST['action'] == 'Download Results':
        previous_search_params = { 'chromosome' : form_data['prev_search_selected_chromosome'],
                                   'start_pos'  : form_data['prev_search_gl_start_pos'],
                                   'end_pos'    : form_data['prev_search_gl_end_pos'],
                                   'pvalue_rank': form_data['prev_search_pvalue_rank_cutoff'] }
        print "requested gl search download with these params : " + repr(previous_search_params)
        return StreamingCSVDownloadHandler.streaming_csv_view(request, 
                                                             previous_search_params, 
                                                             'search-by-gl')

    pvalue = PValueFromForm.get_pvalue_rank_from_form(gl_search_form)
    if not ['pvalue_rank_cutoff'] in form_data.keys():
       form_data['pvalue_rank_cutoff'] = pvalue

    search_request_params = Paging.get_paging_info_for_request(request,
                                                         form_data['page_of_results_shown'])

    api_search_query =  { 'chromosome' : form_data['selected_chromosome'],
                          'start_pos'  : form_data['gl_start_pos'],
                          'end_pos'    : form_data['gl_end_pos'],
                          'pvalue_rank': pvalue,
                          'from_result': search_request_params['search_result_offset'] }
    shared_context = APIResponseHandler.handle_search(api_search_query, 
                                                      'search-by-gl',
                                                      search_request_params)
    form_data = copy_valid_form_data_into_hidden_fields(form_data)
    #this 'turns the page'
    form_data['page_of_results_shown'] = search_request_params['page_of_results_to_display']

    new_gl_form = SearchByGenomicLocationForm(form_data)
    context = StandardFormset.setup_formset_context(gl_form = new_gl_form)
    context.update(shared_context)
    return render(request, 
                  'ss_viewer/multi-searchpage.html',
                   context)

