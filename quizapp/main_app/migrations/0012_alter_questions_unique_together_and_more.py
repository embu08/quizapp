# Generated by Django 4.1.1 on 2022-09-22 06:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0011_alter_questions_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='questions',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='questions',
            constraint=models.UniqueConstraint(fields=('question', 'test_id'), name='unique questions'),
        ),
    ]
