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

    #For search views, this should just point back to the main search page.
    def get(self, request, *args, **kwargs):
        return redirect(reverse('ss_viewer:multi-search')) 
   
    def post(self, request, *args, **kwargs):
        search_form = None 
        if len(request.POST.keys()) == 1:
            print "This is a download; rework the post."
            st = request.POST.keys()[0]      
            request.POST = json.loads(st)
 
        #get the 'Action' out of the post.
        if request.POST['action'] in ['Prev', 'Next']:
            oneDict = request.POST.dict()
            search_form = self.form_class(oneDict)
        else: 
            search_form = self.form_class(request.POST, request.FILES)

        if not search_form.is_valid() \
          and not request.POST['action'] == 'Download Results':
            context = {}
            errs = search_form.errors
            context['form_errors'] = \
               [ str(item) for one_error in errs.values() for item in one_error]

            context =  StandardFormset.handle_invalid_form(context)
            #just sets the status message...

            return HttpResponse(json.dumps(context), 
                            content_type="application/json",
                            status=400) 

        self.search_form = search_form
        form_data = self.search_form.cleaned_data

        if request.POST['action'] == 'Download Results':
            print "handling download!"
            #print "data from search form " + repr(self.search_form.cleaned_data)
            return self.handle_download(self.search_form.cleaned_data, request)
   
        search_request_params = Paging.get_paging_info_for_request(request, 
                                             form_data['page_of_results_shown']) 

        api_search_query = self.setup_api_search_query(form_data, request)


        #TODO: take the call to api_search_query.update(self.get_pvalues_from_form())
        #      out of individual search types.
        api_search_query.update( self.get_pvalue_directions_from_form() ) 

        api_search_query.update(
               {'from_result' :  search_request_params['search_result_offset']})


        #make a version of this that's not returning all the page stuff.
        shared_context = APIResponseHandler.handle_search(api_search_query,
                                                          self.api_action_name,
                                                          search_request_params)

        context = self.handle_paging_and_return_context(
                                                 self.search_form.cleaned_data,
                                                 search_request_params)
              
        context.update(shared_context)
        #print "context keys : " + repr(context.keys())

        #don't pass back ALL of the form data that was sent in.
        #This is only triggered by a whole file full of SNPids.
        if 'file_of_snpids' in context['form_data'].keys() and context['form_data']['file_of_snpids'] is not None:
           del context['form_data']['file_of_snpids'] 

        return HttpResponse(json.dumps(context), 
                            content_type="application/json") 

    def handle_paging_and_return_context(self, form_data,
                                                    search_request_params):
        form_data['page_of_results_shown'] =  \
                        search_request_params['page_of_results_to_display']
        self.search_form = self.form_class(form_data)
        context = { 'form_data' : self.search_form.data }
        return context

    def handle_download(self, form_data, request):
        #was setting search_params = form_data, but that's sending too much stuff in.
        search_params = self.handle_params_for_download(form_data)
        search_params.update(self.get_pvalues_from_form())
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
