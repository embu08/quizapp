# Generated by Django 4.1.1 on 2022-10-11 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0028_alter_passedtests_grade_alter_passedtests_max_grade'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passedtests',
            name='grade',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='passedtests',
            name='max_grade',
            field=models.IntegerField(),
        ),
    ]
