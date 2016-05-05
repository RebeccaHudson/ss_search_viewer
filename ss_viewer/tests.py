from django.test import TestCase
from django.core.urlresolvers import reverse
import unittest
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
      expected_fields = [u'motif_len', u'snp_end', u'log_lik_ref', u'snpid', u'motif', u'log_lik_ratio', u'ref_strand', u'ref_start', u'snp_start', u'snp_strand', u'ref_end', u'log_enhance_odds', u'log_reduce_odds', u'log_lik_snp', u'id' ]
      matching_fields = list(set(data_fields_in_one_row).intersection(expected_fields))
      self.assertEqual(len(matching_fields), len(data_fields_in_one_row))


  def test_that_index_view_loads(self):
    response = self.client.get(reverse('ss_viewer:index'))
    self.assertEqual(response.status_code, 200)
    

  def test_that_snp_detail_loads(self):
    #consider making it a random id?
    numb = 750016072
    response = self.client.get(reverse('ss_viewer:one-snp-detail', args=(numb,)))
    self.assertEqual(response.status_code, 200)
    #not sure what else is meaningful to test here, except that the views load.
 
  def test_that_scores_list_loads_post(self):
    response = self.client.post(reverse('ss_viewer:search'),
            { 'requested_snpids' :  '"rs376997626", "rs575624833", "rs189241347"]' })
    #Since the snpids are parsed out with a regular expression, we don't have to 
    #insist on a specific format..
    self.assertEqual(response.context.flatten().has_key('api_response'), True)
    api_response_data = response.context.flatten()['api_response']
    self.assertEqual(len(api_response_data), 3) #asked for 3 rows of data
    for data_row in api_response_data:
      fields_in_data_row = data_row.keys()
      self.check_for_expected_fields_in_scores_row(fields_in_data_row)
    self.assertEqual(response.status_code, 200)

  def test_that_scores_list_loads_get(self): 
     response = self.client.get(reverse('ss_viewer:search'))
     self.assertEqual(response.status_code, 200)


  def test_that_scores_list_loads_post(self):
    response = self.client.post(reverse('ss_viewer:search'),
            { 'requested_snpids' :  '"rs376997626", "rs575624833", "rs189241347"]' })
    #Since the snpids are parsed out with a regular expression, we don't have to 
    #insist on a specific format..
    self.assertEqual(response.context.flatten().has_key('api_response'), True)
    api_response_data = response.context.flatten()['api_response']
    self.assertEqual(len(api_response_data), 3) #asked for 3 rows of data
    for data_row in api_response_data:
      fields_in_data_row = data_row.keys()
      self.check_for_expected_fields_in_scores_row(fields_in_data_row)
    self.assertEqual(response.status_code, 200)

  def test_that_scores_list_loads_get(self): 
     response = self.client.get(reverse('ss_viewer:search'))
     self.assertEqual(response.status_code, 200)

