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


#API should be talking to ES. I just want to be sure we can display these.
def dummy_get_svg_plot_from_es():
    es_url = 'http://atsnp-db2.biostat.wisc.edu:9200'          
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
    es_url = 'http://atsnp-db2.biostat.wisc.edu:9200'          
    es_index = '/atsnp_data'
    es_type = '/svg_plots'
    search_endpoint = '/_search'
    plot_search_url = es_url + es_index + es_type + search_endpoint 
    q = { "query" : {
        "bool" : {
          "must" : [ 
                   { "match" : { "snpid"      : plot_info['snpid']     } },
                   { "match" : { "motif"      : plot_info['motif']     } },
                   { "match" : { "snp_allele" : plot_info['snp_allele'] } },
                 ]     } } }
    #print "plot query " + str(q)
    results = requests.post(plot_search_url, data=json.dumps(q))
    if results.status_code == 200: 
        #svg_data = results.json()['hits']['hits'][0]['svg_plot']    
        result_json = results.json()
        hits = result_json['hits']['hits']
        print "hits : " + str(len(hits))
        print "data keys  " + str(hits[0].keys())
        doc_source = hits[0]['_source']
        svg_data = doc_source['svg_plot']
        #return "nothing special"
        return svg_data 
    else:
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


def get_compressed_download(request):
    #with open('eggs.csv', 'wb') as csvfile:
    #output = NamedTemporaryFile(mode='wrb') ## temp output file
    with NamedTemporaryFile() as output:
        #output is supposed to be a csvfile
        writer = csv.writer(output)

        writer.writerow(['first row', 'foo', 'bizzy', 'bar', "fake meat"])
        writer.writerow(['second row', 'bim', 'bab', 3 , "bacon bomb"    ])
        writer.writerow(['first row', 'foo', 'bizzy', 'bar', "paper towels"])
        writer.writerow(['second row', 'bim', 'bab', 3  , "sad pandas"   ])
        writer.writerow(['first row', 'foo', 'bizzy', 'bar', "bad weekends"])
        writer.writerow(['second row', 'bim', 'bab', 3   , "shitty beer"  ])
        writer.writerow(['first row', 'foo', 'bizzy', 'bar', "untreatable illness"])
        writer.writerow(['second row', 'bim', 'bab', 3, "pain and isolation"     ])
        writer.writerow(['first row', 'foo', 'bizzy', 'bar', "fake meat"])
        writer.writerow(['second row', 'bim', 'bab', 3 , "bacon bomb"    ])
        writer.writerow(['first row', 'foo', 'bizzy', 'bar', "paper towels"])
        writer.writerow(['second row', 'bim', 'bab', 3  , "sad pandas"   ])
        writer.writerow(['first row', 'foo', 'bizzy', 'bar', "bad weekends"])
        writer.writerow(['second row', 'bim', 'bab', 3   , "shitty beer"  ])
        writer.writerow(['first row', 'foo', 'bizzy', 'bar', "untreatable illness"])
        writer.writerow(['second row', 'bim', 'bab', 3, "pain and isolation"     ])

        output.write("dogs dogs dogs") 
        output.seek(0)
        output.flush()
        print "read output " + output.read()

        #code for writing csv file go here...
        response = HttpResponse(content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=test.csv.zip'

        z = zipfile.ZipFile(response,'w')   ## write zip to response
        print " what can we do with this? " + repr(dir(output))
        print " what can we do with this? " + repr(dir(output.file))
        print " what can we do with this? " + repr(output.read())
        print " what can we do with this? " + repr(output.file.name)
        tmppath = output.name
        print "temp path " + tmppath
        output.seek(0)
        data_to_write = output.read()
        print "data to write " + data_to_write
        z.writestr("test.csv", data_to_write)  ## write csv file to zip
        #z.write("test.csv", output.file)
        z.close()
    return response



#@gzip_compress   #is the decorator all that is needed?
def get_download(request):
  response = HttpResponse(content_type='text/csv')
  response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'  
  writer = csv.writer(response)
  writer.writerow(['first row', 'foo', 'bizzy', 'bar', "fake meat"])
  writer.writerow(['second row', 'bim', 'bab', 3 , "bacon bomb"    ])
  writer.writerow(['first row', 'foo', 'bizzy', 'bar', "paper towels"])
  writer.writerow(['second row', 'bim', 'bab', 3  , "sad pandas"   ])
  writer.writerow(['first row', 'foo', 'bizzy', 'bar', "bad weekends"])
  writer.writerow(['second row', 'bim', 'bab', 3   , "shitty beer"  ])
  writer.writerow(['first row', 'foo', 'bizzy', 'bar', "untreatable illness"])
  writer.writerow(['second row', 'bim', 'bab', 3, "pain and isolation"     ])
  writer.writerow(['first row', 'foo', 'bizzy', 'bar', "fake meat"])
  writer.writerow(['second row', 'bim', 'bab', 3 , "bacon bomb"    ])
  writer.writerow(['first row', 'foo', 'bizzy', 'bar', "paper towels"])
  writer.writerow(['second row', 'bim', 'bab', 3  , "sad pandas"   ])
  writer.writerow(['first row', 'foo', 'bizzy', 'bar', "bad weekends"])
  writer.writerow(['second row', 'bim', 'bab', 3   , "shitty beer"  ])
  writer.writerow(['first row', 'foo', 'bizzy', 'bar', "untreatable illness"])
  writer.writerow(['second row', 'bim', 'bab', 3, "pain and isolation"     ])

  return response


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

