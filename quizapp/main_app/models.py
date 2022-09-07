from django.db import models


class Categories(models.Model):
    name = models.CharField(max_length=100, db_index=True)

    def __str__(self):
        return self.name


class User(models.Model):
    pass


class Test(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Categories, on_delete=models.PROTECT)


class Questions(models.Model):
    question = models.CharField(max_length=255)
    correct_answer = models.CharField()
