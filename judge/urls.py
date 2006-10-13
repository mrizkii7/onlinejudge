from django.conf.urls.defaults import *

from oj.judge.models import Judge


urlpatterns = patterns('',

    (r'^$', 'oj.judge.views.judge_filter'),

    (r'^filter/$', 'oj.judge.views.judge_filter'),

    (r'^(?P<object_id>\d+)/$', 'django.views.generic.list_detail.object_detail',
     {'queryset':Judge.objects.all()}),

    (r'^(?P<object_id>\d+)/print/$', 'oj.judge.views.judge_print'),

    (r'^(?P<object_id>\d+)/rejudge/$', 'oj.judge.views.judge_rejudge'),

)

