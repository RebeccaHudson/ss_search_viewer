import re
import copy
from ss_viewer.views.shared import APIResponseHandler
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.views.generic import View
from ss_viewer.views.shared import StandardFormset
from ss_viewer.views.shared import PValueDictFromForm
from ss_viewer.views.shared import Paging
from ss_viewer.views.shared import StreamingCSVDownloadHandler

from ss_viewer.forms import SharedSearchControlsForm 


from django.http import HttpResponse
import json

class GenericSearchView(View):
    template_name = 'ss_viewer/multi-searchpage.html'
    search_form = None 
    shared_search_controls_dict = None  #New!
    api_search_query = None

    #For search views, this should just point back to the main search page.
    def get(self, request, *args, **kwargs):
        return redirect(reverse('ss_viewer:multi-search')) 

    #pass the request through without change if it's a download request.
    def check_for_download_request(self, request):
        if len(request.POST.keys()) == 1:
           st = request.POST.keys()[0]      
           request.POST = json.loads(st)
        return request 

    def setup_form_for_paging_or_download_request(self,request):
        newDict = None
        #this might be were to put the shared_search_controls 
        print "\n\n\n  HEY: here's the form keys that are avaialbe right now:  " + repr(request.POST.dict().keys())
        self.shared_search_controls_dict = {} 
        for x in [ 'page_of_results_shown', 'ic_filter', 'sort_order', 'pvalue_snp', 'pvalue_ref', 'pvalue_rank', \
                    'pvalue_ref_direction' , 'pvalue_snp_direction' ]:
            self.shared_search_controls_dict[x] = request.POST.dict()[x]
            print "setting up key x w/ value " + str(request.POST.dict()[x])
        print "trying to setup the sort order properly : " + self.shared_search_controls_dict['sort_order'].__class__.__name__
        print "trying to setup the sort order properly : " + repr(self.shared_search_controls_dict['sort_order'])
        self.shared_search_controls_dict['sort_order'] =  json.loads(self.shared_search_controls_dict['sort_order'])
        print "trying to setup the sort order properly : " + self.shared_search_controls_dict['sort_order'].__class__.__name__
        print "trying to setup the sort order properly : " + repr(self.shared_search_controls_dict['sort_order'])
        #if shared_controls is in here, we can assign the shared_controls dict right here.
        if request.POST['action'] in ['Prev', 'Next']:
            newDict = self.setup_form_for_paging_request(request)
        else:
            newDict = self.setup_form_for_download_request(request)

        newDict = self.add_form_prefix_to_fields_for_search(newDict)
        print "newDict : " + repr(newDict)

        #The shared search controls will be pulled out either way.
        #No form prefixes to add to the shared search controls form.
        self.search_form = self.form_class(newDict)

    #TODO, finish this NEW function. Can we see the control values from here?
    #* Don't call this for paging requests.
    def setup_shared_search_controls_form(self, request):
        print "FOO -->> in setup_shared_search_controls_form:"
        print repr(request.POST.dict())
        self.shared_search_controls_dict = request.POST.dict()['shared_controls']
        self.shared_search_controls_dict = json.loads(self.shared_search_controls_dict)
        #pvalue_snp_cutoff, pvalue_ref_cutoff, and pvalue_rank_cutoff are all present
        #from the SharedSearchControls form at this point in the POST.
        #self.shared_search_controls_form = SharedSearchControlsForm(d)
        print "successfully created the SharedSearchControlsForm"

    def unpack_motif_ic_list(self, dict_as_given):
        motif_ic_str = dict_as_given['ic_filter']
        return {'ic_filter':  json.loads(motif_ic_str)}
        #dict_as_given will be modified in the calling method.

    def setup_form_for_paging_request(self, request):
        d = request.POST.dict()   #is motif_ic anywhere in the post?
        print "in setup_form_for_paging_request " + repr(d)
        d.update(self.unpack_motif_ic_list(d))
        #Not needed. self.setup_shared_search_controls_form(request)  #shared
        return d 

    def setup_form_for_download_request(self, request):
        d = copy.deepcopy(request.POST)
        d.update(self.unpack_motif_ic_list(d))
        return d
 
    #Not paging or download. 
    def setup_form_for_standard_request(self, request):
        self.search_form = self.form_class(request.POST, request.FILES)
        self.setup_shared_search_controls_form(request)

    #Must include some handling for shared_search_controls.
    def pull_all_query_data_from_form(self):
        form_data = self.search_form.cleaned_data
        self.api_search_query = self.setup_api_search_query(form_data)
        self.api_search_query.update(self.get_pvalues_from_form())
        self.api_search_query.update(self.get_pvalue_directions_from_form() ) 
        self.api_search_query.update(self.handle_sort_order() ) 
        ic_filter = self.handle_ic_filter()
        self.api_search_query.update(ic_filter)

    def prepare_search_parameters(self, request):
        print "self.shared_search_controls_dict " + repr(self.shared_search_controls_dict)
        #print "self.shared_search_controls_dict['page_of_results_shown'] " + repr(self.shared_search_controls_dict['page_of_results_shown'])
        if 'page_of_results_shown' not in self.shared_search_controls_dict or self.shared_search_controls_dict['page_of_results_shown'] == '':
            self.shared_search_controls_dict['page_of_results_shown'] = 0
 
        search_request_params = Paging.get_paging_info_for_request(request, 
                                     self.shared_search_controls_dict['page_of_results_shown']) 

        self.api_search_query.update(
               {'from_result' :  search_request_params['search_result_offset']})
        return search_request_params  

    def post(self, request, *args, **kwargs):
        request = self.check_for_download_request(request) 
        #rearranges the request if it's a download.

        #get the 'Action' out of the post; setup the form accordingly.
        if request.POST['action'] in ['Prev', 'Next', 'Download Results'] or\
             'jump' in  request.POST['action']:
            self.setup_form_for_paging_or_download_request(request)
        else: 
            #case when it's a basic (not paging or download) search
            self.setup_form_for_standard_request(request)
        if not self.search_form.is_valid(): 
            #consider hand-validating the shared_search_controls_dict instead 
            #  of relying on form validation. 
            return self.handle_invalid_form()

        #assigns and handles api_search_query.
        #skip this call if possible.
        print "can we skip the call that will pull the query data from the form?"
        self.pull_all_query_data_from_form()
              
        if request.POST['action'] == 'Download Results':
            return self.handle_download(request)
  
        #handle paging stuff. 
        search_request_params = self.prepare_search_parameters(request)
        #make a version of this that's not returning all the page stuff.

        shared_context = APIResponseHandler.handle_search(self.api_search_query,
                                                          self.api_action_name,
                                                          search_request_params)

        context = self.handle_paging_and_return_context(
                                                 self.search_form.cleaned_data,
                                                 search_request_params)
        context.update(shared_context)
        print "context before dumping back from post "  + repr(context.keys())
        print "form data keys "  + repr(context['form_data'].keys())
        #print "search paging info keys "  + repr(context['search_paging_info'].keys())
        print "full context " + repr(context['form_data'])
        return HttpResponse(json.dumps(context), 
                            content_type="application/json") 
 
    def handle_sort_order(self):
        sort_order = { }
        #if 'sort_order' in self.search_form.cleaned_data.keys():
        if 'sort_order' in self.shared_search_controls_dict.keys():
            sort_order['sort_order'] = self.shared_search_controls_dict['sort_order']
            #does this work ok?
            # may only need to json.loads once prior to here
            #sort_order['sort_order'] = json.loads(string_val)
        return sort_order
  
    def handle_ic_filter(self):
        ic_to_include = [] #contains 1, 2, 3, or 4
        #ic_values = self.search_form.cleaned_data['ic_filter']
        ic_values = self.shared_search_controls_dict['ic_filter']
        ic_dict = { 'ic_filter' : ic_values }
        #print "********************************* " + repr(ic_values) + "********************"
        return ic_dict
        

    #pull this out of the shared_search_controls form.
    #sets up form data to be passed back to the web view for paging.
    def handle_paging_and_return_context(self, form_data,
                                                    search_request_params):
        form_data['page_of_results_shown'] =  \
                        search_request_params['page_of_results_to_display']
        self.search_form = self.form_class(form_data)
        base_form_data = self.search_form.data
        print "in handle_paging_and_return_context keys in base form data "  + repr(base_form_data.keys())
        print "adding keys from api search query: " + repr(self.api_search_query.keys())
        base_form_data.update(self.api_search_query)
        #context = { 'form_data' : self.search_form.data }
        context = { 'form_data' : base_form_data }
        return context

    def handle_download(self,  request):
        search_params = self.api_search_query
        return StreamingCSVDownloadHandler.streaming_csv_view(request, 
                                                               search_params, 
                                                               self.api_action_name)
    def get_pvalue_directions_from_form(self):
        pvalue_directions = {}
        #form_data = self.search_form.cleaned_data
        #form_data = self.shared_search_controls_form.cleaned_data
        form_data = self.shared_search_controls_dict
        if 'pvalue_snp_direction' in form_data:
            pvalue_directions.update({'pvalue_snp_direction'  : 
                                       form_data['pvalue_snp_direction']})
        if 'pvalue_ref_direction' in form_data:
            pvalue_directions.update({'pvalue_ref_direction' : 
                                        form_data['pvalue_ref_direction']})
        return pvalue_directions

    def get_pvalues_from_form(self):
        pvalues_for_search = {}
        pvalue_dict = None
        pvalue_dict = PValueDictFromForm.get_pvalues_from_dict(self.shared_search_controls_dict) 
        #No: pvalue_dict = PValueDictFromForm.get_pvalues_from_form(self.shared_search_controls_form) 
        #switching over to use SharedSearchControlsForm
        pvalues_for_search['pvalue_rank'] = pvalue_dict['pvalue_rank_cutoff']
        if 'pvalue_ref_cutoff' in pvalue_dict:
            pvalues_for_search.update({'pvalue_ref'  : pvalue_dict['pvalue_ref_cutoff']})
        if 'pvalue_snp_cutoff' in pvalue_dict:
            pvalues_for_search.update({'pvalue_snp'  : pvalue_dict['pvalue_snp_cutoff']})
        return pvalues_for_search

    def handle_invalid_form(self):
        errs = self.search_form.errors
        context = { 'form_errors' :
                    [ str(item) for one_error in errs.values() for item in one_error]
                  }
        context =  StandardFormset.handle_invalid_form(context)
        return HttpResponse(json.dumps(context), 
                        content_type="application/json",
                        status=400) 

    def add_form_prefix_to_fields_for_search(self, oneDict):
        newDict = {}
        for onekey in oneDict.keys():
            newkey = '-'.join([self.form_class.prefix, onekey])
            newDict[newkey] = oneDict[onekey]
        return newDict
