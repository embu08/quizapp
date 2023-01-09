from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from quizapp import settings


class Categories(models.Model):
    name = models.CharField(max_length=100,
                            db_index=True, unique=True, blank=False,
                            error_messages='Category with that name already exists.')

    def clean(self):
        if len(str(self.name)) < 3:
            raise ValidationError('Length of the name of the category must be between 3 and 100 symbols.')

    def __str__(self):
        return str(self.name).title()


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
        return f'Test "{self.name}" by {self.owner}'

    def get_edit_url(self):
        return reverse('tests:test_edit', kwargs={'pk': self.pk})

    def get_pass_url(self):
        return reverse('tests:pass_test', kwargs={'pk': self.pk})

    def get_absolute_url(self):
        return reverse('tests:test_detail', kwargs={'pk': self.pk})


class Questions(models.Model):
    question = models.CharField(max_length=255, null=False, blank=False)
    correct_answer = models.CharField(max_length=255)
    answer_1 = models.CharField(max_length=255)
    answer_2 = models.CharField(max_length=255, null=True, blank=True)
    answer_3 = models.CharField(max_length=255, null=True, blank=True)
    value = models.IntegerField(default=1)
    test = models.ForeignKey('Test', on_delete=models.CASCADE, null=False, blank=False,
                             related_name='question_test')

    def __str__(self):
        return f'Test: {str(self.test).title()}, question: {str(self.question).title()}'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['test_id', 'question'], name='unique_questions',
                                    violation_error_message='The question is already in the test.', )
        ]


class PassedTests(models.Model):
    test = models.ForeignKey('Test', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             null=True, blank=True, on_delete=models.CASCADE)
    grade = models.DecimalField(decimal_places=2, max_digits=5)
    score = models.IntegerField()
    max_score = models.IntegerField()
    data_passed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user}'s grade is {self.grade}. Scored {self.score} out of {self.max_score} points."
