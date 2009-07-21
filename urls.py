from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
admin.autodiscover()

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^oj/', include('oj.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
	(r'^admin/(.*)', admin.site.root),
	(r'^images/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_PATH}),
	(r'^problem/', include('oj.problem.urls')),
	(r'^$', 'oj.volume.views.index'),
	(r'^volume/', include('oj.volume.urls')),
	(r'^users/', include('oj.userprofile.urls')),
	(r'^judge/', include('oj.judge.urls')),
	(r'^contest/', include('oj.contest.urls')),
)
