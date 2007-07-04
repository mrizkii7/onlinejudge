from django.conf.urls.defaults import *

from oj.volume.models import ProblemVolume

urlpatterns = patterns('',
    (r'^$', 'oj.volume.views.volume_list'), 
    (r'^(?P<object_id>\d+)/$', 'oj.volume.views.volume_detail'), 
    (r'^(?P<object_id>\d+)/regenerate/$', 'oj.volume.views.volume_regenerate'),

#    (r'^$', 'django.views.generic.list_detail.object_list', 
#     {'queryset': ProblemVolume.objects.all()}),

#    (r'^(?P<object_id>\d+)/$', 'django.views.generic.list_detail.object_detail', 
#     {'queryset':ProblemVolume.objects.all()}),
)
