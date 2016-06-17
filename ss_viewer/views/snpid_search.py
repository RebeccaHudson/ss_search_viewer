import re
import requests
import json

from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.shortcuts import redirect

from ss_viewer.views.shared import MotifTransformer
from ss_viewer.views.shared import TFTransformer
from ss_viewer.views.shared import APIUrls 
from ss_viewer.views.shared import PValueFromForm 
from ss_viewer.views.shared import StandardFormset
from ss_viewer.views.shared import Paging 
from ss_viewer.views.shared import APIResponseHandler
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
      print "get_snpid_list_from_form is running"
      form_snpids = form.cleaned_data.get('raw_requested_snpids')
      #remove the data in there.
      print "just grabbed cleaned data from the form " + str(form_snpids)
      if form_snpids:
        print "get snpid list is about to return SNPids from form"
        return SnpidSearchUtils.clean_and_validate_snpid_text_input(form_snpids)
      else:
        print "get snpid list is about to return SNPids from file"
        file_pointer = request.FILES.get('file_of_snpids')
        text_in_file = file_pointer.read()   # TODO: read in chunks rather than all at once. 
        return SnpidSearchUtils.clean_and_validate_snpid_text_input(text_in_file)



def setup_context_for_snpid_search_results(snpid_list, holdover_p_value, 
                                           page_of_results_to_display, shared_context):
    snpid_form = SearchBySnpidForm({'raw_requested_snpids':", ".join(snpid_list),
                                    'pvalue_rank_cutoff' : holdover_p_value, 
                                    'page_of_results_shown': page_of_results_to_display }  )
    context = StandardFormset.setup_formset_context(snpid_form=snpid_form)
    context.update(shared_context)
    return context




def handle_search_by_snpid(request):
    if request.method != 'POST':
        return redirect(reverse('ss_viewer:multi-search'))

    searchpage_template = 'ss_viewer/multi-searchpage.html'
    snpid_search_form = SearchBySnpidForm(request.POST, request.FILES)

    if not snpid_search_form.is_valid():
         context = StandardFormset.setup_formset_context(snpid_form=snpid_search_form)
         return StandardFormset.handle_invalid_form(request, context)

    snpid_list = None
    form_data = snpid_search_form.cleaned_data


    try:
         snpid_list = SnpidSearchUtils.get_snpid_list_from_form(request, snpid_search_form)
    except ValidationError:
         #TODO: form_data should be called "cleaned data", then blank out the snpids and pass the 
         #rest of the form back
         context = StandardFormset.setup_formset_context() #pass in old form here?
         #consider adding an optional message to the handle_invalid_form method
         context.update({'status_message' : "No properly formatted SNPids in the text.",
                         'active_tab'     : 'snpid' })
         return render(request, searchpage_template, context)

    #turn the page
    search_request_params = Paging.get_paging_info_for_request(request,
                                                form_data['page_of_results_shown'])
    pvalue_rank = PValueFromForm.get_pvalue_rank_from_form(snpid_search_form)
    api_search_query = { 'snpid_list' : snpid_list,
                         'pvalue_rank' : pvalue_rank,
                         'from_result' : search_request_params['search_result_offset'] }

    shared_context = APIResponseHandler.handle_search(api_search_query, 
                                                      'snpid-search', 
                                                      search_request_params)
    #we should be able to just pass in the form data
    context = setup_context_for_snpid_search_results(snpid_list,
                       pvalue_rank ,search_request_params['page_of_results_to_display'], shared_context)
    return render(request, searchpage_template, context )






