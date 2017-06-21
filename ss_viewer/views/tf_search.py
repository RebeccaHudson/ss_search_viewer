from ss_viewer.forms import SearchByTranscriptionFactorForm
from ss_viewer.views.generic_search import GenericSearchView
from ss_viewer.views.shared import MotifTransformer, TFTransformer

class TranscriptionFactorSearchView(GenericSearchView):
    form_class = SearchByTranscriptionFactorForm
    form_name_in_context = 'tf_search_form'
    api_action_name = 'search-by-tf'
    previous_search_params = None

    #do transcription-factor specific stuff here. 
    def setup_api_search_query(self, form_data):
        tft = None; tf_for_search = None
        if form_data['tf_library'] == 'encode':
            tft = TFTransformer('encode')
            #The transcription factor IS the motif's prefix; search by that.
            tf_for_search = form_data['encode_trans_factor']
        else:
            #Use JASPAR motifs.
            trans_factor = form_data['trans_factor']
            tft = TFTransformer('jaspar')
            tf_for_search =  form_data['trans_factor'] 

        motif_value = tft.lookup_motifs_by_tf(tf_for_search)
        print "motif value for not download " + repr(motif_value)
        #Downloads already have the query saved on the page?
        api_search_query = {'motif'      :  motif_value, 
                            'tf_library' :  form_data['tf_library'] }
        return api_search_query

