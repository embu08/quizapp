# Generated by Django 4.1.1 on 2022-10-11 12:28

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0023_remove_questions_unique_answers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categories',
            name='name',
            field=models.CharField(db_index=True, error_messages='Test with that name already exists', max_length=100, unique=True, validators=[django.core.validators.MinLengthValidator(4)]),
        ),
    ]
