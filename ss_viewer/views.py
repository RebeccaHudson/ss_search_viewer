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

def get_scores_for_list(request):
  context_to_pass = { }
  if request.method == 'POST':
    raw_snpids = request.POST.get('requested_snpids')
    snpid_list = extract_snpids_from_textfield(raw_snpids)
    api_url = setup_api_url('search')
    req_headers = { 'content-type' : 'application/json' }
    api_response  = requests.post(api_url, 
                                json=snpid_list, headers=req_headers)
    context_to_pass['api_response'] = json.loads(api_response.text)
    context_to_pass['holdover_snpids'] = ", ".join(snpid_list)
  return render(request, 'ss_viewer/searchpage.html', context_to_pass )

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
  if file_pointer is None:
    print "no file pointer" 
    return None
  build_a_str = ""
  for chunk in file_pointer.chunks():
    build_a_str +=  chunk 
    return build_a_str

def xxx_get_scores_for_list(request):
  searchpage_template = 'ss_viewer/alt-searchpage.html'
  context_to_pass = { }
  if request.method == 'POST':
    form = ScoresSearchForm(request.POST, request.FILES)
    if form.is_valid():
       file_stuff = handle_uploaded_file(request.FILES.get('file_of_snpids'))
       snpid_list = extract_snpids_from_textfield(form.cleaned_data['raw_requested_snpids'])
       api_response = requests.post( setup_api_url('search'), 
             json=snpid_list, headers={ 'content-type' : 'application/json' })

       context = { 'api_response'  :  json.loads(api_response.text), 
                   'holdover_snpids': ", ".join(snpid_list),
                   'form' : ScoresSearchForm({'raw_requested_snpids':", ".join(snpid_list)})
                 }
       return render(request, searchpage_template, context )
    else: 
        #the form failed validation, but show it anyway so the user can see error messages.
        #Don't make a new form to render on failed validation, or the error messages will be lost.
        return render(request, searchpage_template, {'form': form })
  else:
    return render(request, searchpage_template, {'form':ScoresSearchForm() })

