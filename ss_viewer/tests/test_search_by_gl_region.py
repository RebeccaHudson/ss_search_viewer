from django.test import TestCase
from django.core.urlresolvers import reverse
from django.conf import settings
from ss_viewer.tests.scores_viewer_test_cases import ScoresViewerTestCase
import unittest
import json

class SearchByGenomicLocationTests(ScoresViewerTestCase):

  def test_that_gl_search_loads_get(self):
    response = self.client.get(reverse('ss_viewer:gl-region-search'), follow=True)
    self.check_that_response_contains_expected_forms(response)
    # if follow is not true, we just get the redirection status code
    response = self.client.get(reverse('ss_viewer:gl-region-search'))
    self.assertEqual(response.status_code, 302)

  def test_that_gl_search_returns_some_data(self):
    response = self.client.post(reverse('ss_viewer:gl-region-search'),
                                { 'selected_chromosome'  : 'ch1',
                                  'gl_start_pos'         : 12214,
                                  'gl_end_pos'           : 12314,
                                  'pvalue_rank_cutoff'   : 0.05,
                                  'action'               : 'Search by Gene Name' })
    self.check_for_api_response_and_200_response_code(response)
    data_response = response.context.__getitem__('api_response')
    #print("api response: " + str(data_response))
    #self.assertEqual(len(data_response), 0) #only one item at this position.
    self.assertEqual(data_response, None)

    self.assertTrue(response.context['gl_search_form'].is_valid())

    # TODO: test that the gl-search gets rejected when it's improperly specified.
    # This request just uses a crazy-high p value, but is otherwise identical
    # to the above.
    response = self.client.post(reverse('ss_viewer:gl-region-search'),
                                { 'selected_chromosome'  : 'ch1',
                                  'gl_start_pos'         : 12214,
                                  'gl_end_pos'           : 12314,
                                  'pvalue_rank_cutoff'   : 0.9,
                                  'action'               : 'Search by Gene Name'  })
    self.check_for_api_response_and_200_response_code(response)
    data_response = response.context.__getitem__('api_response')
    #print("api response: " + str(data_response))
    self.check_for_expected_fields_in_scores_row(data_response[0])
   # print("status message" + response.context.flatten().get('status_message'))
   # #check that some data is returned.
   # print("Form errors: : " + str(response.context['gl_search_form'].errors))
    self.assertTrue(response.context['gl_search_form'].is_valid())



  def test_that_gl_search_can_be_paged(self):
    url = reverse('ss_viewer:gl-region-search')
    base_request = { 'selected_chromosome'  : 'ch1',
                     'gl_start_pos'         : 12214,
                     'gl_end_pos'           : 102314,
                     'pvalue_rank_cutoff'   : 0.01,
                     'action'               : 'Search by Gene Name' }
    self.page_through_request_data(url, base_request, 'gl_search_form')


  def test_nomatch_response_for_gl_search(self):
    response = self.client.post(reverse('ss_viewer:gl-region-search'),
                                { 'selected_chromosome'  : 'ch1',
                                  'gl_start_pos'         : 59152,
                                  'gl_end_pos'           : 59153,
                                  'pvalue_rank_cutoff'   : 0.05,
                                  'action'               : 'Search by Gene Name'  })
    api_response_data = response.context.__getitem__('api_response')
    self.check_for_api_response_and_200_response_code(response)
    self.assertEqual(api_response_data, None)
    self.check_status_message(response, 'No matching rows.')

  
  def test_that_gl_search_post_rejects_an_invalid_form(self):
    response = self.client.post(reverse('ss_viewer:gl-region-search'),
                                       { 'totally_invalid_field'  : 'har-dee-har-harr!' })
    self.check_status_message(response, 'Invalid search. Try agian.')
    self.assertEqual(response.context['gl_search_form'].is_valid(), False)


  def test_that_gl_search_rejects_backwards_region(self):
    response = self.client.post(reverse('ss_viewer:gl-region-search'),
                                { 'selected_chromosome'  : 'ch1',
                                  'gl_start_pos'         : 6000,
                                  'gl_end_pos'           : 5000,
                                  'pvalue_rank_cutoff'   : 0.05,
                                  'action'               : 'Search by Gene Name'  })

    print("status message: " + response.context['status_message'])
    self.assertEqual(response.context['gl_search_form'].is_valid(), False)
    self.check_status_message(response, 'Invalid search. Try agian.')

  #  any p-value cutoff greater than 1 or less than 0 should be rejected.
  def test_that_gl_search_rejects_invalid_cutoffs(self):
    response = self.client.post(reverse('ss_viewer:gl-region-search'),
                                { 'selected_chromosome'  : 'ch1',
                                  'gl_start_pos'         : 100,
                                  'gl_end_pos'           : 200,
                                  'pvalue_rank_cutoff'   : -.1 , 
                                  'action'               : 'Search by Gene Name'  })
    self.assertEqual(response.context['gl_search_form'].is_valid(), False)
    self.check_status_message(response, 'Invalid search. Try agian.')
   
    response = self.client.post(reverse('ss_viewer:gl-region-search'),
                                { 'selected_chromosome'  : 'ch1',
                                  'gl_start_pos'         : 100,
                                  'gl_end_pos'           : 200,
                                  'pvalue_rank_cutoff'   : 1.02,
                                  'action'               : 'Search by Gene Name'  })
    self.assertEqual(response.context['gl_search_form'].is_valid(), False)
    self.check_status_message(response, 'Invalid search. Try agian.')


  def test_that_gl_search_rejects_oversized_region(self):
    big_end = 100 + settings.HARD_LIMITS['MAX_NUMBER_OF_BASES_IN_GENOMIC_LOCATION_REQUEST']
    response = self.client.post(reverse('ss_viewer:gl-region-search'),
                                { 'selected_chromosome'  : 'ch1'  ,
                                  'gl_start_pos'         : 100    ,
                                  'gl_end_pos'           : big_end, 
                                  'pvalue_rank_cutoff'   : -.1 , 
                                  'action'               : 'Search by Gene Name'  })
    self.assertEqual(response.context['gl_search_form'].is_valid(), False)
    self.check_status_message(response, 'Invalid search. Try agian.')



