from django.conf.urls import url

from . import views
from .views import main #this is apparently the key?
from .views import gl_search
from .views import snpid_search
from .views import shared
from .views import tf_search
from .views import snpid_window_search
from .views import gene_name_search

app_name = 'ss_viewer'

urlpatterns = [
  url(r'^$', views.main.index, name = 'index'),

  url(r'^multi-search/$', 
      views.shared.StandardFormset.show_multisearch_page,
       name='multi-search'),

  url(r'^gl-region-search/$', 
      views.gl_search.handle_search_by_genomic_location,
      name='gl-region-search'),

  url(r'^trans-factor-search/$',
      views.tf_search.handle_search_by_trans_factor,
      name='trans-factor-search'),

  url(r'snpid-search/$', 
     views.snpid_search.handle_search_by_snpid, 
     name='snpid-search'),

  url(r'snpid-window-search/$',
       views.snpid_window_search.handle_snpid_window_search,
       name='snpid-window-search'),
 
  url(r'gene-name-search/$', 
       views.gene_name_search.handle_gene_name_search,
       name='gene-name-search')
]
