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
from ss_viewer.views.shared import APIResponseHandler 
from ss_viewer.views.shared import StandardFormset
#TODO: clean up the imports


#TODO: pull the motif data out of the API, not this static file
from ss_viewer.views.shared import MotifPlottingData

from django.core.exceptions import ValidationError
from tempfile import NamedTemporaryFile 
import csv
import zipfile

#This view is not class-based because it doesn't rely on shared code.
#Detail pages look exactly the same between all search types.
#TODO: make sure this view responds only to POST requests.

def one_row_detail(request, id_str):
  detail_page_template = 'ss_viewer/detail.html'
  context = {'id_str': id_str }

  #TODO: put that id into a JSON search query (a dict, pretty much)
  # that has the key 'id_string'
  detail_query = { 'id_string' : id_str }  
  api_response = requests.post( APIUrls.setup_api_url('details-for-one'), 
                                json=detail_query,
                                timeout=100, 
                                headers={'content-type':'application/json'})
  response_json = json.loads(api_response.text)

  #setup the plot.
  print "response json: " + repr(response_json)
  #the plot data gets put onto the data that's passed in.
  APIResponseHandler.get_plots([response_json])

  mt = MotifTransformer() 
  response_data = mt.transform_motifs_to_transcription_factors([response_json])
  context['api_response'] = response_json #drhhrepr(dir(api_response))

  return render(request, detail_page_template, context) 
