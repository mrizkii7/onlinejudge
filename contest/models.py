#coding=utf-8
from django.db import models

# Create your models here.

from oj.problem.models import Problem
from django.contrib.auth.models import Group


class Contest(models.Model):
    title = models.CharField('标题', maxlength = 256, core = True)
    description = models.TextField('描述', blank=True, core = True)
    problem = models.ManyToManyField(Problem, blank = True, verbose_name = "问题")
    permittedgroups = models.ManyToManyField(Group, blank = True, verbose_name = "有权限的组")
    start_time = models.DateTimeField('开始时间')
    end_time = models.DateTimeField('结束时间')
    is_public = models.BooleanField('公开')
    
    def __str__(self):
        return '%s' % self.title
    class Admin: 
        pass
    class Meta:
        verbose_name = verbose_name_plural = '比赛'

