"""
Django settings for ss_search_viewer project.

Generated by 'django-admin startproject' using Django 1.9.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os


#Add/change the tooltip text here.
ALL_TOOLTIPS = {
    'pvalue_rank' : 'Threshold for the p-value of difference in PWM match scores with the reference and the SNP alleles.',
    'pvalue_ref'  : 'P-value for the PWM match with the reference allele.', 
    'pvalue_snp'  : 'P-value for the PWM match with the SNP allele.',
    'motif_degeneracy' : 'PWMs are classified into the degeneracy classes shown here based on their information content (IC).',
    'snpid_box'    :"Enter SNPids to search for.",
    'genomic_location_start' : "Search for data in a region that begins at this position on the chromosome.", 
    'genomic_location_end'   : "Search for data in a region taht ends at this position on the chromosome.",
    'genomic_location_chromosome' : "Chromosome to search for data between the start and end positions specified.",
    'trans_factor_library' : "Select either the ENCODE or JASPAR motif library.",
    'trans_factor_select'  : "Select the transcription factor here.",
    'snpid_window_snpid' :  "Search for data with a window around the position of the snpid entered here.",
    'snpid_window_size' :   "Search for data in a range this number of bases upstream and downstream of the position of the SNPid.",   
    'gene_name'         : "Name of the gene to search for.",
    'gene_window_size'  : "Search for data in a range beginning this many bases upstream of the gene's start position and ending this \
                           number of bases downstream of the gene's end position." 
}


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATIC_URL = '/old/static/' #once this app is back at /, take out the /old/ and put
                            #in 'static'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

UCSC_WINDOW_WIDTH = 200

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'z_qjigm@1xd6(vv7*uc-p(f@4wjcrrlwixgxlpm&tbs2d*yj^s'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

#I added this setting.
API_HOST_INFO = {
  'host_url': 'http://0.0.0.0',
  'host_port' : '8005',
  'api_root' : 'api_v0',
  'result_page_size'  : 15, #this should be much bigger later.
  'download_result_page_size' : 250,
}

ELASTICSEARCH_URLS = [ 'http://atsnp-db'+ str(x) +'.biostat.wisc.edu:9200' for x in range(1,4) ]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ss_viewer',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ss_search_viewer.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ss_search_viewer.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#    }
#}
#

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True
USE_THOUSAND_SEPARATOR = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')

HARD_LIMITS = {
  'MAX_NUMBER_OF_SNPIDS_ALLOWED': 1000,
  'MAX_NUMBER_OF_BASES_IN_GENOMIC_LOCATION_REQUEST': 250000000,
  'MAX_CSV_DOWNLOAD' : 5000,
  'ELASTIC_MAX_RESULT_WINDOW' : 10000,
}

#max number of bases in genomic location request
#ch1 is about 249 million bases, so we limit 
#requests to 250 million.

#ELASTIC_MAX_RESULT_WINDOW:
#is a setting in the Elasticsearch cluster.



QUERY_DEFAULTS = {
  'DEFAULT_REGION_SIZE' : 2500
}




