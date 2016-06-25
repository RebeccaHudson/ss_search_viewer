from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
import os
import json
import pickle
import requests
import csv
import zipfile
from tempfile import NamedTemporaryFile
from ss_viewer.forms import SearchBySnpidForm  #replaces ScoresSearchForm
from ss_viewer.forms import SearchByGenomicLocationForm
from ss_viewer.forms import SearchByTranscriptionFactorForm
from ss_viewer.forms import SearchBySnpidWindowForm
from ss_viewer.forms import SearchByGeneNameForm
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils.six.moves import range
from django.http import StreamingHttpResponse

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
     def setup_formset_context(tf_form=None, 
                               gl_form=None,
                               snpid_form=None,
                               snpid_window_form=None,
                               gene_name_form=None):
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

          if snpid_window_form is None:
              snpid_window_form = SearchBySnpidWindowForm(initial=hidden_page_number)
          else:
              active_tab = 'snpid-window'

          if gene_name_form is None:
              gene_name_form = SearchByGeneNameForm(initial=hidden_page_number)
          else: 
              active_tab = 'gene-name'

          context =  { 'tf_search_form' : tf_form,
                      'gl_search_form': gl_form,
                      'snpid_search_form' : snpid_form, 
                      'snpid_window_form' : snpid_window_form,
                      'gene_name_form'    : gene_name_form }
          if active_tab is not None:
              context.update({'active_tab': active_tab })
          return context 

     @staticmethod
     def show_multisearch_page(request):
          searchpage_template = 'ss_viewer/multi-searchpage.html'
          #plotting_data = get_a_plot_by_snpid_and_motif('rs111200574', 'fake.motif')
          #needs a DLL plotting_data=get_a_plot_by_snpid_and_motif('rs111200574', 'fake.motif')
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
    order_of_fields = ['chromosome', 'pos',   'snpid',   'transcription factor', 
                       'motif',   'motif length',  'pval rank',   'snp start',
                       'snp end',   'ref start',   'ref end',   'log lik ref',
                       'log lik ratio',   'log enhance odds',  'log reduce odds',
                       'log lik snp',   'snp strand',  'ref strand',  'pval ref',
                       'pval snp',  'pval cond ref'   'pval cond snp'   'pval diff',
                       'ref allele',  'snp allele']
    @staticmethod  
    def setup_hits_message(hitcount, page_of_results_to_display):
        return 'Got ' + str(hitcount) + ' rows back from API.' +\
               ' Showing page: ' + str(page_of_results_to_display)
     
    @staticmethod 
    #meant to handle one page of results at a time.
    #start with just the first result
    def get_plots_for_rows_with_plots(rows_to_display):
        plot_data = {} 
        field_names = ['motif', 'snpid', 'snpAllele'] 
        first_plot_id_str = None
        for one_row in rows_to_display:
            if one_row['has_plot'] is True:
                plot_id_str = "_".join([one_row[field_name] for field_name in field_names ])
                plot_data[plot_id_str] = reverse('ss_viewer:dynamic-svg', args=[plot_id_str])  
                print "grabbed a plot from right here: " + plot_id_str
                if first_plot_id_str is None:
                    first_plot_id_str = plot_id_str  #tell the interface which plot to show first.
        if not any(plot_data):
            return None
        return { 'plot_data':plot_data , 
                 'first_plot_id_str': first_plot_id_str}
 
    @staticmethod
    #api_action should be 'search-by-tf' or 'search-by-gl'
    #This code gets repeated between every search.
    def handle_search(api_search_query, api_action, search_request_params):
        api_response = requests.post( APIUrls.setup_api_url(api_action),
                 json=api_search_query, headers={'content-type':'application/json'})

        response_data = None
        status_message = None
        search_paging_info = None
        if api_response.status_code == 204:
            status_message = 'No matching rows.'
        elif api_response.status_code == 500:
            status_message = 'The API expeienced an error; no data returned.'
        elif api_response.status_code == 400:
            status_message = 'Bad request. API says: ' + api_response.text
        else:
            response_json = json.loads(api_response.text)
            mt = MotifTransformer()
            response_data = mt.transform_motifs_to_transcription_factors(response_json['data'])

            #slyly avoiding nested dictionaries. 
            plot_data = APIResponseHandler.get_plots_for_rows_with_plots(response_data)
            plot_source = plot_data['plot_data']          
            first_plot_id_str = plot_data['first_plot_id_str']
 
            status_message = APIResponseHandler.setup_hits_message(response_json['hitcount'], 
                                       search_request_params['page_of_results_to_display'])

            search_paging_info = Paging.get_paging_info_for_display(response_json['hitcount'],
                                        search_request_params['page_of_results_to_display'])
        return  {'status_message' : status_message, 
                 'search_paging_info' : search_paging_info,
                 'api_response'       : response_data,
                 'plot_source'          : plot_source,
                 'first_plot_id_str'  : first_plot_id_str }
    

    @staticmethod
    def write_one_response_to_csv(api_response_data, csv_writer):
        mt = MotifTransformer()
        prepared_data = mt.transform_motifs_to_transcription_factors(api_response_data)
        fields_for_csv = ['chr', 'pos', 'snpid', 'trans_factor', 'motif', 'motif_len',
                         'pval_rank', 'snp_start', 'snp_end', 'ref_start', 'ref_end',
                         'log_lik_ref', 'log_lik_ratio', 'log_enhance_odds',  
                         'log_reduce_odds', 'log_lik_snp', 'snp_strand', 'ref_strand',
                         'pval_ref', 'pval_snp', 'pval_cond_ref', 'pval_cond_snp',
                         'pval_diff', 'refAllele', 'snpAllele']
        for dr in api_response_data:
            row_to_write = [ dr[field_name] for field_name in fields_for_csv]
            csv_writer.writerow(row_to_write)

 
    @staticmethod
    def handle_download_request(api_search_query, api_action):
        response_data = None
        status_message = None
        response = HttpResponse(content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=search-results.csv.zip'
        api_response = requests.post( APIUrls.setup_api_url(api_action),
                 json=api_search_query, headers={'content-type':'application/json'})

        if api_response.status_code != 200:
            context = { "status_message" : "Download failed for some reason." } 
            return redirect(reverse('ss_viewer:multi-search'))

        response_json = json.loads(api_response.text)

        with NamedTemporaryFile() as output_tmp:
            writer = csv.writer(output_tmp)     
            writer.writerow(APIResponseHandler.order_of_fields) 
            APIResponseHandler.write_one_response_to_csv(response_json['data'], writer) 

            #loop until 204 or error.. 
            page_of_results = 1 
            while api_response.status_code == 200:
                search_offset = settings.API_HOST_INFO['result_page_size'] * page_of_results
                api_search_query.update({'from_result':search_offset})                
                #print "api search query : " + repr(api_search_query)
                api_response = requests.post( APIUrls.setup_api_url(api_action),
                     json=api_search_query, headers={'content-type':'application/json'})

                page_of_results += 1
                if api_response.status_code == 200:
                    response_json = json.loads(api_response.text)
                    APIResponseHandler.write_one_response_to_csv(response_json['data'], writer) 
           
            z = zipfile.ZipFile(response, 'w')
            output_tmp.seek(0)
            z.writestr("search-results.csv", output_tmp.read())
            z.close()
        #tempfile will be deleted when it closes.
        return response





"""An object that implements just the write method of the file-like
interface.
"""
class Echo(object):
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value

#lifted almost verbatim from django 1.9 docs
#https://docs.djangoproject.com/en/1.9/howto/outputting-csv/#streaming-large-csv-files
class StreamingCSVDownloadHandler:

    @staticmethod
    def fields_for_csv():
        return  ['chr', 'pos', 'snpid', 'trans_factor', 'motif', 'motif_len',
                 'pval_rank', 'snp_start', 'snp_end', 'ref_start', 'ref_end',
                 'log_lik_ref', 'log_lik_ratio', 'log_enhance_odds',
                 'log_reduce_odds', 'log_lik_snp', 'snp_strand', 'ref_strand',
                 'pval_ref', 'pval_snp', 'pval_cond_ref', 'pval_cond_snp',
                 'pval_diff', 'refAllele', 'snpAllele']

    #get all of the needed parts
    @staticmethod
    def return_rows_from_api( api_search_query, api_action):
        fields_for_csv = StreamingCSVDownloadHandler.fields_for_csv()
        mt = MotifTransformer()
        rows = []
        page_of_results = 0 
        keep_on_paging = True
        while keep_on_paging is True:
            search_offset = settings.API_HOST_INFO['download_result_page_size'] * page_of_results
            api_search_query.update(
                               {'from_result':search_offset,
                                'page_size':settings.API_HOST_INFO['download_result_page_size']})
            api_response = requests.post( APIUrls.setup_api_url(api_action),
                 json=api_search_query, headers={'content-type':'application/json'})
            
            page_of_results += 1
            
            if api_response.status_code == 200:
                response_json = json.loads(api_response.text)
                api_response_data = response_json['data']         
                prepared_data = mt.transform_motifs_to_transcription_factors(api_response_data)
                print "hitcount = " + str(response_json['hitcount'])
                print "got this much data out of API this round : " + str(len(api_response_data))
                for dr in prepared_data:
                    rows.append( [ dr[field_name] for field_name in fields_for_csv ])
            else:
                keep_on_paging = False

        print "returning this many rows " + str(len(rows))
        return rows

    @staticmethod
    def streaming_csv_view(request, api_search_query, api_action):
        """A view that streams a large CSV file."""
        # Generate a sequence of rows. The range is based on the maximum number of
        # rows that can be handled by a single sheet in most spreadsheet
        # applications.
        #rows = (["Row {}".format(idx), str(idx)] for idx in range(65536))
        rows = StreamingCSVDownloadHandler.return_rows_from_api(api_search_query, api_action)
        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)
        response = StreamingHttpResponse((writer.writerow(row) for row in rows),
                                         content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'
        return response

class APIUrls:
    @staticmethod
    def setup_api_url(api_function):
        hostinfo = settings.API_HOST_INFO
        host_w_port = ':'.join([ hostinfo['host_url'], hostinfo['host_port'] ] )
        url_arglist =  [ hostinfo['api_root'], api_function]
        url_args = '/'.join(url_arglist)
        url = host_w_port + "/" + url_args  + "/"
        return url
 
