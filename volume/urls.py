from django.conf.urls.defaults import *

from oj.volume.models import ProblemVolume

urlpatterns = patterns('',
    (r'^$', 'django.views.generic.list_detail.object_list', 
     {'queryset': ProblemVolume.objects.all()}),

    (r'^(?P<object_id>\d+)/$', 'django.views.generic.list_detail.object_detail', 
     {'queryset':ProblemVolume.objects.all()}),
)
