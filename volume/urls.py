from django.conf.urls.defaults import *

from oj.volume.models import ProblemVolume

urlpatterns = patterns('oj.volume.views',
	(r'^$', 'volume_list'), 
	(r'^(?P<object_id>\d+)/$', 'volume_detail'), 
    (r'^(?P<object_id>\d+)/regenerate/$', 'volume_regenerate'),
)
