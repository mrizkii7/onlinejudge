#coding=utf-8
from django.db import models

# Create your models here.

from oj.problem.models import Problem
from django.contrib.auth.models import Group


class ProblemVolume(models.Model):
    title = models.CharField('标题', maxlength = 256, core = True)
    description = models.TextField('描述', blank=True, core = True)
    problem = models.ManyToManyField(Problem, blank = True, verbose_name = "问题")
    permittedgroups = models.ManyToManyField(Group, blank = True, verbose_name = "有权限的组")
    ispublic = models.BooleanField("公开", blank = True, core = True)

    def __str__(self):
	return '%s' % self.title

    class Admin: pass

    class Meta:
	verbose_name = verbose_name_plural = '问题卷'
	#permissions = ( ("can_view", "Can View"),
	#	("can_submit", "Can Submit"),
	#)

