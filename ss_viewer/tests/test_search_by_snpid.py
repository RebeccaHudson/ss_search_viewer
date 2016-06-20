from django.test import TestCase
from django.core.urlresolvers import reverse
from ss_viewer.tests.scores_viewer_test_cases import ScoresViewerTestCase
import unittest
import os
import json

class SearchBySnpidTests(ScoresViewerTestCase):
    btn_action = "Search by SNPid" 
    def test_that_scores_list_loads_get(self):
       response = self.client.get(reverse('ss_viewer:snpid-search'), follow=True)
       self.assertTrue(response.context.__contains__('gl_search_form'))
       self.assertTrue(response.context.__contains__('snpid_search_form'))
       self.assertTrue(response.context.__contains__('status_message'))
       self.assertEqual(response.status_code, 200) 
       # if follow is not true, we just get the redirection status code
       response = self.client.get(reverse('ss_viewer:snpid-search'))
       self.assertEqual(response.status_code, 302)

    #we can only expect this test to pass if the requested snpids are actually in the database...
    #retain this code for testing when we actually expect matches to come out...
    def test_that_scores_list_loads_post(self):
      response = self.client.post(reverse('ss_viewer:snpid-search'),
              { 'raw_requested_snpids' : 'rs371194064 rs199706086 rs111200574',
                'pvalue_rank_cutoff' : 1,
                'action'             : self.btn_action })

      self.check_for_api_response_and_200_response_code(response)
      api_response_data = response.context['api_response']
      self.assertTrue(len(api_response_data)> 3)

      for data_row in api_response_data:
        fields_in_data_row = data_row.keys()
        self.check_for_expected_fields_in_scores_row(fields_in_data_row)

    def test_that_scores_list_post_rejects_an_invalid_form(self):
      #None of the form fields are filled out.
      response = self.client.post(reverse('ss_viewer:snpid-search'),
             { 'totally_invalid_field'  : 'har-dee-har-harr!',
                'action'             : self.btn_action })
      self.assertEqual(response.context.__contains__('status_message'), True)
      self.assertEqual(response.context['status_message'],'Invalid search. Try agian.')
      self.assertEqual(response.context['snpid_search_form'].is_valid(), False)


    def test_that_snpid_search_rejects_invalid_cutoffs(self):
      response = self.client.post(reverse('ss_viewer:snpid-search'),
              { 'raw_requested_snpids' : 'rs371194064 rs199706086 rs111200574',
                'pvalue_rank_cutoff' : -0.001,
                'action'             : self.btn_action })
      self.check_status_message(response, 'Invalid search. Try agian.')
      self.assertEqual(response.context['snpid_search_form'].is_valid(), False)

      response = self.client.post(reverse('ss_viewer:snpid-search'),
              { 'raw_requested_snpids' : 'rs371194064 rs199706086 rs111200574',
                'pvalue_rank_cutoff' : 1.001,
                'action'             : self.btn_action })
      self.check_status_message(response, 'Invalid search. Try agian.')
      self.assertEqual(response.context['snpid_search_form'].is_valid(), False)



    def test_that_scores_list_loads_post_for_no_matching_snpids(self):
      response = self.client.post(reverse('ss_viewer:snpid-search'),
             { 'raw_requested_snpids'  : 'rs111, rs1111111, rs11111111111111, rs1',
               'pvalue_rank_cutoff' : 0.05,
               'action'             : self.btn_action    })

      self.check_for_api_response_and_200_response_code(response)

      api_response_data = response.context['api_response']
      self.assertEqual(api_response_data, None)

      self.assertEqual(response.context.__contains__('status_message'), True)
      self.assertEqual(response.context['status_message'],
                                               'No matches for requested snpids' )


    def test_that_scores_list_loads_get(self):
         response = self.client.get(reverse('ss_viewer:snpid-search'), follow=True)

         self.assertTrue(response.context.__contains__('gl_search_form'))
         self.assertTrue(response.context.__contains__('snpid_search_form'))
         self.assertTrue(response.context.__contains__('status_message'))
         self.assertEqual(response.status_code, 200)   #302 redirection


         # if follow is not true, we just get the redirection status code
         response = self.client.get(reverse('ss_viewer:snpid-search'))
         self.assertEqual(response.status_code, 302)   #302 redirection


    def test_page_through_response_data(self):
         response = None
         url = reverse('ss_viewer:snpid-search')
         fpath = os.path.dirname(os.path.abspath(__file__))+'/tinysnp.txt'
         fp = open(fpath, 'r')
         base_request = {'pvalue_rank_cutoff' :0.6,
                         'file_of_snpids'     :fp,
                         'action'             : self.btn_action }
         response = self.client.post(url, base_request )

         #print "response from file input test: " +\
         #       str((dir(response.context['snpid_search_form'])))

         #print "drill into the form:: " +\
         #       str((response.context['snpid_search_form'].data['raw_requested_snpids']))

         snpids_scraped_out_of_file = \
                  response.context['snpid_search_form'].data['raw_requested_snpids']

         #print "snpids scraped " + repr(snpids_scraped_out_of_file)


         while response.context['search_paging_info']['show_next_btn'] is True:
              page_shown = response.context['snpid_search_form'].data['page_of_results_shown']
              next_page_request = \
                         {'pvalue_rank_cutoff'   :  0.6,
                         'raw_requested_snpids'  :  snpids_scraped_out_of_file, 
                         'action'                : 'Next',
                         'page_of_results_shown' :  page_shown 
                         }
              response = self.client.post(url, next_page_request)     
              print "status msg: " + response.context['status_message'] 
              print "items on page: " + str(len(response.context['api_response']))

 
    def test_that_file_input_works_for_snpid_search(self):
          response = None
          url = reverse('ss_viewer:snpid-search')
          fpath = os.path.dirname(os.path.abspath(__file__))+'/tinysnp.txt'
          fp = open(fpath, 'r')
          response = self.client.post(url,
                                      {'pvalue_rank_cutoff' :0.6,
                                       'file_of_snpids'     :fp,
                                       'action'             : self.btn_action })
          #print("response from file input test: " + str(response))      
          self.check_for_api_response_and_200_response_code(response)

          api_response_data = response.context['api_response'] 
          # this look like what it should be? self.assertEqual(len(api_response_data), 15)
          print "api response " + str(len(api_response_data))
          self.assertTrue(len(api_response_data) >= 10)

          for one_row in api_response_data:
              self.check_for_expected_fields_in_scores_row(one_row.keys())

          self.assertEqual(response.context.__contains__('status_message'), True)
          

