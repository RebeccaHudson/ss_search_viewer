from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
import requests
import json
import re

from .forms import ScoresSearchForm
from django.core.files.uploadedfile import SimpleUploadedFile


#found at the URL: ss_viewer
def index(request):
  return HttpResponse("This is a basic response")

def one_snp_detail(request, snpid_numeric):
  #the requests library probably has a cleaner, happier way to do this.
  url = setup_api_url( 'one-scores-snpid', "rs" + snpid_numeric)
  print("url = " + url) 
  r = requests.get(url)
  return HttpResponse(r.text)

#def get_scores_for_list(request):
#  context_to_pass = { }
#  if request.method == 'POST':
#    raw_snpids = request.POST.get('requested_snpids')
#    snpid_list = extract_snpids_from_textfield(raw_snpids)
#    api_url = setup_api_url('search')
#    req_headers = { 'content-type' : 'application/json' }
#    api_response  = requests.post(api_url, 
#                                json=snpid_list, headers=req_headers)
#    context_to_pass['api_response'] = json.loads(api_response.text)
#    context_to_pass['holdover_snpids'] = ", ".join(snpid_list)
#  return render(request, 'ss_viewer/searchpage.html', context_to_pass )

def extract_snpids_from_textfield(text):
  gex = re.compile('(rs[0-9]+)', re.MULTILINE)  
  list_of_snpids = gex.findall(text)
  return list_of_snpids

def setup_api_url(api_function, snpid=None):
  hostinfo = settings.API_HOST_INFO 
  host_w_port = ':'.join([ hostinfo['host_url'], hostinfo['host_port'] ] )
  url_arglist =  [ hostinfo['api_root'], api_function] 
  if snpid:
    url_arglist.append(snpid)
  url_args = '/'.join(url_arglist) 
  url = host_w_port + "/" + url_args  + "/"
  return url

def handle_uploaded_file(file_pointer):
  #break if there is no file pointer and this is called.      
  #if file_pointer is None:
  #  print "no file pointer" 
  #  return None
  text_in_file = file_pointer.read() 

  return clean_and_validate_snpid_text_input(text_in_file)

def clean_and_validate_snpid_text_input(text_input):
  snpids = extract_snpids_from_textfield(text_input)
  deduped_snpids = list(set(snpids))  #don't allow any duplicate requests.
  if len(deduped_snpids) == 0:  
    raise forms.ValidationError("No snpids have been included")  
  return deduped_snpids


def get_scores_for_list(request):
  searchpage_template = 'ss_viewer/searchpage.html'
  if request.method == 'POST':

    form = ScoresSearchForm(request.POST, request.FILES)
    status_message = ""  #used to indicate to users status of their search results. 

    if form.is_valid():
       snpid_list = None
       try:
         if form.cleaned_data['raw_requested_snpids']: #this is detected properly?
           snpid_list = clean_and_validate_snpid_text_input(form.cleaned_data['raw_requested_snpids'])
         else:
           snpid_list = handle_uploaded_file(request.FILES.get('file_of_snpids'))
       except forms.ValidationError:
         status_message = "No properly formatted SNPids in the text."           
         return render(request, searchpage_template, {'form': ScoresSearchForm(),
                                                      'status_message': status_message })

       api_response = requests.post( setup_api_url('search'), 
             json=snpid_list, headers={ 'content-type' : 'application/json' })

       response_json = None 

       if api_response.status_code == 204:
         status_message = "No matches for requested snpids" 
       else:
         count_of_requested_snpids = len(snpid_list)
         status_message = "Retrieved data for {0} out of {1} requested snpids.".format(
                  66666,  count_of_requested_snpids)
         response_json = json.loads(api_response.text)

       context = { 'api_response'  :  response_json,
                   'status_message':  status_message,
                   'holdover_snpids': ", ".join(snpid_list),
                   'form' : ScoresSearchForm({'raw_requested_snpids':", ".join(snpid_list)})
                 }
       return render(request, searchpage_template, context )

    else: 
        #the form failed validation, but show it anyway so the user can see error messages.
        #Don't make a new form to render on failed validation, or the error messages will be lost.
        return render(request, searchpage_template, {'form': form, 
                                                 'status_message':'Invalid search. Try agian.'})
  else:
    return render(request, searchpage_template, {'form':ScoresSearchForm() })
    #No status message when just loading the form.

