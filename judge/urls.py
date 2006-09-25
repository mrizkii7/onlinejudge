from django.conf.urls.defaults import *

from oj.judge.models import Judge


urlpatterns = patterns('',

    (r'^$', 'django.views.generic.list_detail.object_list',
     {'queryset':Judge.objects.all(), 'paginate_by':20, 'allow_empty':True }),

    (r'^(?P<object_id>\d+)/$', 'django.views.generic.list_detail.object_detail',
     {'queryset':Judge.objects.all()}),

    (r'^(?P<object_id>\d+)/print/$', 'oj.judge.views.judge_print'),

)

