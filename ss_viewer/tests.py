from django.test import TestCase
from django.core.urlresolvers import reverse
"""
 Since the goal of this application is to interact with the rsss_api,
 these tests interact with the live, (non-test) version of this api.
 Make sure that the api_v0 app in the rss_api project is running on 
 the expected port before expecting these tests to pass.
"""

#Check that views load up and that we get status codes that make sense.

class OneScoresRowViewDetailTests(TestCase):
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
    requested_snpids =  [ "rs376997626", "rs575624833", "rs189241347"]
    req_header =  { 'content-type' : 'application/json' }
    response = self.client.post(reverse('ss_viewer:search'), headers=req_header,
                               json = requested_snpids )
    self.assertEqual(response.status_code, 200)


