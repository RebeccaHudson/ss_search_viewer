from django.conf.urls import url

from . import views
from .views import main #this is apparently the key?
from .views import gl_search
from .views import snpid_search
from .views import shared
from .views import tf_search
from .views import snpid_window_search
from .views import gene_name_search
from .views.tf_search import TranscriptionFactorSearchView
from .views.gl_search import GenomicLocationSearchView
from .views.gene_name_search import GeneNameSearchView
from .views.snpid_window_search import SnpidWindowSearchView
from .views.snpid_search import SnpidSearchView

from .views.ajaxy_snpid_window_search import AjaxySnpidWindowSearchView

app_name = 'ss_viewer'

urlpatterns = [
  url(r'^$', 
         views.main.home_page,
         name = 'index'), 

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
      views.gl_search.GenomicLocationSearchView.as_view(),
      name='gl-region-search'),

  url(r'^trans-factor-search/$',
      views.tf_search.TranscriptionFactorSearchView.as_view(),
      name='trans-factor-search'),

  url(r'snpid-search/$', 
     views.snpid_search.SnpidSearchView.as_view(), 
     name='snpid-search'),

  url(r'ajaxy-snpid-window-search/$', 
       views.ajaxy_snpid_window_search.AjaxySnpidWindowSearchView.as_view(),
       name='ajaxy-snpid-window-search'),

  url(r'snpid-window-search/$',
       views.snpid_window_search.SnpidWindowSearchView.as_view(),
       name='snpid-window-search'),
 
  url(r'gene-name-search/$', 
       views.gene_name_search.GeneNameSearchView.as_view(),
       name='gene-name-search')


]
