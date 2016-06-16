from django.conf.urls import url

from . import views
from .views import main #this is apparently the key?

app_name = 'ss_viewer'

urlpatterns = [
  url(r'^$', views.main.index, name = 'index'),
  url(r'one-snp-detail/rs(?P<snpid_numeric>[0-9]+)/$', views.main.one_snp_detail, name = 'one-snp-detail'),  #remove this shit 
  url(r'^multi-search/$', views.main.show_multisearch_page, name='multi-search'),
  url(r'^gl-region-search/$', views.main.handle_search_by_genomic_location, name='gl-region-search'),
  url(r'^trans-factor-search/$', views.main.handle_search_by_trans_factor, name='trans-factor-search'),
  url(r'snpid-search/$', views.main.handle_search_by_snpid, name = 'snpid-search'),
]
