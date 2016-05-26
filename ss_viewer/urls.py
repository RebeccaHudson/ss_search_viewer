from django.conf.urls import url

from . import views

app_name = 'ss_viewer'

urlpatterns = [
  url(r'^$', views.index, name = 'index'),
  url(r'one-snp-detail/rs(?P<snpid_numeric>[0-9]+)/$', views.one_snp_detail, name = 'one-snp-detail'), 
  url(r'^multi-search/$', views.show_multisearch_page, name='multi-search'),
  url(r'^gl-region-search/$', views.handle_search_by_genomic_location, name='gl-region-search'),
  url(r'^trans-factor-search/$', views.handle_search_by_trans_factor, name='trans-factor-search'),
  url(r'snpid-search/$', views.handle_search_by_snpid, name = 'snpid-search'),
]
