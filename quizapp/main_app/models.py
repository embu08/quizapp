import uuid

from django.db import models, IntegrityError
from django.urls import reverse
from quizapp import settings


class Categories(models.Model):
    name = models.CharField(max_length=100, db_index=True, unique=True,
                            error_messages='Test with that name already exists')

    def __str__(self):
        return self.name


class Test(models.Model):
    name = models.CharField(max_length=255, db_index=True, null=False, blank=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              null=True, blank=True, on_delete=models.CASCADE)
    description = models.CharField(max_length=1000, db_index=True, null=True, blank=True)
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='date')
    time_update = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=True)
    access_by_link = models.BooleanField(default=True)
    show_results = models.BooleanField(default=True)
    category = models.ForeignKey('Categories', blank=True,
                                 null=True, on_delete=models.PROTECT)

    def __str__(self):
        return self.name

    def get_edit_url(self):
        return reverse('tests:edit', kwargs={'pk': self.pk})

    def get_pass_url(self):
        return reverse('tests:pass', kwargs={'pk': self.pk})

    def get_absolute_url(self):
        return reverse('tests:test_detail', kwargs={'pk': self.pk})


class Questions(models.Model):
    question = models.CharField(max_length=255, null=False, blank=False)
    correct_answer = models.CharField(max_length=255)
    answer_1 = models.CharField(max_length=255, null=True)
    answer_2 = models.CharField(max_length=255, null=True, blank=True)
    answer_3 = models.CharField(max_length=255, null=True, blank=True)
    value = models.IntegerField(default=1)
    test = models.ForeignKey('Test', on_delete=models.CASCADE, null=False, blank=False,
                             related_name='question_test')

    def __str__(self):
        return self.question

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['test_id', 'question'], name='unique_questions',
                                    violation_error_message='The question is already in the test.', )
        ]


class PassedTests(models.Model):
    test = models.ForeignKey('Test', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             null=True, blank=True, on_delete=models.CASCADE)
    grade = models.DecimalField(max_digits=5, decimal_places=2)
    max_grade = models.DecimalField(max_digits=5, decimal_places=2)
    data_passed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} get {self.grade} for test {self.test}, {self.data_passed}'



