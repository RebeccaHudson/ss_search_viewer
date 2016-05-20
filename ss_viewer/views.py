from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.conf import settings
import requests
import json
import re

from .forms import SearchBySnpidForm  #replaces ScoresSearchForm

from .forms import SearchByGenomicLocationForm

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


def setup_api_url(api_function, snpid=None):
  hostinfo = settings.API_HOST_INFO 
  host_w_port = ':'.join([ hostinfo['host_url'], hostinfo['host_port'] ] )
  url_arglist =  [ hostinfo['api_root'], api_function] 
  if snpid:
    url_arglist.append(snpid)
  url_args = '/'.join(url_arglist) 
  url = host_w_port + "/" + url_args  + "/"
  return url


def extract_snpids_from_textfield(text):
  gex = re.compile('(rs[0-9]+)', re.MULTILINE)  
  list_of_snpids = gex.findall(text)
  return list_of_snpids


def clean_and_validate_snpid_text_input(text_input):
  snpids = extract_snpids_from_textfield(text_input)
  deduped_snpids = list(set(snpids))  #don't allow any duplicate requests.
  if len(deduped_snpids) == 0:  
    raise forms.ValidationError("No snpids have been included")  
  return deduped_snpids


# Either by textarea or by file, snpid search form is not 
# valid unless one of these is present 
def get_snpid_list_from_form(request, form):
  form_snpids = form.cleaned_data.get('raw_requested_snpids')
  #remove the data in there.
  if form_snpids:
    return clean_and_validate_snpid_text_input(form_snpids)
  else:
    file_pointer = request.FILES.get('file_of_snpids')
    text_in_file = file_pointer.read()   # TODO: read in chunks rather than all at once. 
    return clean_and_validate_snpid_text_input(text_in_file) 


def setup_context_for_snpid_search_results(api_response, snpid_list):
  status_message = ""; response_json = None

  if api_response.status_code == 204:
    status_message = "No matches for requested snpids" 
  else:
    count_of_requested_snpids = len(snpid_list)
    status_message = "Retrieved data for {0} out of {1} requested snpids.".format(
             66666,  count_of_requested_snpids)

    response_json = json.loads(api_response.text)

  context = { 'api_response'     :  response_json,
              'status_message'    :  status_message,
              'holdover_snpids'   :  ", ".join(snpid_list),
              'snpid_search_form' :  SearchBySnpidForm({'raw_requested_snpids':", ".join(snpid_list)}),
              'gl_search_form'    :  SearchByGenomicLocationForm()
            }
  return context


def handle_search_by_snpid(request):
  if request.method == 'GET':
    return redirect(reverse('ss_viewer:multi-search'))

  if request.method == 'POST':
    searchpage_template = 'ss_viewer/multi-searchpage.html'  
    snpid_search_form = SearchBySnpidForm(request.POST, request.FILES)
    gl_search_form = SearchByGenomicLocationForm()
    status_message = ""    
    if not snpid_search_form.is_valid():
       return render(request, 
                     searchpage_template, 
                     {'snpid_search_form': snpid_search_form, 
                      'gl_search_form' : gl_search_form,                
                      'status_message':'Invalid search. Try agian.'})
    #if execution reaches this point, the form is valid.
    snpid_list = None
    try:
      snpid_list = get_snpid_list_from_form(request, snpid_search_form)
    except forms.ValidationError:
      status_message = "No properly formatted SNPids in the text."           
      return render(request, 
                    searchpage_template,
                    {'snpid_search_form': SearchBySnpidForm(),
                     'gl_search_form'   : SearchByGenomicLocationForm(),
                     'status_message'   : status_message })

    api_response = requests.post( setup_api_url('snpid-search'), 
             json=snpid_list, headers={ 'content-type' : 'application/json' })

    context = setup_context_for_snpid_search_results(api_response, snpid_list) 

    return render(request, searchpage_template, context )






#The above function 'get_scores_for_list' should actually be called
#handle search by genomic location.. 
#this should only handle POST
def handle_search_by_genomic_location(request):
  if request.method == 'GET':
    return redirect(reverse('ss_viewer:multi-search'))

  if request.method == 'POST': 
    print("here is the request: ")
    print(dir(request._post))
    print(str(request._post))
    searchpage_template = 'ss_viewer/multi-searchpage.html'  
    gl_search_form = SearchByGenomicLocationForm(request.POST)  #no files in here...
   
    status_message = ""
    if gl_search_form.is_valid():
      #status_message = "This form appears to be valid."

      print("cleaned data" + str(gl_search_form.cleaned_data) )
      form_data = gl_search_form.cleaned_data
      specified_region = { 'chromosome': form_data['selected_chromosome'],
                           'start_pos' : form_data['gl_start_pos'], 
                           'end_pos'   : form_data['gl_end_pos']   }
 
      api_response = requests.post( setup_api_url('search-by-gl'), 
             json=specified_region, headers={ 'content-type' : 'application/json' })
      response_json = json.loads(api_response.text)

      if len(response_json) == 0:
        status_message = 'No matching rows from the API'
      else:
        status_message = 'Got ' + str(len(response_json)) + ' rows back from API.'
     

      status_message += str(specified_region) 
      new_form = SearchByGenomicLocationForm(form_data)
      #TODO: what other context do we actually need here?
      #return the original form because we want to have the old data carry over. 
      return render(request, searchpage_template, { 'api_response' : response_json,
                                                    'gl_search_form': new_form, 
                                                    'snpid_search_form' : SearchBySnpidForm(),
                                                    'holdover_gl_region': specified_region,
                                                    'status_message' : status_message})                                              
       # Will I have to include the specified region into an argument to a new SearchForm
       # in order for the values to holdover?
    else:
       status_message = "This form is apparently not valid."
       return render(request, searchpage_template, 
                        { 'gl_search_form'    : gl_search_form,
                          'snpid_search_form' : SearchBySnpidForm(),
                          'status_message'   : status_message     
                        })



#Def this is the actual multi-search page, this handles the GET.
def show_multisearch_page(request):
  searchpage_template = 'ss_viewer/multi-searchpage.html'  
  status_message = "Enter genomic location info."
  gl_search_form = SearchByGenomicLocationForm()
  snpid_search_form = SearchBySnpidForm()
  context = { 'gl_search_form'    : gl_search_form, 
              'snpid_search_form' : snpid_search_form,
              'status_message'    : status_message }   
  return render(request, searchpage_template, context)











