from django.conf.urls import url

from . import views

app_name = 'ss_viewer'

urlpatterns = [
  url(r'^$', views.index, name = 'index'),
  #url(r'one-snp-detail/$', views.one_snp_detail, name = 'one-snp-detail'),
  url(r'one-snp-detail/rs(?P<snpid_numeric>[0-9]+)/$', views.one_snp_detail, name = 'one-snp-detail'), 
  #url(r'search/$', views.get_scores_for_list, name = 'search'),
  url(r'search/$', views.xxx_get_scores_for_list, name = 'alt-search'),
]
