from django.conf.urls import url

from . import views

urlpatterns = [
  url(r'^$', views.index, name = 'index'),
  #url(r'one-snp-detail/$', views.one_snp_detail, name = 'one-snp-detail'),
  url(r'one-snp-detail/rs(?P<snpid_numeric>[0-9]+)/$', views.one_snp_detail, name = 'one-snp-detail'), 
  url(r'^$', views.index, name = 'one-snp-detail'),
]
