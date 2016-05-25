from django.test import TestCase
from django.core.urlresolvers import reverse
import unittest
import json

class ScoresViewerTestCase(TestCase):
  def check_for_expected_fields_in_scores_row(self, data_fields_in_one_row):
      expected_fields = [u'motif_len', u'snp_end', u'log_lik_ref', u'snpid', u'motif', u'log_lik_ratio', u'ref_strand', u'ref_start', u'snp_start', u'snp_strand', u'ref_end', u'log_enhance_odds', u'log_reduce_odds', u'log_lik_snp', u'pval_ref', u'pval_snp', u'pval_cond_ref', u'pval_cond_snp', u'pval_diff', u'pval_rank', u'chr', u'pos' ]
      # TODO this could be much better
      matching_fields = list(set(data_fields_in_one_row).intersection(expected_fields))
      self.assertEqual(len(expected_fields), len(matching_fields))

  #this means the api returned something and response is OK. very common.
  def check_for_api_response_and_200_response_code(self, response):
      self.assertEqual(response.context.flatten().has_key('api_response'), True)
      self.assertEqual(response.status_code, 200) 


  def check_status_message(self, response, expected_message):
    self.assertTrue(response.context.flatten().has_key('status_message'))
    self.assertEqual(response.context.flatten()['status_message'], expected_message)
                                                 
   