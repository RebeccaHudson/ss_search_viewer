from ss_viewer.views.generic_search import GenericSearchView
from ss_viewer.forms import SearchBySnpidWindowForm
from django.http import HttpResponse
import json

class SnpidWindowSearchView(GenericSearchView):
    form_class = SearchBySnpidWindowForm
    form_name_in_context = 'snpid_window_form'
    api_action_name = 'search-by-window-around-snpid'
  
    def setup_api_search_query(self, form_data, request):
        requested_snpid = form_data['snpid']

        api_search_query =  {'snpid'       : requested_snpid, 
                             'window_size' : form_data['window_size']}
        api_search_query.update(self.get_pvalues_from_form())
        return api_search_query

    #does this get used anymore?
    def handle_params_for_download(self, form_data):
        #don't do for ajaxy
        return \
         { 'snpid'       : form_data['snpid'], 
           'window_size' : form_data['window_size'], 
           'pvalue_rank' : form_data['pvalue_rank_cutoff']  }
 

