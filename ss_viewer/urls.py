from django.conf.urls import url

from . import views
from .views import main #this is apparently the key?
from .views import gl_search
from .views import shared

app_name = 'ss_viewer'

urlpatterns = [
  url(r'^$', views.main.index, name = 'index'),

  #url(r'^multi-search/$', views.main.show_multisearch_page, name='multi-search'),

  url(r'^multi-search/$', 
      views.shared.StandardFormset.show_multisearch_page,
       name='multi-search'),

  url(r'^gl-region-search/$', 
      views.gl_search.handle_search_by_genomic_location,
      name='gl-region-search'),

  url(r'^trans-factor-search/$',
      views.main.handle_search_by_trans_factor,
      name='trans-factor-search'),

  #url(r'snpid-search/$', views.main.handle_search_by_snpid, name = 'snpid-search'),
  url(r'snpid-search/$', 
     views.snpid_search.handle_search_by_snpid, 
     name='snpid-search'),
]
