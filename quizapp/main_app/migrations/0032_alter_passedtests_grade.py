# Generated by Django 4.1.1 on 2022-11-04 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0031_rename_correct_answers_passedtests_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passedtests',
            name='grade',
            field=models.DecimalField(decimal_places=2, max_digits=5),
        ),
    ]
