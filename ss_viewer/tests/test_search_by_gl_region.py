from django.test import TestCase
from django.core.urlresolvers import reverse
from ss_viewer.tests.scores_viewer_test_cases import ScoresViewerTestCase
import unittest
import json

class SearchByGenomicLocationTests(ScoresViewerTestCase):

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



  def test_that_gl_search_returns_some_data(self):
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

