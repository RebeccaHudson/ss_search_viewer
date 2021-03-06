import re
import copy
from ss_viewer.views.shared import APIResponseHandler
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.views.generic import View
from ss_viewer.views.shared import StandardFormset
from ss_viewer.views.shared import Paging
from ss_viewer.views.shared import StreamingCSVDownloadHandler
from ss_viewer.forms import SharedSearchControlsForm 
from django.http import HttpResponse
from django.conf import settings
import json

class GenericSearchView(View):
    template_name = 'ss_viewer/search-page.html'
    search_form = None 
    shared_search_controls_errors = None
    shared_search_controls_dict = None 
    api_search_query = None

    #For search views, this should just point back to the main search page.
    def get(self, request, *args, **kwargs):
        return redirect(reverse('ss_viewer:search')) 

    #Pass the request through without change if it's a download request.
    def check_for_download_request(self, request):
        if len(request.POST.keys()) == 1:
           st = request.POST.keys()[0]      
           request.POST = json.loads(st)
        return request 

    #try to flatten one more time...
    def setup_form_for_paging_or_download_request(self,request):
        newDict = None
        if request.POST['action'] in ['Prev', 'Next']:
            self.shared_search_controls_dict = copy.deepcopy(request.POST.dict())
            newDict = self.setup_form_for_paging_request(request)
        else: 
            self.shared_search_controls_dict = copy.deepcopy(request.POST)
            newDict = self.setup_form_for_download_request(request)

        #print "right before assignment: " + repr(post_dict_to_use)
        for one_field in ['sort_order', 'ic_filter']: 
            self.shared_search_controls_dict[one_field] =  \
              json.loads(self.shared_search_controls_dict[one_field])

        newDict = self.add_form_prefix_to_fields_for_search(newDict)  #is this still needed?
        self.search_form = self.form_class(newDict)

    # Don't call this for paging or download requests, it comes in with all the other keys.
    def setup_shared_search_controls_form(self, request):
        self.shared_search_controls_dict = request.POST.dict()['shared_controls']
        self.shared_search_controls_dict = json.loads(self.shared_search_controls_dict)

    #Used only for download and paging requests.
    def unpack_motif_ic_list(self, dict_as_given):
        motif_ic_str = dict_as_given['ic_filter']
        return {'ic_filter':  json.loads(motif_ic_str)}

    def setup_form_for_paging_request(self, request):
        d = request.POST.dict()  
        d.update(self.unpack_motif_ic_list(d))
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
        shared_control_values = {}
        shared_control_values.update(self.get_pvalues_from_form())
        shared_control_values.update(self.get_pvalue_directions_from_form() ) 
        shared_control_values.update(self.handle_sort_order() ) 
        shared_control_values.update(self.handle_ic_filter() )

        #any errors with these will be recorded in self.shared_search_control_errors
        if self.search_form.is_valid():
          form_data = self.search_form.cleaned_data  #query-type specific.
          self.api_search_query = self.setup_api_search_query(form_data)
          self.api_search_query.update(shared_control_values)


    def prepare_search_parameters(self, request):
        if 'page_of_results_shown' not in self.shared_search_controls_dict or\
          self.shared_search_controls_dict['page_of_results_shown'] == '':
            self.shared_search_controls_dict['page_of_results_shown'] = 0
 
        search_request_params = Paging.get_paging_info_for_request(request, 
                                     self.shared_search_controls_dict['page_of_results_shown']) 

        self.api_search_query.update(
               {'from_result' :  search_request_params['search_result_offset']})
        return search_request_params  

    def post(self, request, *args, **kwargs):
        request = self.check_for_download_request(request) 
        #rearranges the request if it's a download.

        self.shared_search_controls_errors = [] 

        #get the 'Action' out of the post; setup the form accordingly.
        if request.POST['action'] in ['Prev', 'Next', 'Download Results'] or\
             'jump' in  request.POST['action']:
            self.setup_form_for_paging_or_download_request(request)
        else: 
            #case when it's a basic (not paging or download) search
            self.setup_form_for_standard_request(request)

        #Can't pull query data off of the form if the form is not valid.
        self.pull_all_query_data_from_form()     #errors for shared controls should be
                                                 #made available by/after this line.
        if not self.search_form.is_valid() or \
               not len(self.shared_search_controls_errors) == 0:
            return self.handle_invalid_form()

        if request.POST['action'] == 'Download Results':
            return self.handle_download(request)
  
        #handle paging stuff. 
        search_request_params = self.prepare_search_parameters(request)

        shared_context = APIResponseHandler.handle_search(self.api_search_query,
                                                          self.api_action_name,
                                                          search_request_params)
        context = self.handle_paging_and_return_context(
                                                 self.search_form.cleaned_data,
                                                 search_request_params)
 
        context.update(shared_context)
        context['search_paging_info'] = json.dumps(context['search_paging_info'])
        context['form_data'] = json.dumps(context['form_data'])
        context['plot_source'] = json.dumps(context['plot_source'])

        template_path = 'ss_viewer/search_results.html' 
        context['tooltips'] = settings.ALL_TOOLTIPS
        return render(request, template_path, context)
 
    def handle_sort_order(self):
        sort_order = { }
        if 'sort_order' in self.shared_search_controls_dict.keys():
            sort_order['sort_order'] = self.shared_search_controls_dict['sort_order']
        return sort_order
 
    #Spit if this is empty. 
    def handle_ic_filter(self):
        ic_to_include = [] #contains 1, 2, 3, or 4
        ic_values = self.shared_search_controls_dict['ic_filter']
        if len(ic_values) == 0:
            #print "*************** recognized empty ic_filter values"
            msg = "No motif degeneracy levels are selected. Select at least one." 
            self.shared_search_controls_errors.append(msg)
        ic_dict = { 'ic_filter' : ic_values }
        return ic_dict
        

    #pull this out of the shared_search_controls form.
    #sets up form data to be passed back to the web view for paging.
    def handle_paging_and_return_context(self, form_data,
                                                    search_request_params):
        form_data['page_of_results_shown'] =  \
                        search_request_params['page_of_results_to_display']
        self.search_form = self.form_class(form_data)
        base_form_data = self.search_form.data
        base_form_data.update(self.api_search_query)
        context = { 'form_data' : base_form_data }
        return context

    def handle_download(self,  request):
        search_params = self.api_search_query
        return StreamingCSVDownloadHandler.streaming_csv_view(request, 
                                                               search_params, 
                                                               self.api_action_name)

    #Clean this up. Shorten it.
    def get_pvalue_directions_from_form(self):
        pvalue_directions = {}
        form_data = self.shared_search_controls_dict
        if 'pvalue_snp_direction' in form_data:
            pvalue_directions.update({'pvalue_snp_direction'  : 
                                       form_data['pvalue_snp_direction']})
        if 'pvalue_ref_direction' in form_data:
            pvalue_directions.update({'pvalue_ref_direction' : 
                                        form_data['pvalue_ref_direction']})
        return pvalue_directions

    def get_pvalues_from_form(self):
        #print "in get_pvalues_from_form " + repr(self.shared_search_controls_dict)
        pval_dict = {}
        for one_pval in ['rank', 'ref', 'snp']:
            k = '_'.join(['pvalue', one_pval])
            if k in self.shared_search_controls_dict and \
                    self.shared_search_controls_dict[k]:
                pval_dict[k] = self.shared_search_controls_dict[k]
            #print "pval_dict as given : " + str(pval_dict)

        if 'pvalue_rank' not in  pval_dict:
            msg = "No p-value SNP impact has been specified, \
                   specify at least p-value SNP impact to search."
            self.shared_search_controls_errors.append(msg)
        return pval_dict

    def handle_invalid_form(self):
        errs = self.search_form.errors
        context = {'form_errors': []}
 
        if len(errs) > 0:
            context['form_errors'].extend(
             [ str(item) for one_error in errs.values() for item in one_error])
          
        #print "form errors content right after assigning form errors " + \
        #   repr(context['form_errors'])      
  
        if len(self.shared_search_controls_errors) > 0: 
            context['form_errors'].extend(self.shared_search_controls_errors)
           
        #print "form errors content right after assigning shared controls errors " + \
        #   repr(context['form_errors'])      
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
