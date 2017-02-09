from ss_viewer.forms import SearchByTranscriptionFactorForm
from ss_viewer.views.generic_search import GenericSearchView
from ss_viewer.views.shared import MotifTransformer, TFTransformer

class TranscriptionFactorSearchView(GenericSearchView):
    form_class = SearchByTranscriptionFactorForm
    form_name_in_context = 'tf_search_form'
    api_action_name = 'search-by-tf'
    previous_search_params = None

    #do transcription-factor specific stuff here. 
    def setup_api_search_query(self, form_data, request):
        tft = TFTransformer()
        motif_value = None
        if form_data['tf_library'] == 'encode':
            #The transcription factor IS the motif's prefix; search by that.
            motif_value = form_data['encode_trans_factor'] 
        else:
            #Use JASPAR motifs.
            trans_factor = form_data['trans_factor']
            motif_value = tft.lookup_motifs_by_tf(form_data['trans_factor'])
            print "motif value for not download " + repr(motif_value)
        api_search_query = {'motif'      :  motif_value, 
                            'tf_library' :  form_data['tf_library'] }
        api_search_query.update(self.get_pvalues_from_form())
        return api_search_query


    #TODO: properly handle ENCODE data.
    def handle_params_for_download(self, form_data):
        motif_value = None
        if form_data['prev_search_tf_library'] == 'encode': 
            motif_value = form_data['prev_search_encode_trans_factor'] 
        else:   
            #JASPAR
            tft = TFTransformer()
            motif_value = tft.lookup_motifs_by_tf(
                                  form_data['prev_search_trans_factor']),
            print "motif value for download " + repr(motif_value)
            motif_value = motif_value[0]
        return \
          {'motif'      : motif_value,
           'pvalue_rank': form_data['prev_search_pvalue_rank_cutoff'],
           'tf_library' : form_data['prev_search_tf_library']         }
