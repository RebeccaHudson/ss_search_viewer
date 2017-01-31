from ss_viewer.views.generic_search import GenericSearchView
from ss_viewer.forms import SearchBySnpidForm

class SnpidSearchView(GenericSearchView):
    form_class = SearchBySnpidForm 
    form_name_in_context = 'snpid_search_form'
    api_action_name = 'snpid-search'

    def setup_api_search_query(self, form_data, request):
        #raw_requested_snpids = ", ".join(form_data['snpid_list'])
        api_search_query = { 'snpid_list' : form_data['snpid_list']  }
        api_search_query.update(self.get_pvalues_from_form())
        return api_search_query

    def handle_params_for_download(self, form_data):
       snpid_list = [one_snpid.strip() for one_snpid in 
                    form_data['prev_search_raw_requested_snpids'].split(",")]
       return \
        {'pvalue_rank' : form_data['prev_search_pvalue_rank_cutoff'], 
         'snpid_list'  : snpid_list } 

