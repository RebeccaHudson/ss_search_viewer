from ss_viewer.forms import SearchByTranscriptionFactorForm
from ss_viewer.views.generic_search import GenericSearchView
from ss_viewer.views.shared import MotifTransformer, TFTransformer

class TranscriptionFactorSearchView(GenericSearchView):
    form_class = SearchByTranscriptionFactorForm
    form_name_in_context = 'tf_search_form'
    api_action_name = 'search-by-tf'  #TODO: This should be called API action name
    previous_search_params = None

    #unused, remove later.
    def handle_search_by_trans_factor(self, request):
        #tf_search_form = None
        #if request.POST['action'] in ['Prev', 'Next']:
        #    oneDict = request.POST.dict()
        #    oneDict = self.copy_hidden_fields_into_form_data(oneDict) 
        #    #tf_search_form = SearchByTranscriptionFactorForm(oneDict)
        #    tf_search_form = self.form_class(oneDict)   #does parametrizing the form class work?
        #else: 
        #    #tf_search_form = SearchByTranscriptionFactorForm(request.POST)
        #    tf_search_form = self.form_class(request.POST)
        #if not tf_search_form.is_valid() and not request.POST['action'] == 'Download Results':
        #    context = \
        #         StandardFormset.dict_based_setup_formset_context({'tf_form':tf_search_form})
        #    return StandardFormset.handle_invalid_form(request, context)
        #form_data = tf_search_form.cleaned_data
        
        form_data = self.search_form.cleaned_data 
        tf_search_form = self.search_form
        print "form data for tf search " + str(form_data)
         

        # ENCODE motifs are prefixes, JASPAR are actually mapped with TFTransformer
        if form_data['tf_library'] == 'encode':
            return handle_search_by_encode_trans_factor(request, form_data, pvalue_rank)
            #this logic is inelegant because I need to finish it ASAP at this point.; 
            # consider tidying up. Otherwise, go with the previously-developed JASPAR 
            #library behavior (lookups for transcription factors)
        print "searching by jaspar.."

        #TODO: find a way to sidestep validation for Prev, Next, and Download. 
        #EG: would I just call 'data' or something?
        if request.POST['action'] == 'Download Results':
            return self.handle_download(self.search_form.cleaned_data, request)

        tft = TFTransformer()
        #offer a download of results currently shown, use the values copied into the 
        #hidden controls on the previous form POST.
        #if request.POST['action'] == 'Download Results':
        #    motif_value = tft.lookup_motifs_by_tf(form_data['prev_search_trans_factor'])
        #    pvalue_rank = form_data['prev_search_pvalue_rank_cutoff']
        #    previous_search_params = {'motif'  :  motif_value, 
        #                         'pvalue_rank' :  pvalue_rank,
        #                          'tf_library' : 'jaspar' }
        #    if form_data['prev_search_pvalue_ref_cutoff'] is not None:
        #        previous_search_params.update(
        #                     {'pvalue_ref'  : form_data['prev_search_pvalue_ref_cutoff']})
        #    if form_data['prev_search_pvalue_snp_cutoff'] is not None:
        #        previous_search_params.update(
        #                     {'pvalue_snp'  : form_data['prev_search_pvalue_snp_cutoff']})

        #    return StreamingCSVDownloadHandler.streaming_csv_view(request, 
        #                                                          previous_search_params, 
        #                                                          'search-by-tf')

        #if it's not the special paging actions, carry on as normal.
        motif_value = tft.lookup_motifs_by_tf(form_data['trans_factor'])

        search_request_params = Paging.get_paging_info_for_request(request,
                                                    form_data['page_of_results_shown'])
        #pvalue_rank = PValueFromForm.get_pvalue_rank_from_form(tf_search_form)
        pvalue_dict = PValueDictFromForm.get_pvalues_from_form(tf_search_form)
        api_search_query = {'motif'       :  motif_value, 
                            'pvalue_rank' :  pvalue_dict['pvalue_rank_cutoff'],
                            'from_result' :  search_request_params['search_result_offset']}
        #onnly include pvalue_ref and pvalue_snp if they are present in the input.
        if 'pvalue_ref_cutoff' in pvalue_dict:
            api_search_query.update({'pvalue_ref'  : pvalue_dict['pvalue_ref_cutoff']})
        if 'pvalue_snp_cutoff' in pvalue_dict:
            api_search_query.update({'pvalue_snp'  : pvalue_dict['pvalue_snp_cutoff']})

        shared_context = APIResponseHandler.handle_search(api_search_query, 
                                                          'search-by-tf',
                                                           search_request_params)

        form_data = self.copy_valid_form_data_into_hidden_fields(form_data) 
        #the next line of code 'turns the page'
        form_data['page_of_results_shown'] = search_request_params['page_of_results_to_display']

        #tf_search_form = SearchByTranscriptionFactorForm(form_data)
        tf_search_form = self.form_class(form_data)

        context = StandardFormset.setup_formset_context(tf_form=tf_search_form)
        context.update(shared_context)

        return render(request, 
                     'ss_viewer/multi-searchpage.html',
                      context)

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
        return \
          {'motif'      : motif_value,
           'pvalue_rank': form_data['prev_search_pvalue_rank_cutoff'],
           'tf_library' : form_data['prev_search_tf_library']         }

    # Note/remember for ENCODE, the transcription factor is ABC the motif value 
    #is ABC-omg-why-is-this-name-so-long
    def  handle_search_by_encode_trans_factor(self, request, form_data, pvalue_rank): 
        print "Searching by encode"
        if request.POST['action'] == 'Download Results':
            motif_prefix = form_data['prev_search_encode_trans_factor']
            pvalue_rank = form_data['prev_search_pvalue_rank_cutoff']
            previous_search_params = {'tf_library' :  'encode',
                                      'motif'      :  motif_prefix,
                                      'pvalue_rank':  pvalue_rank}
            return StreamingCSVDownloadHandler.streaming_csv_view(request, 
                                                                  previous_search_params, 
                                                                  'search-by-tf')

        motif_prefix = form_data['encode_trans_factor']
        #pvalue_rank = PValueFromForm.get_pvalue_rank_from_form(tf_search_form)
        search_request_params = Paging.get_paging_info_for_request(request,
                                                    form_data['page_of_results_shown'])
        api_search_query = {'tf_library'  :  'encode', 
                            'motif'       :  motif_prefix, 
                            'pvalue_rank' :  pvalue_rank,
                            'from_result' :  search_request_params['search_result_offset']}

        shared_context = APIResponseHandler.handle_search(api_search_query, 
                                                          'search-by-tf',
                                                          search_request_params)

        form_data = copy_valid_form_data_into_hidden_fields(form_data) 
        #the next line of code 'turns the page'
        form_data['page_of_results_shown'] = search_request_params['page_of_results_to_display']

        tf_search_form = SearchByTranscriptionFactorForm(form_data)
        context = StandardFormset.setup_formset_context(tf_form=tf_search_form)
        context.update(shared_context)

        return render(request, 
                     'ss_viewer/multi-searchpage.html',
                      context)
