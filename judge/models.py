from django.db import models

from django.contrib.auth.models import User

from oj.problem.models import Problem

# Create your models here.

LANGUAGE_CHOICES = (
    ('c++', 'C++(GNU C++ 4.1)'),
    ('c', 'C(GNU C 4.1)'),
    ('python', 'Python (Python 2.3)'),
    ('java', 'Java (GCJ 4.1)'),
)

RESULT_CHOICES = (
    ('AC', 'Accepted'),
    ('TLE', 'Time Limit Exceeded'),
    ('MLE', 'Memory Limit Exceeded'),
    ('RE', 'Runtime Error'),
    ('CE', 'Compile Error'),
    ('WA', 'Wrong Answer'),
    ('PE', 'Presentation Error'),
    ('OT', 'Out of Time'),
    ('RV', 'Rule Violated'),
    ('WAIT', 'Waiting'),
    ('TESTING','Testing'),
    ('JE', 'Judger internal error'),
)

class Judge(models.Model):
    user = models.ForeignKey(User)
    problem = models.ForeignKey(Problem)
    language = models.CharField('Language', maxlength = 100, choices=LANGUAGE_CHOICES)
    sourcecode = models.TextField('Source Code')
    submittime = models.DateTimeField('Submit Time')
    result = models.CharField('Result', maxlength = 100, blank = True, choices = RESULT_CHOICES)
    result_detail = models.TextField('Detail of Result', blank = True)
    
    def __str__(self):
	return '%s %s %s %s %s' % (self.user, self.problem, self.language, self.submittime, self.result)

    class Admin: pass

    class Meta:
        ordering = ['-id']
