from django.test import TestCase
from django.core.urlresolvers import reverse
import unittest
import json
"""
 Since the goal of this application is to interact with the rsss_api,
 these tests interact with the live, (non-test) version of this api.
 Make sure that the api_v0 app in the rss_api project is running on 
 the expected port before expecting these tests to pass.
"""



#Check that views load up and that we get status codes that make sense.
#TODO inspect content/context information about what is going into these views.
class OneScoresRowViewDetailTests(TestCase):
  #This will have the expecetd field names hardcoded. 
  #Change that here when the time comes to add new fields.
  def check_for_expected_fields_in_scores_row(self, data_fields_in_one_row):
      expected_fields = [u'motif_len', u'snp_end', u'log_lik_ref', u'snpid', u'motif', u'log_lik_ratio', u'ref_strand', u'ref_start', u'snp_start', u'snp_strand', u'ref_end', u'log_enhance_odds', u'log_reduce_odds', u'log_lik_snp', u'pval_ref', u'pval_snp', u'pval_cond_ref', u'pval_cond_snp', u'pval_diff', u'pval_rank', u'chr', u'pos' ]
      # TODO this could be much better
      matching_fields = list(set(data_fields_in_one_row).intersection(expected_fields))
      self.assertEqual(len(expected_fields), len(matching_fields))
       
  def test_that_index_view_loads(self):
    response = self.client.get(reverse('ss_viewer:index'))
    self.assertEqual(response.status_code, 200)
    
#TODO: grab a couple of SNPs from the actual, live DB to avoid having to have
#these hardcoded. It seems like many of these aren't in there?
  def test_that_snp_detail_loads(self):
    #consider making it a random id?
    numb = 145599635 
    response = self.client.get(reverse('ss_viewer:one-snp-detail', args=(numb,)))
    #print("context " + response.context)
    #api_response = response.context.flatten().get('api_response') 
    #print("The api told us this: " + str(api_response))
    print("response: " + str(response))
    self.assertEqual(len(response_json), 1)
    # This is an unused oddball function. Should probably remove this.
    #self.check_for_expected_fields_in_scores_row(response_json[0].keys())
    print("response: " + str(response.content))
    self.assertEqual(response.status_code, 200)
    #not sure what else is meaningful to test here, except that the views load.
 
#  def test_that_scores_list_loads_post(self):
#    response = self.client.post(reverse('ss_viewer:search'),
#            { 'requested_snpids' :  '"rs376997626", "rs575624833", "rs189241347"]' })
#    #Since the snpids are parsed out with a regular expression, we don't have to 
#    #insist on a specific format..
#    self.assertEqual(response.context.flatten().has_key('api_response'), True)
#    api_response_data = response.context.flatten()['api_response']
#    self.assertEqual(len(api_response_data), 3) #asked for 3 rows of data
#    for data_row in api_response_data:
#      fields_in_data_row = data_row.keys()
#      self.check_for_expected_fields_in_scores_row(fields_in_data_row)
#    self.assertEqual(response.status_code, 200)


  #we can only expect this test to pass if the requested snpids are actually in the database...
  #retain this code for testing when we actually expect matches to come out...
  def test_that_scores_list_loads_post(self):
    response = self.client.post(reverse('ss_viewer:snpid-search'),
            { 'raw_requested_snpids' : 'rs371194064 rs199706086 rs111200574' })

    self.assertTrue(response.context.flatten().has_key('api_response'))
    api_response_data = response.context.flatten()['api_response']
    self.assertEqual(len(api_response_data), 3)

    for data_row in api_response_data:
      fields_in_data_row = data_row.keys()
      print("one row fields:  " + str(fields_in_data_row))
      self.check_for_expected_fields_in_scores_row(fields_in_data_row)

    self.assertEqual(response.status_code, 200)

  #there should be different combinations of inputs that make it spit. 
  #test as many of those here as possbile.
  def test_that_scores_list_post_rejects_an_invalid_form(self):
    #None of the form fields are filled out.
    response = self.client.post(reverse('ss_viewer:snpid-search'),
           { 'totally_invalid_field'  : 'har-dee-har-harr!' })
    self.assertEqual(response.context.flatten().has_key('status_message'), True)
    self.assertEqual(response.context.flatten()['status_message'],'Invalid search. Try agian.')
    self.assertEqual(response.context['snpid_search_form'].is_valid(), False)
    


    #names of the fields in the form.
    #response = self.client.post(reverse('ss_viewer:search'),
    #        { 'requested_snpids' :  '"rs376997626", "rs575624833", "rs189241347"]' })



  def test_that_scores_list_loads_post_for_no_matching_snpids(self):
    response = self.client.post(reverse('ss_viewer:snpid-search'),
           { 'raw_requested_snpids'  : 'rs111, rs1111111, rs11111111111111, rs1' })
           #banking on these being fake

    self.assertEqual(response.context.flatten().has_key('api_response'), True)
    api_response_data = response.context.flatten()['api_response']
    self.assertEqual(api_response_data, None)

    self.assertEqual(response.context.flatten().has_key('status_message'), True)
    self.assertEqual(response.context.flatten()['status_message'],
                                             'No matches for requested snpids' )

    self.assertEqual(response.status_code, 200) 
    #no content from API, but success from ss_viewer.





  def test_that_scores_list_loads_get(self): 
     response = self.client.get(reverse('ss_viewer:snpid-search'))
     self.assertEqual(response.status_code, 200)
     #not expecting a status message; there should be a form in the context though.







  def test_gl_search_returns_some_data(self):
    response = self.client.post(reverse('ss_viewer:gl-region-search'),
                                { 'selected_chromosome'  : 'ch1', 
                                  'gl_start_pos'         : 12214,
                                  'gl_end_pos'           : 12314  })
    self.assertTrue(response.context.flatten().has_key('api_response'))
   # print("response " + str(response.context.flatten().keys()))
   # print("status message" + response.context.flatten().get('status_message'))
   # #check that some data is returned.
   # print("Form errors: : " + str(response.context['gl_search_form'].errors))
    self.assertEqual(response.status_code, 200) 
    self.assertTrue(response.context['gl_search_form'].is_valid())
   # test that the gl-search gets rejected when it's improperly specified.


  #test that search page loads.




