from django.shortcuts import render
from django.http import HttpResponse
import json
import os
from ss_viewer.views.shared import MotifPlottingData

def index(request):
  return HttpResponse("Try another url, like :ss_viewer/multi-search.")

#
def test_svg_plots(request):
    name_of_template  =  'ss_viewer/show_test_plot.html' 
    #path_to_tests = '/test_data/plotsToTest.json'
    test_plot_dir = '/test_data/'
    plots_to_test = ['shorter_test_plot.json', 'normal_test_plot.json']
    test_data = {}
    #load up each file of test data.
    for one_plot in plots_to_test:
        path = '/'.join([test_plot_dir, one_plot])
        #fpath = os.path.dirname(os.path.dirname(__file__)) + path_to_tests
        fpath = os.path.dirname(os.path.dirname(__file__)) + path
        with open(fpath,  'r') as f:
            #testjson = json.load(f)
            #testdata = testjson['hits']
            dict_key = one_plot.replace('.json', '')
            test_data[dict_key] = json.dumps(json.load(f))
            #testdata = testjson
            #print "testjson hits " + str(testdata.keys())
            #testdata2 = testdata['hits'][2]['_source']
            #print "testjson2 hits " + str(testdata2.keys())
    #get a dictionary.
    print "test data: " + repr(test_data)
    #now included w/ the test data. motif = testdata2['motif']   
    #motifMap = MotifPlottingData()
    #plot_id_string = 'MA0002.2_rs538221432_T'
    #motif_data = motifMap.lookup_motif_data(motif)
    #print "motif data : " + str(motif_data)

    #motif_data is now included.
    context = {}# { 'dynamic_svg_data' : 'scooby doo',
                # "happy_data" : json.dumps(testdata2),
                # "motif_data" : json.dumps(motifMap.lookup_motif_data(motif)) }
    context.update(test_data)
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
    home_page_template = 'ss_viewer/home_page.html'
    context = {}
    return render(request, home_page_template, context)

