# Generated by Django 4.2.1 on 2023-12-17 11:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0024_remove_addassessmentclosplo_question_num'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='credit_hours',
            field=models.FloatField(default='0', max_length=100),
        ),
    ]