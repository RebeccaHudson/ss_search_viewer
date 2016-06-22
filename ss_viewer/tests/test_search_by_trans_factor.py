from django.test import TestCase
from django.core.urlresolvers import reverse
from django.conf import settings
from ss_viewer.tests.scores_viewer_test_cases import ScoresViewerTestCase
import unittest
import json

class SearchByTranscriptionFactorTests(ScoresViewerTestCase):
    btn_action = "Search by Transcription Factor"

    def test_that_trans_factor_search_loads_get(self):
        # if follow is not true, we just get the redirection status code
        response = self.client.get(reverse('ss_viewer:trans-factor-search'), follow=True)
        self.check_that_response_contains_expected_forms(response)
        response = self.client.get(reverse('ss_viewer:trans-factor-search'))
        self.assertEqual(response.status_code, 302)

    def test_that_tf_search_returns_some_data(self):
        response = self.client.post(reverse('ss_viewer:trans-factor-search'),
                                    { 'trans_factor'         : 'Klf4',
                                      'pvalue_rank_cutoff'   : 0.000001,
                                      'action'               : self.btn_action })
        self.check_for_api_response_and_200_response_code(response)
        data_response = response.context.__getitem__('api_response')
        self.assertTrue(response.context['tf_search_form'].is_valid())

    def test_that_trans_factor_search_can_be_paged(self):
        url = reverse('ss_viewer:trans-factor-search')
        base_request  = { 'trans_factor'         : 'Klf4',
                          'pvalue_rank_cutoff'   : 0.000001,
                          'action'               : self.btn_action }
        self.page_through_request_data(url, base_request, 'tf_search_form')

    # WARNING: final dataset may have something for this.
    def test_nomatch_response_for_tf_search(self):
        response = self.client.post(reverse('ss_viewer:trans-factor-search'),
                                    { 'trans_factor'         :  'Atoh1',
                                      'pvalue_rank_cutoff'   :  0.0,
                                      'action'               :  self.btn_action  })
        api_response_data = response.context.__getitem__('api_response')
        self.check_for_api_response_and_200_response_code(response)
        self.assertEqual(api_response_data, None)
        self.check_status_message(response, 'No matching rows.')

    
    def test_that_tf_search_post_rejects_totally_invalid_form(self):
        response = self.client.post(reverse('ss_viewer:trans-factor-search'),
                                           { 'totally_invalid_field'  : 'har-dee-har-harr!' })
        self.check_status_message(response, 'Invalid search. Try agian.')
        self.assertEqual(response.context['tf_search_form'].is_valid(), False)

