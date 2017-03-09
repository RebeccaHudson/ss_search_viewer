from django.shortcuts import render
import requests
import json
from ss_viewer.views.shared import MotifTransformer
from ss_viewer.views.shared import APIUrls 
from ss_viewer.views.shared import APIResponseHandler 


#TODO: pull the motif data out of the API, not this static file
from ss_viewer.views.shared import MotifPlottingData

from ss_viewer.views.shared import ExternalResourceUrls 

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

  detail_query = { 'id_string' : id_str }  

  api_response = requests.post( APIUrls.setup_api_url('details-for-one'), 
                                json=detail_query,
                                timeout=100, 
                                headers={'content-type':'application/json'})
  response_json = json.loads(api_response.text)

  #setup the plot.
  #print "response json: " + repr(response_json)
  #the plot data gets put onto the data that's passed in.
  APIResponseHandler.get_plots([response_json])

  mt = MotifTransformer() 
  response_data = mt.transform_motifs_to_transcription_factors([response_json])

  context['api_response'] = response_json

  context['ucsc_link'] =         \
     ExternalResourceUrls.ucsc_link(response_json['chr'], response_json['pos'])

  context['factorbook_link'] =   \
     ExternalResourceUrls.factorbook_link(response_json['trans_factor'])

  #factorbook_link will be None if it's unavailable.
  context['dbsnp_link'] =        \
     ExternalResourceUrls.dbsnp_link(response_json['snpid'])

  context['jaspar_motif_link'] = \
     ExternalResourceUrls.jaspar_motif_link(response_json['motif'])

  return render(request, detail_page_template, context) 
