from ss_viewer.views.generic_search import GenericSearchView
from ss_viewer.forms import SearchBySnpidWindowForm
from django.http import HttpResponse
import json

class SnpidWindowSearchView(GenericSearchView):
    form_class = SearchBySnpidWindowForm
    form_name_in_context = 'snpid_window_form'
    api_action_name = 'search-by-window-around-snpid'
  
    def setup_api_search_query(self, form_data):
        requested_snpid = form_data['snpid']
        api_search_query =  {'snpid'       : requested_snpid, 
                             'window_size' : form_data['window_size']}
        return api_search_query

