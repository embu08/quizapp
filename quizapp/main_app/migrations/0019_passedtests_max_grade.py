# Generated by Django 4.1.1 on 2022-09-29 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0018_questions_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='passedtests',
            name='max_grade',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
            preserve_default=False,
        ),
    ]