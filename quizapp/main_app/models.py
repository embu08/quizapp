from django.db import models

import users.models
from quizapp import settings


class Categories(models.Model):
    name = models.CharField(max_length=100, db_index=True)

    def __str__(self):
        return self.name


class Test(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              null=True, blank=True, on_delete=models.CASCADE)
    category = models.ForeignKey('Categories', on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.name} by {self.owner}'

    def save_model(self, request, obj, form, change):
        obj.added_by = request.user
        super().save_model(request, obj, form, change)


class Questions(models.Model):
    question = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=255)
    answer_1 = models.CharField(max_length=255, null=True)
    answer_2 = models.CharField(max_length=255, null=True)
    answer_3 = models.CharField(max_length=255, null=True)
    test = models.ForeignKey('Test', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.test}; {self.question} - {self.correct_answer}'
