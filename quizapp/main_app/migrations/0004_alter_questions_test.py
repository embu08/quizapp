# Generated by Django 4.1.1 on 2022-09-12 07:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0003_alter_test_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questions',
            name='test',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main_app.test'),
        ),
    ]