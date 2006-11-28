from django.conf.urls.defaults import *

#from oj.contest.models import Contest

urlpatterns = patterns('',
    (r'^$', 'oj.contest.views.contest_list'), 
    (r'^(?P<object_id>\d+)/$', 'oj.contest.views.contest_detail'), 

)
