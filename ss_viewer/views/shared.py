from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
import os
import json
import pickle
import requests
import csv
import re
from tempfile import NamedTemporaryFile
from ss_viewer.forms import SearchBySnpidForm  #replaces ScoresSearchForm
from ss_viewer.forms import SearchByGenomicLocationForm
from ss_viewer.forms import SearchByTranscriptionFactorForm
from ss_viewer.forms import SearchBySnpidWindowForm
from ss_viewer.forms import SearchByGeneNameForm
from ss_viewer.forms import SharedSearchControlsForm

from django.core.urlresolvers import reverse
from django.shortcuts import redirect
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
        if trans_factor is None:
             #probably  encode, if not, fall back as though it was.
             trans_factor = motif_value.split("_")[0]
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
    def __init__(self, jaspar_or_encode):
        lut = None;  fpath = None
        if jaspar_or_encode == 'jaspar':
         which_one = '/lut_jaspar_motifs_by_tf.pkl'
        else: #assuming 'encode' 
          which_one = '/lut_encode_motifs_by_family.pkl'
        fpath = os.path.dirname(os.path.dirname(__file__)) + "/lookup-tables" +\
                  which_one
        with open(fpath , 'r') as f:  
            lut = pickle.load(f) 
        self.lut = lut

    def lookup_motifs_by_tf(self, trans_factor):
        one_or_more_motif_values = self.lut[trans_factor]
        if not type(one_or_more_motif_values) == list:
          one_or_more_motif_values = [one_or_more_motif_values]
        return one_or_more_motif_values




#includes all of the forms that should be loaded every time.
class StandardFormset:
     @staticmethod
     def setup_formset_context(tf_form=None, 
                               gl_form=None,
                               snpid_form=None,
                               snpid_window_form=None,
                               gene_name_form=None):

          #Setup the shared search controls form.
          shared_search_controls_form = SharedSearchControlsForm()

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

          context =  { 'tf_search_form'   : tf_form,
                       'gl_search_form'    : gl_form,
                       'snpid_search_form' : snpid_form, 
                       'snpid_window_form' : snpid_window_form,
                       'gene_name_form'    : gene_name_form,
                       'shared_search_controls_form' : shared_search_controls_form }

          if active_tab is not None:
              context.update({'active_tab': active_tab })
          context.update({"tooltips": settings.ALL_TOOLTIPS} )
          return context 

     @staticmethod
     def show_multisearch_page(request):
          searchpage_template = 'ss_viewer/multi-searchpage.html'
          context = StandardFormset.setup_formset_context()
          context.update({'status_message' : "Enter a search.",
                          'active_tab'     : 'none-yet'})
          if request.GET and request.GET['flavor']:
              context['flavor'] = request.GET['flavor']
          return render(request, searchpage_template, context)

     #Might be worth moving out of this class.
     @staticmethod
     def handle_invalid_form(context, status_message=None):
          if status_message == None:
              status_message =  "Invalid search. Try again."
          context.update({'status_message' :  status_message })
          return context

class Paging:
    @staticmethod
    def get_paging_info_for_request(request, page_of_search_results):
        last_page_size = None
        page_of_results_to_display = 1
        print "page of search results " + repr(page_of_search_results) + str(page_of_search_results)
        page_of_search_results = int(page_of_search_results)
        if request.POST['action'] == 'Next':
             page_of_results_to_display = page_of_search_results + 1
        elif request.POST['action'] == 'Prev':
             page_of_results_to_display = page_of_search_results - 1
        elif 'jump' in request.POST['action']:
             #VALIDATION?
             page_of_results_to_display = \
                 int(request.POST['action'].split('-')[1])

        search_result_offset = (page_of_results_to_display - 1) * \
                              settings.API_HOST_INFO['result_page_size']


        max_page_available = Paging.calculate_max_page_available()

        #The size of the last page to display has to be calculated.
        if max_page_available == page_of_results_to_display:
            last_page_size =                                     \
             settings.HARD_LIMITS['ELASTIC_MAX_RESULT_WINDOW'] - \
               ((max_page_available - 1)   *                     \
                 settings.API_HOST_INFO['result_page_size']      \
               )
            print "calculated last page size " + str(last_page_size)

        return { 'search_result_offset'       : search_result_offset,
                 'page_of_results_to_display' : page_of_results_to_display,
                 'last_page_size'             : last_page_size  }
        #last page size is None if this is not the last page

    @staticmethod
    def calculate_max_page_available():
        #the last page will have fewer results on it.
        return (settings.HARD_LIMITS['ELASTIC_MAX_RESULT_WINDOW'] / \
               settings.API_HOST_INFO['result_page_size']) + 1 

    @staticmethod
    def get_paging_info_for_display(hitcount, page_of_results_to_display):
        search_paging_info = {'show_next_btn': False, 'show_prev_btn': False}
        max_page_available = Paging.calculate_max_page_available()
        hits_paged = (page_of_results_to_display ) * \
                     settings.API_HOST_INFO['result_page_size']
        if hitcount > hits_paged and \
           page_of_results_to_display < max_page_available:
            search_paging_info['show_next_btn'] = True
        if page_of_results_to_display > 1:
             search_paging_info['show_prev_btn'] = True
        
        search_paging_info['page_of_results_to_display'] = page_of_results_to_display
        totalPageCount = (hitcount / settings.API_HOST_INFO['result_page_size']) + 1
        search_paging_info['total_page_count'] = totalPageCount 

        search_paging_info['max_page_available'] = Paging.calculate_max_page_available()
        #could be refactored so calculation above does not get repeated in 'setup_hits_message'
        return search_paging_info



class APIResponseHandler:
    @staticmethod  
    def setup_hits_message(hitcount, page_of_results_to_display):
        #Showing page N, a through b of N total pairs.
        #could be refactored so the following calculation is not repeated in the 'Paging' class.
        totalPageCount = (hitcount / settings.API_HOST_INFO['result_page_size']) + 1
        #hitsMsg = ""
        #if hitcount > settings.HARD_LIMITS['ELASTIC_MAX_RESULT_WINDOW']:
        #    hitsMsg +=  \
        #     "The first {:,}".format( \
        #           settings.HARD_LIMITS['ELASTIC_MAX_RESULT_WINDOW']) +\
        #     "  available from  "
        hitsMsg =  "Query returned {:,} (SNP,TF) pairs.".format(hitcount)
        #hitsMsg +=  " Showing page: {:,}".format(page_of_results_to_display) +\
        #            " out of  {:,}.".format(totalPageCount)
        return hitsMsg
                    
    @staticmethod 
    #meant to handle one page of results at a time.
    #start with just the first result
    def get_plots(rows_to_display):
        plot_data = {} 
        field_names = ['motif', 'snpid', 'snpAllele'] 
        for one_row in rows_to_display:
            plot_id_str = \
              "_".join([one_row[field_name] for field_name in field_names ])
            plot_id_str_for_web_page = plot_id_str.replace(".", "_")
            one_row['plot_id_str'] = plot_id_str_for_web_page

            #Motifs for ENCODE and JASPAR are pulled from an Elasticsearch 
            #index by the API.
            motif_data_b = json.loads(one_row['motif_bits'])
            json_for_plotting = { 'snp_aug_match_seq': one_row['snp_aug_match_seq'],
                                  'snp_extra_pwm_off': one_row['snp_extra_pwm_off'],
                                  'ref_aug_match_seq': one_row['ref_aug_match_seq'],
                                  'ref_extra_pwm_off': one_row['ref_extra_pwm_off'],
                                  'snp_strand'      : one_row['snp_strand'],
                                  'ref_strand'      : one_row['ref_strand'], 
                                  'motif'           : one_row['motif'],
                                  'motif_data'      : motif_data_b, #change to _b ...
                                  'snpid'           : one_row['snpid'],
                                  'plot_id_str'     : plot_id_str_for_web_page
                                 }
            one_row['json_for_plotting'] = json.dumps(json_for_plotting)
        if not any(plot_data):
            return None
        return { 'response_data' : rows_to_display, 
                 'plot_data': plot_data } 

    @staticmethod
    def check_that_result_window_is_not_exceeded(search_request_params):
        last_doc_requested =  \
        settings.API_HOST_INFO['result_page_size'] + \
        search_request_params['search_result_offset']
          
        limit =  settings.HARD_LIMITS['ELASTIC_MAX_RESULT_WINDOW']
        print "last doc requested : " + str(last_doc_requested)
        print "hard ES window limit " + str(limit)
        print "all of the search_request_parameters : " + repr(search_request_params)
        if last_doc_requested <= limit:
            return True
        return False

    #BEGIN code that needs Elastic to test.
    @staticmethod
    def check_cutoff(operator, cutoff, value_to_check):
        if operator == 'lte':
            return value_to_check <= cutoff 
        elif operator == 'lt':
            return value_to_check < cutoff 
        elif operator == 'gte':
            return value_to_check >= cutoff 
        elif operator == 'gt':
            return value_to_check > cutoff 
        assert False #If exection reaches this point, 
                     #a bad operator was passed.
        #Add more checks if external users want to use this function.

    #given a row of search results and 'loss' or 'gain' this returns if each row
    #meets the critera for loss or gain of function as specified.
    @staticmethod
    def test_change_of_function(one_row, loss_or_gain):
        cutoffs = settings.GAIN_AND_LOSS_DEFS[loss_or_gain]

        cutoff  = cutoffs['pval_ref']['cutoff']
        operator = cutoffs['pval_ref']['operator']
        value = one_row['pval_ref']
        ref_change = APIResponseHandler.check_cutoff(operator, cutoff, value)

        cutoff  = cutoffs['pval_snp']['cutoff']
        operator = cutoffs['pval_snp']['operator']
        value = one_row['pval_snp']
        snp_change = APIResponseHandler.check_cutoff(operator, cutoff, value)
        return ref_change and snp_change 

    @staticmethod
    def add_color_coding_to_search_results(results):
        function_change = settings.GAIN_AND_LOSS_DEFS
        for result in results:
            if APIResponseHandler.test_change_of_function(result, 'gain'):
                result['color_code'] = 'gain' 
            elif APIResponseHandler.test_change_of_function(result, 'loss'):
                result['color_code'] = 'loss'
            else:
                result['color_code'] = 'neutral'
        return results
    #END code that needs Elastic to test 

    @staticmethod
    #api_action should be 'search-by-tf' or 'search-by-gl'
    #This code gets repeated between every search.
    def handle_search(api_search_query, api_action, search_request_params):
        response_data = None
        plot_source = None
        api_response = None
        search_paging_info = None
        page_size = settings.API_HOST_INFO['result_page_size']
        print "attempting search, query: " + repr(api_search_query)
        if search_request_params['last_page_size'] is not None:
            page_size = search_request_params['last_page_size'] 
            print "use last page size " + str(page_size)
        api_search_query.update( {"page_size": page_size })
        try:
            api_response = requests.post( APIUrls.setup_api_url(api_action),
                                      json=api_search_query, 
                                      timeout=300,
                                      headers={'content-type':'application/json'})
        except requests.exceptions.Timeout:
             print "Request timed out !! for the following query" + str(api_search_query) 

        if api_response is  None:
             status_message = "API timed out. Request took too long."
        elif api_response.status_code == 204:
             status_message = 'No results match the query.'
        elif api_response.status_code == 207:
            if str(api_response.text).find('INFO') is not -1:
                status_message  = api_response.text.replace('"', "")
        elif api_response.status_code == 500:
            status_message = 'API error; no data returned.'
            if len(api_response.text) > 0 and len(api_response.text) < 200:
                status_message += " More info: "+api_response.text.replace('"', "")

        elif api_response.status_code == 400:
            status_message = "Problem with search: " + api_response.text.replace('"', "")
        else:
            response_json = json.loads(api_response.text)
            #print "response json " + str(response_json['data'][0].keys())
            mt = MotifTransformer()
            response_data = mt.transform_motifs_to_transcription_factors(response_json['data'])
            
            response_data = \
              ExternalResourceUrls.add_links_to_search_results(response_data)

            response_data = \
              APIResponseHandler.add_color_coding_to_search_results(response_data)

            #slyly avoiding nested dictionaries. 
            plot_data = APIResponseHandler.get_plots(response_data)

            if plot_data is not None: #append the plot id strings to each row..
                response_data = plot_data['response_data']
                plot_source = plot_data['plot_data']          

            status_message = APIResponseHandler.setup_hits_message(response_json['hitcount'], 
                                       search_request_params['page_of_results_to_display'])

            search_paging_info = Paging.get_paging_info_for_display(response_json['hitcount'],
                                        search_request_params['page_of_results_to_display'])
        return  {'status_message' : status_message, 
                 'search_paging_info' : search_paging_info,
                 'api_response'       : response_data,
                 'plot_source'          : plot_source }
    


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
    #pval_rank is now called pval_snp_impact. Change other field names here if they are to 
    #have different names than those in the raw data/ Elasticsearch index.
    def field_labels_for_csv(): 
        return  ['chr', 'pos', 'snpid', 'trans_factor', 'motif', 
                 'pval_snp_impact','log_lik_ref', 'log_lik_ratio', 'log_enhance_odds',
                 'log_reduce_odds', 'log_lik_snp', 'snp_strand', 'ref_strand',
                 'pval_ref', 'pval_snp', 'pval_cond_ref', 'pval_cond_snp',
                 'pval_diff', 'refAllele', 'snpAllele']

    @staticmethod
    def fields_for_csv():
        return  ['chr', 'pos', 'snpid', 'trans_factor', 'motif', 
                 'pval_rank','log_lik_ref', 'log_lik_ratio', 'log_enhance_odds',
                 'log_reduce_odds', 'log_lik_snp', 'snp_strand', 'ref_strand',
                 'pval_ref', 'pval_snp', 'pval_cond_ref', 'pval_cond_snp',
                 'pval_diff', 'refAllele', 'snpAllele']

    #get all of the needed parts.  Check against limits!
    @staticmethod
    def return_rows_from_api( api_search_query, api_action):
        fields_for_csv = StreamingCSVDownloadHandler.fields_for_csv()
        mt = MotifTransformer()
        rows = []
        #Add headers to the downloaded data.
        scroll_id = None   #should I move this?
        rows.append(StreamingCSVDownloadHandler.field_labels_for_csv()) 
        page_of_results = 0 
        keep_on_paging = True

        #remove 'search_offset'
        #search_offset = settings.API_HOST_INFO['download_result_page_size'] * page_of_results
        #just run with the query as it is to begin with. 
        #api_search_query.update(
        #                   {'from_result':search_offset,
        #                    'page_size':settings.API_HOST_INFO['download_result_page_size']})

        api_search_query.update({'for_download': True})
        print "for download: api search query : "+ repr(api_search_query)

        api_response = requests.post( APIUrls.setup_api_url(api_action),
             json=api_search_query, headers={'content-type':'application/json'})
                     
        while keep_on_paging is True:
            page_of_results += 1
            if page_of_results > 30: 
                keep_on_paging = False  #try to scroll here!
            #status code changes to 204 when there is no data left to page through. 
            if api_response.status_code == 200:
                response_json = json.loads(api_response.text)
                api_response_data = response_json['data']         
                prepared_data = mt.transform_motifs_to_transcription_factors(api_response_data)
                for dr in prepared_data:
                    rows.append( [ dr[field_name] for field_name in fields_for_csv ])
                    if len(rows) - 1 >= settings.HARD_LIMITS['MAX_CSV_DOWNLOAD']:
                        keep_on_paging = False
                        break
                #just handled the return data 
                print "here's the response json keys " + repr(response_json.keys())
                #under what conditions do we not have a scroll id?
                api_response = requests.post(APIUrls.setup_api_url('continue-scroll'),
                                           json = {'scroll_id': response_json['scroll_id']})
                print "status code spit out by API response; " + str(api_response.status_code)

            else:
                print "api response : " + api_response.text
                keep_on_paging = False
        
            #this should be sending the scroll id to the API.
            #the api action is 'continue_scroll'

        print "returning this many rows " + str(len(rows))
        return rows

    @staticmethod
    def streaming_csv_view(request, api_search_query, api_action):
        """A view that streams a large CSV file."""
        # Generate a sequence of rows. The range is based on the maximum number of
        # rows that can be handled by a single sheet in most spreadsheet
        # applications.
        rows = StreamingCSVDownloadHandler.return_rows_from_api(api_search_query, api_action)
        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)
        response = StreamingHttpResponse((writer.writerow(row) for row in rows),
                                         content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="search-results.csv"'
        print "response info :  " + repr(response)
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
 
class ExternalResourceUrls:
    @staticmethod
    def dbsnp_link(snpid):
        link = 'https://www.ncbi.nlm.nih.gov/projects/SNP/' \
                + 'snp_ref.cgi?rs=' + snpid; 
        return link 

    #takes the raw stirng values
    @staticmethod
    def ucsc_link(chromosome, position):
        chromosome = chromosome.replace('ch', 'chr') 
        position = int(position)
        half_width = settings.UCSC_WINDOW_WIDTH/2
        posWindowStart = str(position - half_width)
        if posWindowStart < 0:
            posWindowStart = 0
        posWindowEnd = str(position + half_width)             
        linkBits = \
           ['http://genome.ucsc.edu/cgi-bin/hgTracks?org=Human',
            '&db=hg38&position=', chromosome, ':', posWindowStart,'-',
             posWindowEnd ]
        ucsc_link = ''.join(linkBits)
        return ucsc_link  
 
    @staticmethod
    def factorbook_link(t_factor):
        factorbookJaspar = \
           ["ELK1","RELA","TBP","BRCA1","CTCF","GABPA","REST","ESR1","ARID3A",
            "NFIC","CREB1","CEBPB","E2F4","E2F6","ELF1","FOS","FOSL1","FOSL2",
            "HNF4G","HSF1","JUN","JUND","MAFF","MAFK","MEF2C","NFYB","NR2C2",
            "NRF1","POU2F2","PRDM1","RFX5","SP2","TCF7L2","USF2","ZBTB33",
            "ZNF263","E2F1","EBF1","EGR1","ELK4","FOXA1","GATA2","GATA3",
            "HNF4A","IRF1","MAX","MEF2A","NFYA","PAX5","SP1","SRF","STAT1",
            "STAT3","USF1","RRA","FOXP2","SREBF1","SREBF2","THAP1","NR3C1"]
        #TODO: add the ENCODE transcription factors.

        #check if t_factor is in that there list. 
        if t_factor in factorbookJaspar:
            return 'http://www.factorbook.org/human/chipseq/tf/' + t_factor 
        return None  #handle this in the view.

    #A subset of ENCODE motifs don't have links directly available.
    #If the given motif is among these, lookup the correspoinding 'linkable' motif.
    @staticmethod 
    def encode_motif_for_link(encode_motif):
        fpath = os.path.dirname(os.path.dirname(__file__)) + "/lookup-tables" +\
        '/lut_encode_motifs_for_link.pkl'
        lut = None
        with open(fpath , 'r') as f:
            lut = pickle.load(f)
        if encode_motif in lut:
            return lut[encode_motif] 
        #if it's not included in the 'for links' lookup table, use the same
        #motif as was passed to this method.
        return encode_motif

 
    @staticmethod 
    def motif_link(motif):
        link_start = None; link_end = None
        if re.match('MA(\d)+\.\d', motif):
            link_start = 'http://jaspar.genereg.net/cgi-bin/jaspar_db.pl?ID='
            link_end = '&rm=present&collection=CORE'
            return ''.join([link_start, motif, link_end])
        return None
        #else:
            #Detect and handle ENCODE motifs in the same way that the
            #MotifTransformer class does. (They don't meet the JASPAR regex.)
            #motif = ExternalResourceUrls.encode_motif_for_link(motif)
            #link_start = \
            #  'http://compbio.mit.edu/encode-motifs/logos/table/logos/mat/fwd/' 
            #link_end = '.txt'
        # if ENCODE motifs should be included: return ''.join([link_start, motif, link_end]) 

    @staticmethod
    #use motif transformer code as a pattern
    def add_links_to_search_results(results):
        for one_row in results:
            one_row['dbsnp_link'] = \
               ExternalResourceUrls.dbsnp_link(one_row['snpid'])
            one_row['ucsc_link'] =  \
               ExternalResourceUrls.ucsc_link(one_row['chr'], one_row['pos'])
            one_row['factorbook_link'] = \
               ExternalResourceUrls.factorbook_link(one_row['trans_factor'])
            #JASPAR motif link is not added; it's only shown on the detail page.
        return results

