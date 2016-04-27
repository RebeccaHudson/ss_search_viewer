from django.shortcuts import render
from django.http import HttpResponse

def index(request):
  return HttpResponse("This is a basic response")

# Create your views here.
