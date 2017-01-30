from django.conf.urls import url

from . import views
from .views import main #this is apparently the key?
from .views import gl_search
from .views import snpid_search
from .views import shared
from .views import tf_search
from .views import snpid_window_search
from .views import gene_name_search
from .views.tf_classbased_search import TranscriptionFactorSearchView

app_name = 'ss_viewer'


 #  url(r'^$',
 #      views.shared.StandardFormset.show_multisearch_page,
 #      name = 'index'),
 # For home page to be the search page.

#known-working version:
#  url(r'^trans-factor-search/$',
#      views.tf_search.handle_search_by_trans_factor,
#      name='trans-factor-search'),

urlpatterns = [
  url(r'^$', 
         views.main.home_page,
         name = 'index'),           #does this need also to be 'home-page'?

  url (r'^dynamic-svg/(?P<plot_id_string>.+)$',
       views.main.dynamic_svg,
       name = 'dynamic-svg'),

  url  (r'^svg-test/$', 
       views.main.test_svg_plots,
       name = 'svg-test'),

  url (r'^help/$', 
       views.main.help_page,
       name = 'help-page'),

  url (r'^about/$', 
       views.main.about_page,
       name = 'about-page'),
  
  url(r'^home/$',
       views.main.home_page,
       name = 'home-page'), 
 
  url(r'^multi-search/$', 
       views.shared.StandardFormset.show_multisearch_page,
       name='multi-search'),

  url(r'^gl-region-search/$', 
      views.gl_search.handle_search_by_genomic_location,
      name='gl-region-search'),

  url(r'^trans-factor-search/$',
      views.tf_classbased_search.TranscriptionFactorSearchView.as_view(),
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
