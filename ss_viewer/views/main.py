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
from tempfile import NamedTemporaryFile 
import csv
import zipfile

#TODO pare down the imports here. Most of them are not needed at this point.

#from .plots import MakePlots #tempfile writer can stay hiedden
def index(request):
  return HttpResponse("Try another url, like :ss_viewer/multi-search.")



def find_working_es_url(): 
    found_working = False
    i = 0
    while found_working is False:
        url_to_try = settings.ELASTICSEARCH_URLS[i] + '/_cluster/health?timeout=1s&pretty=true'
        es_check_response = requests.get(url_to_try)
        es_check_data = json.loads(es_check_response.text)
        if es_check_data.get('error') is  None:
            return settings.ELASTICSEARCH_URLS[i]
        i += 1

#API should be talking to ES. I just want to be sure we can display these.
def dummy_get_svg_plot_from_es():

    es_index = '/img_update_test'
    es_type = '/dummy_record'
    dummy_id = '/AVWER04sBpk2eOuD830v'
    url = es_url + es_index + es_type + dummy_id
    es_result = requests.get(url)
    to_show = es_result.json()['_source'].keys()
    print "showing this " + str(to_show)
    #print "dumping it out ... " + es_result.text
    svg_plot_data = es_result.json()['_source']['svg_plot']
    return svg_plot_data

def get_plot_data_out_of_es(plot_info):
    #es_url = 'http://atsnp-db1.biostat.wisc.edu:9200'          
    es_url = find_working_es_url()
    es_index = '/atsnp_data'
    es_type = '/svg_plots'
    search_endpoint = '/_search?size=1'
    plot_search_url = es_url + es_index + es_type + search_endpoint 
    q = { "query" : {
        "bool" : {
          "must" : [ 
                   { "match" : { "snpid"      : plot_info['snpid']     } },
                   { "match" : { "motif"      : plot_info['motif']     } },
                   { "match" : { "snp_allele" : plot_info['snp_allele'] } },
                 ]     } } }
    results = requests.post(plot_search_url, data=json.dumps(q))
    if results.status_code == 200: 
        #svg_data = results.json()['hits']['hits'][0]['svg_plot']    
        result_json = results.json()
        hits = result_json['hits']['hits']
        print "hits : " + str(len(hits))
        if len(hits) > 0:
            print "data keys  " + str(hits[0].keys())
            doc_source = hits[0]['_source']
            svg_data = doc_source['svg_plot']
            #return "nothing special"
            return svg_data 
        print result_json
    print "no plot found for " + str(plot_info)
    return None

def get_plot_query_info_from_string(query_str):
    split_parts = query_str.split("_")
    motif = split_parts[0]
    snpid = split_parts[1]
    snpAllele = split_parts[2]
    return { 'motif' : motif, 
             'snpid' : snpid, 
             'snp_allele' : snpAllele}

#this should take a post with the request data
def dynamic_svg(request, plot_id_string):
    print "running dynamic svg, plot_id_string = "  + plot_id_string
    #should be able to make an API request with this data that will return a plot
    plot_info = get_plot_query_info_from_string(plot_id_string)
    image = get_plot_data_out_of_es(plot_info)
    #image=get_svg_plot_from_es()
    return HttpResponse(image, content_type="image/svg+xml")

def test_svg_plots(request):
    name_of_template  =  'ss_viewer/show_test_plot.html' 
    #template = loader.get_template(name_of_template)
    #data_from_post = requests.post(url_of_dyn, data=json.dumps({'bit of post data':69})
    #I intend to put the data that comes out of ES on the result itself into the output file.
    plot_id_string = 'MA0002.2_rs538221432_T'
    context =  {'dynamic_svg_data' : reverse('ss_viewer:dynamic-svg', args=[plot_id_string]),
                 "happy_data" : "eat, shit, and die." } 
    # in original example ,reverse also has args=['gene_links_graph'])})

    #context = { "happy_data" : "eat, shit, and die.",
    #            "plot_data"  : svg_plot_data }
    return render(request, name_of_template, context)




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


def help_page(request):
    help_page_template = 'ss_viewer/help-page.html'
    context = {}
    return render(request, help_page_template, context) 

    #reverse('ss_viewer:help-page')



