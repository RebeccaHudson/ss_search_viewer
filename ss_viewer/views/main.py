from django.shortcuts import render
from django.http import HttpResponse
import json
import os

def index(request):
  return HttpResponse("Try another url, like :ss_viewer/multi-search.")

def test_svg_plots(request):
    name_of_template  =  'ss_viewer/show_test_plot.html' 
    test_plot_dir = '/test_data/'
    plots_to_test = ['shorter_test_plot.json', 'normal_test_plot.json']
    test_data = {}
    #load up each file of test data.
    for one_plot in plots_to_test:
        path = '/'.join([test_plot_dir, one_plot])
        fpath = os.path.dirname(os.path.dirname(__file__)) + path
        with open(fpath,  'r') as f:
            dict_key = one_plot.replace('.json', '')
            test_data[dict_key] = json.dumps(json.load(f))
    #get a dictionary.
    print "test data: " + repr(test_data)

    #motif_data is now included.
    context = {}
                
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

def about_page(request):
    about_page_template = 'ss_viewer/about_page.html'
    context = {}
    return render(request, about_page_template, context)
