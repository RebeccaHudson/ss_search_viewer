from ss_viewer.views.generic_search import GenericSearchView
from ss_viewer.forms import SearchBySnpidForm

class SnpidSearchView(GenericSearchView):
    form_class = SearchBySnpidForm 
    form_name_in_context = 'snpid_search_form'
    api_action_name = 'snpid-search'

    def setup_api_search_query(self, form_data, request):
        api_search_query = { 'snpid_list' : form_data['snpid_list']  }
        #should be able to delete the file from the form data at this point.
        if 'file_of_snpids' in form_data.keys() and \
            form_data['file_of_snpids'] is not None:
            del form_data['file_of_snpids']
        return api_search_query
