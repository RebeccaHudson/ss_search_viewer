from ss_viewer.views.generic_search import GenericSearchView
from ss_viewer.forms import SearchByGenomicLocationForm

class GenomicLocationSearchView(GenericSearchView):
    form_class = SearchByGenomicLocationForm 
    form_name_in_context = 'gl_search_form'
    api_action_name = 'search-by-gl'


    def setup_api_search_query(self, form_data):
        api_search_query =  { 'chromosome' : form_data['selected_chromosome'],
                              'start_pos'  : form_data['gl_start_pos'],
                              'end_pos'    : form_data['gl_end_pos']          }
        return api_search_query

