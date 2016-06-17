import requests
import json
from ss_viewer.forms import SearchByGenomicLocationForm
from django.core.urlresolvers import reverse
from django.shortcuts import render
from ss_viewer.views.shared import Paging
from ss_viewer.views.shared import MotifTransformer
from ss_viewer.views.shared import APIUrls 
from ss_viewer.views.shared import StandardFormset 



def handle_search_by_genomic_location(request):
    if request.method == 'GET':
        return redirect(reverse('ss_viewer:multi-search'))

    if request.method == 'POST':
        searchpage_template = 'ss_viewer/multi-searchpage.html'
        gl_search_form = SearchByGenomicLocationForm(request.POST)

        search_paging_info = None
        status_message = ""
        response_data = None

        if not gl_search_form.is_valid():
             context = setup_formset_context(gl_form=gl_search_form)
             context.update({'status_message' :  "Invalid search. Try agian."})
             return(request, searchpage_template, context)
        form_data = gl_search_form.cleaned_data
        search_request_params = Paging.get_paging_info_for_request(request,
                                                             form_data['page_of_results_shown'])
        api_search_query = { 'chromosome' : form_data['selected_chromosome'],
                             'start_pos'  : form_data['gl_start_pos'],
                             'end_pos'    : form_data['gl_end_pos'],
                             'pvalue_rank': form_data['pvalue_rank_cutoff'],
                             'from_result': search_request_params['search_result_offset'] }
        api_response = requests.post( APIUrls.setup_api_url('search-by-gl'),
               json=api_search_query, headers={ 'content-type' : 'application/json' })

        # DRY up the following part here, if it appears to be possible.
        response_json = None
        if api_response.status_code == 204:
            status_message = "No matching rows"
        elif api_response.status_code == 400:
            status_message  = "API reported an error: " + api_response.text
        else:
            response_json = json.loads(api_response.text)
            #print "whatever this is: " + str(response_json['data'])
            tft = MotifTransformer()
            response_data = tft.transform_motifs_to_transcription_factors(response_json['data'])
            status_message = 'Got ' + str(response_json['hitcount']) + ' rows back from API.'
            status_message+= ' page shown '+str(search_request_params['page_of_results_to_display'])
            form_data['page_of_results_shown'] = search_request_params['page_of_results_to_display']
            search_paging_info = Paging.get_paging_info_for_display(response_json['hitcount'],
                                             search_request_params['page_of_results_to_display'])
        new_form = SearchByGenomicLocationForm(form_data)
        context = StandardFormset.setup_formset_context(gl_form = new_form)
        context.update({'api_response' : response_data,
                        'holdover_gl_region': api_search_query,
                        'search_paging_info': search_paging_info })
        return render(request, searchpage_template, context)


