from django.test import TestCase
from django.core.urlresolvers import reverse
import unittest
import json

class ScoresViewerTestCase(TestCase):

    def  page_through_request_data(self, url, base_request, form_name):
        response = None
        response = self.client.post(url, base_request )
        print "\n\nresponse from search form" + repr(response.context)
        while response.context['search_paging_info']['show_next_btn'] is True:
            page_shown = response.context[form_name].data['page_of_results_shown']
  
            base_request.update(
                   { 'action'                : 'Next',
                  'page_of_results_shown' :  page_shown })
            response = self.client.post(url, base_request)
            print "status msg: " + response.context['status_message']


    def check_that_response_contains_expected_forms(respone):
        #for one_form in [ 'gl_search_form', 'snpid_search_form' ]
        self.assertTrue(response.context.__contains__('gl_search_form'))
        self.assertTrue(response.context.__contains__('snpid_search_form'))
        # Add additional forms above.
        self.assertTrue(response.context.__contains__('status_message'))
        self.assertEqual(response.status_code, 200)


    def check_for_expected_fields_in_scores_row(self, data_fields_in_one_row):
        expected_fields = [u'motif_len', u'snp_end', u'trans_factor',  u'log_lik_ref', u'snpid', u'motif', u'log_lik_ratio', u'ref_strand', u'ref_start', u'snp_start', u'snp_strand', u'ref_end', u'log_enhance_odds', u'log_reduce_odds', u'log_lik_snp', u'pval_ref', u'pval_snp', u'pval_cond_ref', u'pval_cond_snp', u'pval_diff', u'pval_rank', u'chr', u'pos' ]
        # TODO this could be much better
        matching_fields = list(set(data_fields_in_one_row).intersection(expected_fields))
        self.assertEqual(len(expected_fields), len(matching_fields))

    #this means the api returned something and response is OK. very common.
    def check_for_api_response_and_200_response_code(self, response):
        self.assertEqual(response.context.__contains__('api_response'), True)
        self.assertEqual(response.status_code, 200) 

    def check_status_message(self, response, expected_message):
      self.assertTrue(response.context.__contains__('status_message'))
      self.assertEqual(response.context['status_message'], expected_message)
