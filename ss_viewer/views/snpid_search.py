import re
import requests
import json

from django.core.urlresolvers import reverse
from django.shortcuts import render
from ss_viewer.views.shared import MotifTransformer
from ss_viewer.views.shared import TFTransformer
from ss_viewer.views.shared import APIUrls 
from ss_viewer.views.shared import PValueFromForm 
from ss_viewer.views.shared import StandardFormset
from ss_viewer.views.shared import Paging 
from django.core.exceptions import ValidationError
from ss_viewer.forms import SearchBySnpidForm

class SnpidSearchUtils:
    @staticmethod
    def extract_snpids_from_textfield(text):
        gex = re.compile('(rs[0-9]+)', re.MULTILINE)  
        list_of_snpids = gex.findall(text)
        return list_of_snpids
    
    @staticmethod
    def clean_and_validate_snpid_text_input(text_input):
        snpids = SnpidSearchUtils.extract_snpids_from_textfield(text_input)
        deduped_snpids = list(set(snpids))  #don't allow any duplicate requests.
        if len(deduped_snpids) == 0:  
          raise forms.ValidationError("No snpids have been included")  
        return deduped_snpids

    @staticmethod
    def get_snpid_list_from_form(request, form):
      form_snpids = form.cleaned_data.get('raw_requested_snpids')
      #remove the data in there.
      if form_snpids:
        return SnpidSearchUtils.clean_and_validate_snpid_text_input(form_snpids)
      else:
        file_pointer = request.FILES.get('file_of_snpids')
        text_in_file = file_pointer.read()   # TODO: read in chunks rather than all at once. 
        return SnpidSearchUtils.clean_and_validate_snpid_text_input(text_in_file)



def setup_context_for_snpid_search_results(api_response, snpid_list, holdover_p_value, 
                                           page_of_results_to_display):
    status_message = ""; response_json = None
    response_data = None
    if api_response.status_code == 204:
        status_message = "No matches for requested snpids" 
    else:
        count_of_requested_snpids = len(snpid_list)
        response_json = json.loads(api_response.text)
        tft = MotifTransformer()
        response_data = tft.transform_motifs_to_transcription_factors(response_json['data'])
        status_message = 'Got ' + str(response_json['hitcount']) + ' hits.'
        status_message += " Showing page " + str(page_of_results_to_display) + " of results."    
    snpid_form = SearchBySnpidForm({'raw_requested_snpids':", ".join(snpid_list),
                                    'pvalue_rank_cutoff' : holdover_p_value, 
                                    'page_of_results_shown': page_of_results_to_display }  )
    search_paging_info = Paging.get_paging_info_for_display(response_json['hitcount'], 
                                                      page_of_results_to_display) 

    context = StandardFormset.setup_formset_context(snpid_form=snpid_form)
    context.update({'api_response' :  response_data, 'status_message' : status_message,
                    'holdover_snpids' : ', '.join(snpid_list), 
                    'search_paging_info' : search_paging_info })  
    return context




def handle_search_by_snpid(request):
  if request.method == 'GET':
      return redirect(reverse('ss_viewer:multi-search'))

  if request.method == 'POST':
    searchpage_template = 'ss_viewer/multi-searchpage.html'
    snpid_search_form = SearchBySnpidForm(request.POST, request.FILES)
    status_message = ""
    if not snpid_search_form.is_valid():
       context = StandardFormset.setup_formset_context(snpid_form=snpid_search_form)
       context.update({'status_message':'Invalid search. Try agian.'})
       return render(request, searchpage_template, context)
    #if execution reaches this point, the form is valid.
    snpid_list = None
    try:
        snpid_list = SnpidSearchUtils.get_snpid_list_from_form(request, snpid_search_form)

    except ValidationError:
        context = StandardFormset.setup_formset_context()
        context.update({'status_message' : "No properly formatted SNPids in the text.",
                        'active_tab'     : 'snpid' })
        return render(request, searchpage_template, context)

    form_data = snpid_search_form.cleaned_data
    search_request_params = Paging.get_paging_info_for_request(request,
                                                form_data['page_of_results_shown'])

    pvalue_rank = PValueFromForm.get_pvalue_rank_from_form(snpid_search_form)
    request_data = { 'snpid_list' : snpid_list,
                     'pvalue_rank' : pvalue_rank,
                     'from_result' : search_request_params['search_result_offset'] }

    api_response = requests.post( APIUrls.setup_api_url('snpid-search'),
                                  json=request_data,
                                  headers={ 'content-type' : 'application/json' })

    context = setup_context_for_snpid_search_results(api_response, snpid_list,
                       pvalue_rank ,search_request_params['page_of_results_to_display'])
    return render(request, searchpage_template, context )
