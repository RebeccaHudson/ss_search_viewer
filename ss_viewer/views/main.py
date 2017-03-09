from django.shortcuts import render
from django.http import HttpResponse
import json
import os
from ss_viewer.views.shared import MotifPlottingData

def index(request):
  return HttpResponse("Try another url, like :ss_viewer/multi-search.")

def test_svg_plots(request):
    name_of_template  =  'ss_viewer/show_test_plot.html' 
    path_to_tests = '/test_data/plotsToTest.json'
    testData = None
    fpath = os.path.dirname(os.path.dirname(__file__)) + path_to_tests
    with open(fpath,  'r') as f:
        testjson = json.load(f)
        testdata = testjson['hits']
        print "testjson hits " + str(testdata.keys())
        testdata2 = testdata['hits'][2]['_source']
        print "testjson2 hits " + str(testdata2.keys())

    motif = testdata2['motif']   
    motifMap = MotifPlottingData()
    plot_id_string = 'MA0002.2_rs538221432_T'

    motif_data = motifMap.lookup_motif_data(motif)
    print "motif data : " + str(motif_data)

    context =  {'dynamic_svg_data' : 'scooby doo',
                 "happy_data" : json.dumps(testdata2),
                 "motif_data" : json.dumps(motifMap.lookup_motif_data(motif)) }
                    
    return render(request, name_of_template, context)

def help_page(request):
    help_page_template = 'ss_viewer/help-page.html'
    context = {}
    return render(request, help_page_template, context) 

def faq_page(request):
    faq_page_template = 'ss_viewer/faq.html'
    context = {}
    return render(request, faq_page_template, context) 

def home_page(request):
    home_page_template = 'ss_viewer/happyhome.html'
    context = {}
    return render(request, home_page_template, context)

