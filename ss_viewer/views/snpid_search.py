from ss_viewer.views.generic_search import GenericSearchView
from ss_viewer.forms import SearchBySnpidForm

class SnpidSearchView(GenericSearchView):
    form_class = SearchBySnpidForm 
    form_name_in_context = 'snpid_search_form'
    api_action_name = 'snpid-search'

    def setup_api_search_query(self, form_data, request):
        api_search_query = { 'snpid_list' : form_data['snpid_list']  }
        return api_search_query
