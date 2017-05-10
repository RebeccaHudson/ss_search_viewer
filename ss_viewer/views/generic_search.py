import re
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

from django.http import HttpResponse
import json

class GenericSearchView(View):
    template_name = 'ss_viewer/multi-searchpage.html'
    search_form = None 
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
        if request.POST['action'] in ['Prev', 'Next']:
            newDict = self.setup_form_for_paging_request(request)
        else:
            newDict = self.setup_form_for_download_request(request)

        newDict = self.add_form_prefix_to_fields_for_search(newDict)
        self.search_form = self.form_class(newDict)

    def setup_form_for_paging_request(self, request):
        print "setup for paging request.." 
        return request.POST.dict()

    def setup_form_for_download_request(self, request):
        return request.POST 
 
    #Not paging or download. 
    def setup_form_for_standard_request(self, request):
        self.search_form = self.form_class(request.POST, request.FILES)

    def pull_all_query_data_from_form(self):
        form_data = self.search_form.cleaned_data
        self.api_search_query = self.setup_api_search_query(form_data)
        self.api_search_query.update(self.get_pvalues_from_form())
        self.api_search_query.update(self.get_pvalue_directions_from_form() ) 
        self.api_search_query.update(self.handle_sort_order() ) 

    def prepare_search_parameters(self, request):
        search_request_params = Paging.get_paging_info_for_request(request, 
                                     self.search_form.cleaned_data['page_of_results_shown']) 
        self.api_search_query.update(
               {'from_result' :  search_request_params['search_result_offset']})
        return search_request_params  

    def post(self, request, *args, **kwargs):
        request = self.check_for_download_request(request) 
        #rearranges the request if it's a download.

        #get the 'Action' out of the post; setup the form accordingly.
        if request.POST['action'] in ['Prev', 'Next', 'Download Results']:
            self.setup_form_for_paging_or_download_request(request)
        else: 
            #case when it's a basic (not paging or download) search
            self.setup_form_for_standard_request(request)

        if not self.search_form.is_valid():
            return self.handle_invalid_form()

        #assigns and handles api_search_query.
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
        return HttpResponse(json.dumps(context), 
                            content_type="application/json") 
 
    def handle_sort_order(self):
        sort_order = { }
        if 'sort_order' in self.search_form.cleaned_data.keys():
            string_val = self.search_form.cleaned_data['sort_order']
            sort_order['sort_order'] = json.loads(string_val)
        return sort_order

    def handle_paging_and_return_context(self, form_data,
                                                    search_request_params):
        form_data['page_of_results_shown'] =  \
                        search_request_params['page_of_results_to_display']
        self.search_form = self.form_class(form_data)
        context = { 'form_data' : self.search_form.data }
        return context

    def handle_download(self,  request):
        search_params = self.api_search_query
        return StreamingCSVDownloadHandler.streaming_csv_view(request, 
                                                               search_params, 
                                                               self.api_action_name)
    def get_pvalue_directions_from_form(self):
        pvalue_directions = {}
        form_data = self.search_form.cleaned_data
        if 'pvalue_snp_direction' in form_data:
            pvalue_directions.update({'pvalue_snp_direction'  : 
                                       form_data['pvalue_snp_direction']})
        if 'pvalue_ref_direction' in form_data:
            pvalue_directions.update({'pvalue_ref_direction' : 
                                        form_data['pvalue_ref_direction']})
        return pvalue_directions

    def get_pvalues_from_form(self):
        pvalues_for_search = {}
        pvalue_dict = PValueDictFromForm.get_pvalues_from_form(self.search_form) 
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
