from django.db import models

# Create your models here.

from oj.problem.models import Problem
from django.contrib.auth.models import Group


class ProblemVolume(models.Model):
    title = models.CharField('Title', maxlength = 256, core = True)
    description = models.TextField('Description', blank=True, core = True)
    problem = models.ManyToManyField(Problem, blank = True)
    permittedgroups = models.ManyToManyField(Group, blank = True)

    def __str__(self):
	return '%s' % self.title

    class Admin: pass

    class Meta:
	verbose_name = 'Problem Volume'
	#permissions = ( ("can_view", "Can View"),
	#	("can_submit", "Can Submit"),
	#)

