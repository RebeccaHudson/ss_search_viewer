from django.test import TestCase
from django.core.urlresolvers import reverse
from ss_viewer.tests.scores_viewer_test_cases import ScoresViewerTestCase
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
class GeneralTestsStillYet(ScoresViewerTestCase):
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
    response_json = json.loads(response.content)
    self.assertEqual(len(response_json), 1)
    self.assertEqual(response.status_code, 200)
 
  #we can only expect this test to pass if the requested snpids are actually in the database...
  #retain this code for testing when we actually expect matches to come out...
  def test_that_scores_list_loads_post(self):
    response = self.client.post(reverse('ss_viewer:snpid-search'),
            { 'raw_requested_snpids' : 'rs371194064 rs199706086 rs111200574',
              'pvalue_rank_cutoff' : 1 })
    #should return everything.
    self.check_for_api_response_and_200_response_code(response)
    api_response_data = response.context.flatten()['api_response']
    self.assertEqual(len(api_response_data), 3)

    for data_row in api_response_data:
      fields_in_data_row = data_row.keys()
      self.check_for_expected_fields_in_scores_row(fields_in_data_row)

  #there should be different combinations of inputs that make it spit. 
  #test as many of those here as possbile.
  def test_that_scores_list_post_rejects_an_invalid_form(self):
    #None of the form fields are filled out.
    response = self.client.post(reverse('ss_viewer:snpid-search'),
           { 'totally_invalid_field'  : 'har-dee-har-harr!' })
    self.assertEqual(response.context.flatten().has_key('status_message'), True)
    self.assertEqual(response.context.flatten()['status_message'],'Invalid search. Try agian.')
    self.assertEqual(response.context['snpid_search_form'].is_valid(), False)

  def test_that_scores_list_loads_post_for_no_matching_snpids(self):
    response = self.client.post(reverse('ss_viewer:snpid-search'),
           { 'raw_requested_snpids'  : 'rs111, rs1111111, rs11111111111111, rs1',
             'pvalue_rank_cutoff' : 0.05   })

    self.check_for_api_response_and_200_response_code(response)

    api_response_data = response.context.flatten()['api_response']
    self.assertEqual(api_response_data, None)

    self.assertEqual(response.context.flatten().has_key('status_message'), True)
    self.assertEqual(response.context.flatten()['status_message'],
                                             'No matches for requested snpids' )



  def test_that_scores_list_loads_get(self): 
     response = self.client.get(reverse('ss_viewer:snpid-search'), follow=True)
       
     self.assertTrue(response.context.has_key('gl_search_form'))
     self.assertTrue(response.context.has_key('snpid_search_form'))
     self.assertTrue(response.context.has_key('status_message'))
     self.assertEqual(response.status_code, 200)   #302 redirection


     # if follow is not true, we just get the redirection status code
     response = self.client.get(reverse('ss_viewer:snpid-search'))
     self.assertEqual(response.status_code, 302)   #302 redirection


  #TODO check that gl-search view responds to GET by redirecting to multisearch

  def test_gl_search_returns_some_data(self):

    response = self.client.post(reverse('ss_viewer:gl-region-search'),
                                { 'selected_chromosome'  : 'ch1', 
                                  'gl_start_pos'         : 12214,
                                  'gl_end_pos'           : 12314,
                                  'pvalue_rank_cutoff'   : 0.05 })
    self.check_for_api_response_and_200_response_code(response)
    data_response = response.context.get('api_response')
    self.assertEqual(len(data_response), 0) #only one item at this position.
    self.assertTrue(response.context['gl_search_form'].is_valid())
   
    # TODO: test that the gl-search gets rejected when it's improperly specified.


    # This request just uses a crazy-high p value, but is otherwise identical
    # to the above.
    response = self.client.post(reverse('ss_viewer:gl-region-search'),
                                { 'selected_chromosome'  : 'ch1', 
                                  'gl_start_pos'         : 12214,
                                  'gl_end_pos'           : 12314,
                                  'pvalue_rank_cutoff'   : 0.9  })
    self.check_for_api_response_and_200_response_code(response)
    data_response = response.context.get('api_response')
    self.assertEqual(len(data_response), 1) #only one item at this position.
    self.check_for_expected_fields_in_scores_row(data_response[0])
   # print("status message" + response.context.flatten().get('status_message'))
   # #check that some data is returned.
   # print("Form errors: : " + str(response.context['gl_search_form'].errors))
    self.assertTrue(response.context['gl_search_form'].is_valid())
