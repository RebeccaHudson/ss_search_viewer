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

