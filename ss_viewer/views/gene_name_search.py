from ss_viewer.forms import SearchByGeneNameForm 
from ss_viewer.views.generic_search import GenericSearchView

class GeneNameSearchView(GenericSearchView):
    form_class = SearchByGeneNameForm
    form_name_in_context = 'gene_name_form'
    api_action_name = 'search-by-gene-name'

    def setup_api_search_query(self, form_data):
        api_search_query  =  {'gene_name'   : form_data['gene_name'], 
                              'window_size' : form_data['window_size'] }
        return api_search_query
