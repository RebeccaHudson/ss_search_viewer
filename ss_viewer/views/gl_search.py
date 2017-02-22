from ss_viewer.views.generic_search import GenericSearchView
from ss_viewer.forms import SearchByGenomicLocationForm

class GenomicLocationSearchView(GenericSearchView):
    form_class = SearchByGenomicLocationForm 
    form_name_in_context = 'gl_search_form'
    api_action_name = 'search-by-gl'


    def setup_api_search_query(self, form_data, request):
        api_search_query =  { 'chromosome' : form_data['selected_chromosome'],
                              'start_pos'  : form_data['gl_start_pos'],
                              'end_pos'    : form_data['gl_end_pos']          }
        api_search_query.update(self.get_pvalues_from_form())
        return api_search_query

    def handle_params_for_download(self, form_data):
        return \
        { 'chromosome' : form_data['selected_chromosome'],
          'start_pos'  : form_data['gl_start_pos'],
          'end_pos'    : form_data['gl_end_pos'],
          'pvalue_rank': form_data['pvalue_rank_cutoff'] }


