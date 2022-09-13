from django.db import models

from quizapp import settings


class Categories(models.Model):
    name = models.CharField(max_length=100, db_index=True)

    def __str__(self):
        return self.name


class Test(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              null=True, blank=True, on_delete=models.CASCADE)
    description = models.CharField(max_length=1000, db_index=True, null=True, blank=True)
    category = models.ForeignKey('Categories', blank=True, null=True, on_delete=models.PROTECT)

    def __str__(self):
        return self.name


class Questions(models.Model):
    question = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=255)
    answer_1 = models.CharField(max_length=255, null=True)
    answer_2 = models.CharField(max_length=255, null=True)
    answer_3 = models.CharField(max_length=255, null=True)
    test = models.ForeignKey('Test', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.question


class PassedTests(models.Model):
    test = models.ForeignKey('Test', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             null=True, blank=True, on_delete=models.CASCADE)
    grade = models.DecimalField(max_digits=5, decimal_places=2)
    data_passed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} get {self.grade} for test {self.test}, {self.data_passed}'
