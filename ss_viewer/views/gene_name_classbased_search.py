from ss_viewer.forms import SearchByGeneNameForm 
from ss_viewer.views.generic_search import GenericSearchView

class GeneNameSearchView(GenericSearchView):
    form_class = SearchByGeneNameForm
    form_name_in_context = 'gene_name_form'
    api_action_name = 'search-by-gene-name'

    def setup_api_search_query(self, form_data, request):
        api_search_query  =  {'gene_name'   : form_data['gene_name'], 
                              'window_size' : form_data['window_size'] }
        api_search_query.update(self.get_pvalues_from_form())
        return api_search_query
     
    def handle_params_for_download(self, form_data):
        return \
        { 'gene_name'   :  form_data['prev_search_gene_name'],
          'pvalue_rank' :  form_data['prev_search_pvalue_rank_cutoff'],
          'window_size' :  form_data['prev_search_window_size']  }
