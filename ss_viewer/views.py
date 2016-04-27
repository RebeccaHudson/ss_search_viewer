from django.shortcuts import render
from django.http import HttpResponse
import requests
import json

#found at the URL: ss_viewer
def index(request):
  return HttpResponse("This is a basic response")



#returns one snp from the API
#specify the snpid in the URL
def one_snp_detail(request, snpid_numeric):
  
  #the requests library probably has a cleaner, happier way to do this.
  #hardurl = 'http://0.0.0.0:8002/api_v0/one-scores-snpid/rs571194783'
  api_host_url = 'http://0.0.0.0'
  api_host_port = '8005'
  host_w_port = [ api_host_url, api_host_port]

  api_root_url = 'api_v0'
  api_function = 'one-scores-snpid'
  snpid = 'rs' + snpid_numeric
  url_args = [ api_root_url, api_function, snpid ]

  host_w_port = ':'.join(host_w_port)
  url_args = '/'.join(url_args)
  url = host_w_port + "/" + url_args + "/" 

  print("url = " + url) 
  
  r = requests.get(url)
  return HttpResponse(r.text)


def get_snp_list(request):
  pass




