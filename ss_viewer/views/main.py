from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.conf import settings
import pickle
import requests
import json
import re
import os
from ss_viewer.forms import SearchBySnpidForm  #replaces ScoresSearchForm
from ss_viewer.forms import SearchByGenomicLocationForm
from ss_viewer.forms import SearchByTranscriptionFactorForm
import django.forms

from django.core.files.uploadedfile import SimpleUploadedFile

from ss_viewer.views.shared import MotifTransformer
from ss_viewer.views.shared import TFTransformer
from ss_viewer.views.shared import APIUrls 
from ss_viewer.views.shared import PValueFromForm 
from ss_viewer.views.shared import StandardFormset
from django.core.exceptions import ValidationError

from ss_viewer.views.snpid_search import SnpidSearchUtils

#from .plots import MakePlots #tempfile writer can stay hiedden

#found at the URL: ss_viewer
def index(request):
  return HttpResponse("This is a basic response")


def setup_api_url(api_function, snpid=None):
  return APIUrls.setup_api_url(api_function)

#this is shared, I think.
def transform_motifs_to_transcription_factors(response_json):
    tft = MotifTransformer()
    return tft.transform_motifs_to_transcription_factors(response_json)

def extract_snpids_from_textfield(text):
  return SnpidSearchUtils.extract_snpids_from_textfield(text) 

# TODO refer to a default p-value from settings.
def get_pvalue_rank_from_form(form):
  return PValueFromForm.get_pvalue_rank_from_form(form)
   
#this should go into snpid search stuff.
def clean_and_validate_snpid_text_input(text_input):
    return SnpidSearchUtils.clean_and_validate_snpid_text_input(text_input)

# Either by textarea or by file, snpid search form is not 
# valid unless one of these is present 
def get_snpid_list_from_form(request, form):
    return SnpidSearchUtils.get_snpid_list_from_form(request, form)

def setup_context_for_snpid_search_results(api_response, snpid_list, holdover_p_value, 
                                           page_of_results_to_display):
    status_message = ""; response_json = None
    response_data = None
    if api_response.status_code == 204:
        status_message = "No matches for requested snpids" 
    else:
        count_of_requested_snpids = len(snpid_list)
        response_json = json.loads(api_response.text)
        response_data = transform_motifs_to_transcription_factors(response_json['data'])
        status_message = 'Got ' + str(response_json['hitcount']) + ' hits.'
        status_message += " Showing page " + str(page_of_results_to_display) + " of results."    
    snpid_form = SearchBySnpidForm({'raw_requested_snpids':", ".join(snpid_list),
                                    'pvalue_rank_cutoff' : holdover_p_value, 
                                    'page_of_results_shown': page_of_results_to_display }  )
    search_paging_info = get_paging_info_for_display(response_json['hitcount'], 
                                                      page_of_results_to_display) 

    context = setup_formset_context(snpid_form=snpid_form)
    context.update({'api_response' :  response_data, 'status_message' : status_message,
                    'holdover_snpids' : ', '.join(snpid_list), 
                    'search_paging_info' : search_paging_info }) 
    return context

def setup_formset_context(tf_form=None, gl_form=None, snpid_form=None):
    return StandardFormset.setup_formset_context(tf_form, gl_form, snpid_form)

#The above function 'get_scores_for_list' should actually be called
#handle search by genomic location.. 
#this should only handle POST
def handle_search_by_genomic_location(request):
    if request.method == 'GET':
        return redirect(reverse('ss_viewer:multi-search'))

    if request.method == 'POST': 
        searchpage_template = 'ss_viewer/multi-searchpage.html'  
        gl_search_form = SearchByGenomicLocationForm(request.POST)
      
        search_paging_info = None 
        status_message = ""
        response_data = None

        if not gl_search_form.is_valid():
             context = setup_formset_context(gl_form=gl_search_form)
             context.update({'status_message' :  "Invalid search. Try agian."})
             return(request, searchpage_template, context)
        form_data = gl_search_form.cleaned_data
        search_request_params = get_paging_info_for_request(request, 
                                                             form_data['page_of_results_shown'])
        api_search_query = { 'chromosome' : form_data['selected_chromosome'],
                             'start_pos'  : form_data['gl_start_pos'], 
                             'end_pos'    : form_data['gl_end_pos'],
                             'pvalue_rank': form_data['pvalue_rank_cutoff'],
                             'from_result': search_request_params['search_result_offset'] }
        api_response = requests.post( setup_api_url('search-by-gl'), 
               json=api_search_query, headers={ 'content-type' : 'application/json' })

        # DRY up the following part here, if it appears to be possible.
        response_json = None
        if api_response.status_code == 204:
            status_message = "No matching rows"
        elif api_response.status_code == 400:
            status_message  = "API reported an error: " + api_response.text
        else:
            response_json = json.loads(api_response.text)
            print "whatever this is: " + str(response_json['data'])
            response_data = transform_motifs_to_transcription_factors(response_json['data'])
            status_message = 'Got ' + str(response_json['hitcount']) + ' rows back from API.'
            status_message+= ' page shown '+str(search_request_params['page_of_results_to_display'])
            form_data['page_of_results_shown'] = search_request_params['page_of_results_to_display']
            search_paging_info = get_paging_info_for_display(response_json['hitcount'],
                                             search_request_params['page_of_results_to_display'])
        new_form = SearchByGenomicLocationForm(form_data)
        context = setup_formset_context(gl_form = new_form)
        context.update({'api_response' : response_data, 
                        'holdover_gl_region': api_search_query,
                        'search_paging_info': search_paging_info })
        print("context : " + repr(context)) 
        return render(request, searchpage_template, context)


def lookup_motif_by_tf(trans_factor):
    tft = TFTransformer()
    #There can be > 1 motif for one transcription factor. 
    return tft.lookup_motifs_by_tf(trans_factor)
    #lut = None
    ##TODO: the following pickle must be processed in such a way that a 
    ## lookup on a TF with multiple motif values returns a list.
    #fpath = os.path.dirname(os.path.dirname(__file__)) + "/lookup-tables" +\
    #  '/lut_jaspar_motifs_by_tf.pkl'
    #with open(fpath , 'r') as f: 
    #    lut = pickle.load(f) 
    #one_or_more_motif_values = lut[trans_factor]
    #if not type(one_or_more_motif_values) == list:
    #  one_or_more_motif_values = [one_or_more_motif_values]
    #return one_or_more_motif_values


def handle_search_by_trans_factor(request):
    if request.method == 'GET':
        return redirect(reverse('ss_viewer:multi-search'))

    if request.method == 'POST':
        searchpage_template = 'ss_viewer/multi-searchpage.html'  
        tf_search_form = SearchByTranscriptionFactorForm(request.POST)

    search_paging_info  = None 
    status_message = ""
    response_data = None

    if not tf_search_form.is_valid():
        context = setup_formset_context(tf_form=tf_search_form)
        context.update({'status_message': "Invalid search. Try agian."})
        return render(request, searchpage_template, context)
    form_data = tf_search_form.cleaned_data
    trans_factor = form_data['trans_factor'] 
    motif_value = lookup_motif_by_tf(trans_factor) 
   
    search_request_params = get_paging_info_for_request(request, 
                                                form_data['page_of_results_shown']) 
 
    api_search_query = { 'motif' : motif_value,
                         'pvalue_rank': form_data['pvalue_rank_cutoff'],
                         'from_result' : search_request_params['search_result_offset']
                       }
    
    api_response = requests.post( setup_api_url('search-by-tf'),
             json=api_search_query, headers={'content-type':'application/json'})
  
    response_json = None
    if api_response.status_code == 204:
        status_message = 'No matching rows.'
    else:
        response_json = json.loads(api_response.text)
        response_data = transform_motifs_to_transcription_factors(response_json['data'])
        status_message = 'Got ' + str(response_json['hitcount']) + ' rows back from API.'
        status_message += ' page shown ' + str(search_request_params['page_of_results_to_display'])
        form_data['page_of_results_shown'] = search_request_params['page_of_results_to_display']
         
        hitcount = response_json['hitcount']
        search_paging_info = get_paging_info_for_display(hitcount, 
                                           search_request_params['page_of_results_to_display'])

        tf_search_form = SearchByTranscriptionFactorForm(form_data)

    context = setup_formset_context(tf_form=tf_search_form)
    context.update({'api_response' : response_data, 
                    'search_paging_info' : search_paging_info,
                    'status_message'     : status_message})
    return render(request, searchpage_template, context)


#Def this is the actual multi-search page, this handles the GET.
def show_multisearch_page(request):
    searchpage_template = 'ss_viewer/multi-searchpage.html'  
    gl_search_form = SearchByGenomicLocationForm()
    snpid_search_form = SearchBySnpidForm()
    tf_search_form  = SearchByTranscriptionFactorForm(initial={'page_of_results_shown':0})
    #plotting_data = get_a_plot_by_snpid_and_motif('rs111200574', 'fake.motif')
    # needs a DLL plotting_data = get_a_plot_by_snpid_and_motif('rs111200574', 'fake.motif')
    context = setup_formset_context()
    context.update({'status_message' : "Enter a search.", 
                    'active_tab'     : 'none-yet'})
    #context = { 'gl_search_form'    : gl_search_form, 
    #            'snpid_search_form' : snpid_search_form,
    #            'tf_search_form'    : tf_search_form,
    #            'status_message'    : status_message,
    #            'active_tab'        : 'none-yet',
    #            'plotting_data'     : 'ss_viewer/test_plot.svg' }   
    #           
    #path to a plot should look like: 'ss_viewer/test_plot.html' 
    return render(request, searchpage_template, context)




#takes info from the request on the form to seutp the offset 
#for requesting data from the API.
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


#setups up paging stuff for the webpage 
def get_paging_info_for_display(hitcount, page_of_results_to_display):
    search_paging_info = {'show_next_btn': False, 'show_prev_btn': False}    
    hits_paged = (page_of_results_to_display ) * \
                 settings.API_HOST_INFO['result_page_size']
    if hitcount > hits_paged:
        search_paging_info['show_next_btn'] = True 
    if page_of_results_to_display > 1:
         search_paging_info['show_prev_btn'] = True
    return search_paging_info


def get_a_plot_by_snpid_and_motif(snpid, motif):  #TODO: should take a snpid!
    #path_to_images = os.path.join(os.path.dirname(__file__), 'pictures')
    #path_to_image = os.path.join(path_to_images, 'test_plot.svg')
    url = setup_api_url('plotting-data')
    headers = { 'content-type':'application/json' }
    api_search_query = { 'snpid': snpid, 'motif': motif }
    api_response = requests.post(url, 
                                 json=api_search_query,
                                 headers=headers)
    response_json = None
    if api_response.status_code == 204:
        plot_status_message = 'No matching rows.'
    else:
        response_json = json.loads(api_response.text)
        status_message = 'Got ' + str(len(response_json)) + ' rows back from API.'
        print("here's the API response" + str(response_json))

        plotter = MakePlots(response_json)
        plotter.make_plot()

    path_to_image = os.path.join("pictures", 'test_plot.svg')
    return { 'image_path' : path_to_image, 'plotting_data' : response_json }

