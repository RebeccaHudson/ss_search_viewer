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

class GenericAjaxySearchView(View):
    template_name = 'ss_viewer/multi-searchpage.html'
    search_form = None 

    #For search views, this should just point back to the main search page.
    def get(self, request, *args, **kwargs):
        return redirect(reverse('ss_viewer:multi-search')) 
   
    def post(self, request, *args, **kwargs):
        print "GenericAjaxySearchView is called..."
        search_form = None 

        #get the 'Action' out of the post.
        if request.POST['action'] in ['Prev', 'Next']:
            oneDict = request.POST.dict()
            #just passing in stored values..
            #oneDict = self.copy_hidden_fields_into_form_data(oneDict)
            search_form = self.form_class(oneDict)
        else: 
            search_form = self.form_class(request.POST, request.FILES)

        if not search_form.is_valid() \
          and not request.POST['action'] == 'Download Results':
            #context = StandardFormset.dict_based_setup_formset_context(\
            #                              {self.form_name_in_context:search_form})
            context = {}
            errs = search_form.errors
            print "form errors! " + repr(errs)
            context['form_errors'] = \
               [ str(item) for one_error in errs.values() for item in one_error]

            context =  StandardFormset.ajaxy_handle_invalid_form(context)
            #just sets the status message...
            return HttpResponse(json.dumps(context), 
                            content_type="application/json",
                            status=400) 

        self.search_form = search_form
        form_data = self.search_form.cleaned_data

        #TODO: find a way to sidestep validation for Prev, Next, and Download. 
        #EG: would I just call 'data' or something?
        if request.POST['action'] == 'Download Results':
            return self.handle_download(self.search_form.cleaned_data, request)
   
        #don't get it out of the form data? We are not scraping the form data for this.
        search_request_params = Paging.get_paging_info_for_request(request, 
                                             form_data['page_of_results_shown']) 

        api_search_query = self.setup_api_search_query(form_data, request)
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
        print "context keys : " + repr(context.keys())
        #can I still get the info for the form? AS WELL AS adding a rendered template?
        #does the rendered templatel appear under the test_template key?

        #setup a template for the search results portion of the page; 
        #  pass the context into this template, then render that template
        # back to the AJAX request. Then use JS to append that to the DOM.
        #return render(request, 'ss_viewer/multi-searchpage.html',  context)
        #do search results come through without changing any logic?
        return HttpResponse(json.dumps(context), 
                            content_type="application/json") 

    def handle_paging_and_return_context(self, form_data,
                                                    search_request_params):
        #may not need to actually use this anymore.
        form_data = self.copy_valid_form_data_into_hidden_fields(form_data)
        form_data['page_of_results_shown'] =  \
                        search_request_params['page_of_results_to_display']
        self.search_form = self.form_class(form_data)
        #Do not include the forms in the context with the results.
        #context = StandardFormset.dict_based_setup_formset_context(
        #                           {self.form_name_in_context:self.search_form})
        #May have to PUSH THE json values into the form whose data was submitted.
        context = { 'form_data' : self.search_form.data }
        #Where do we put the paging info into the 'search 
        return context

    def handle_download(self, form_data, request):
        prev_search_params = self.handle_params_for_download(form_data)
        if form_data['prev_search_pvalue_ref_cutoff'] is not None:
               prev_search_params.update(
                {'pvalue_ref'  : form_data['prev_search_pvalue_ref_cutoff']})
        if form_data['prev_search_pvalue_snp_cutoff'] is not None:
               prev_search_params.update(
                {'pvalue_snp'  : form_data['prev_search_pvalue_snp_cutoff']})
        return StreamingCSVDownloadHandler.streaming_csv_view(request, 
                                                               prev_search_params, 
                                                               self.api_action_name)
    def get_pvalues_from_form(self):
        pvalues_for_search = {}
        pvalue_dict = PValueDictFromForm.get_pvalues_from_form(self.search_form) 
        pvalues_for_search['pvalue_rank'] = pvalue_dict['pvalue_rank_cutoff']
        if 'pvalue_ref_cutoff' in pvalue_dict:
            pvalues_for_search.update({'pvalue_ref'  : pvalue_dict['pvalue_ref_cutoff']})
        if 'pvalue_snp_cutoff' in pvalue_dict:
            pvalues_for_search.update({'pvalue_snp'  : pvalue_dict['pvalue_snp_cutoff']})
        return pvalues_for_search

    #The next 3 methods are for copying data to and from hidden form fields to
    #maintain consistency between pages of search results and Downloads.
    def get_list_of_fields_to_copy(self):
        return [ onefield for onefield in self.form_class.base_fields.keys() \
                if  not re.match("^prev_search", onefield) ]

    def copy_valid_form_data_into_hidden_fields(self, form_data):
        for form_field in self.get_list_of_fields_to_copy():
            if form_field in form_data:
                form_data['prev_search_' + form_field] = form_data[form_field]
        return form_data
 
    def copy_hidden_fields_into_form_data(self, form_data):
        for form_field in self.get_list_of_fields_to_copy():
            if 'prev_search_' + form_field in form_data:
                form_data[form_field]  = form_data['prev_search_' + form_field]
        return form_data
