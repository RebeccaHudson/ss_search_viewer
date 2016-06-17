from django.conf import settings
from django.shortcuts import render

import os
import json
import pickle
import requests

from ss_viewer.forms import SearchBySnpidForm  #replaces ScoresSearchForm
from ss_viewer.forms import SearchByGenomicLocationForm
from ss_viewer.forms import SearchByTranscriptionFactorForm

class MotifTransformer:
    def __init__(self):
        fpath = os.path.dirname(os.path.dirname(__file__)) + "/lookup-tables" +\
        '/lut_tfs_by_jaspar_motif.pkl'
        lut = None
        with open(fpath , 'r') as f:
            lut = pickle.load(f)
        self.lut = lut
     
    def transform_one_motif_to_trans_factor(self, motif_value):
        trans_factor = self.lut.get(motif_value)
        #TODO load the correct motif file and replace this.
        if trans_factor is None:
             trans_factor  = "Not found."
        return trans_factor

    def transform_motifs_to_transcription_factors(self, response_json):
        transformed_response = []
        for one_row in response_json:
            motif_value = one_row['motif']
            one_row['trans_factor'] = self.transform_one_motif_to_trans_factor(motif_value)
            transformed_response.append(one_row)
        return transformed_response

#maybe put this with searches by transcription factor.
class TFTransformer:
    def __init__(self):
        lut = None
        #TODO: the following pickle must be processed in such a way that a 
        # lookup on a TF with multiple motif values returns a list.
        fpath = os.path.dirname(os.path.dirname(__file__)) + "/lookup-tables" +\
          '/lut_jaspar_motifs_by_tf.pkl'
        with open(fpath , 'r') as f:  
            lut = pickle.load(f) 
        self.lut = lut

    def lookup_motifs_by_tf(self, trans_factor):
        one_or_more_motif_values = self.lut[trans_factor]
        if not type(one_or_more_motif_values) == list:
          one_or_more_motif_values = [one_or_more_motif_values]
        return one_or_more_motif_values





class PValueFromForm:
    @staticmethod
    def get_pvalue_rank_from_form(form):
      if form.cleaned_data.has_key('pvalue_rank_cutoff'):
        return form.cleaned_data.get('pvalue_rank_cutoff')
      else:
        return 0.05

#includes all of the forms that should be loaded every time.
class StandardFormset:
     @staticmethod
     def setup_formset_context(tf_form=None, gl_form=None, snpid_form=None):
          active_tab = None
          hidden_page_number = {'page_of_results_shown':0}
          if tf_form is None:
              tf_form = SearchByTranscriptionFactorForm(initial=hidden_page_number)
          else:
              active_tab = 'tf'
          if gl_form is None:
              gl_form = SearchByGenomicLocationForm(initial=hidden_page_number)
          else:
              active_tab = 'gl-region'
          if snpid_form is None:
              snpid_form = SearchBySnpidForm(initial=hidden_page_number)
          else:
              active_tab = 'snpid'
          context =  { 'tf_search_form' : tf_form,
                      'gl_search_form': gl_form,
                      'snpid_search_form' : snpid_form }
          if active_tab is not None:
              context.update({'active_tab': active_tab })
          return context 

     @staticmethod
     def show_multisearch_page(request):
            searchpage_template = 'ss_viewer/multi-searchpage.html'
            #plotting_data = get_a_plot_by_snpid_and_motif('rs111200574', 'fake.motif')
            # needs a DLL plotting_data = get_a_plot_by_snpid_and_motif('rs111200574', 'fake.motif')
            context = StandardFormset.setup_formset_context()
            context.update({'status_message' : "Enter a search.",
                            'active_tab'     : 'none-yet'})
            return render(request, searchpage_template, context)

     @staticmethod
     def handle_invalid_form(request, context, status_message=None):
        if status_message == None:
            status_message =  "Invalid search. Try agian."
        context.update({'status_message' :  status_message })
        return render(request, 'ss_viewer/multi-searchpage.html', context) 


class Paging:
    @staticmethod
    def get_paging_info_for_request(request, page_of_search_results):
        page_of_results_to_display = 1

        if request.POST['action'] == 'Next':
             page_of_results_to_display = page_of_search_results + 1
        elif request.POST['action'] == 'Prev':
             page_of_results_to_display = page_of_search_results - 1

        search_result_offset = (page_of_results_to_display - 1) * \
                              settings.API_HOST_INFO['result_page_size']
        return { 'search_result_offset' : search_result_offset,
                 'page_of_results_to_display' : page_of_results_to_display }

    @staticmethod
    def get_paging_info_for_display(hitcount, page_of_results_to_display):
        search_paging_info = {'show_next_btn': False, 'show_prev_btn': False}
        hits_paged = (page_of_results_to_display ) * \
                     settings.API_HOST_INFO['result_page_size']
        if hitcount > hits_paged:
            search_paging_info['show_next_btn'] = True
        if page_of_results_to_display > 1:
             search_paging_info['show_prev_btn'] = True
        return search_paging_info



class APIResponseHandler:
    @staticmethod  
    def setup_hits_message(hitcount, page_of_results_to_display):
        return 'Got ' + str(hitcount) + ' rows back from API.' +\
               ' Showing page: ' + str(page_of_results_to_display)
   
    @staticmethod
    #api_action should be 'search-by-tf' or 'search-by-gl'
    #This code gets repeated between every search.
    def handle_search(api_search_query, api_action, search_request_params):
        api_response = requests.post( APIUrls.setup_api_url(api_action),
                 json=api_search_query, headers={'content-type':'application/json'})

        response_json = None
        status_message = None
        search_paging_info = None
        if api_response.status_code == 204:
            status_message = 'No matching rows.'
        else:
            response_json = json.loads(api_response.text)
            mt = MotifTransformer()
            response_data = mt.transform_motifs_to_transcription_factors(response_json['data'])

            status_message = APIResponseHandler.setup_hits_message(response_json['hitcount'], 
                                       search_request_params['page_of_results_to_display'])

            search_paging_info = Paging.get_paging_info_for_display(response_json['hitcount'],
                                        search_request_params['page_of_results_to_display'])
        return  {'status_message' : status_message, 
                 'search_paging_info' : search_paging_info,
                 'api_response'       : response_data }
     


class APIUrls:
    @staticmethod
    def setup_api_url(api_function):
        hostinfo = settings.API_HOST_INFO
        host_w_port = ':'.join([ hostinfo['host_url'], hostinfo['host_port'] ] )
        url_arglist =  [ hostinfo['api_root'], api_function]
        url_args = '/'.join(url_arglist)
        url = host_w_port + "/" + url_args  + "/"
        return url
 
