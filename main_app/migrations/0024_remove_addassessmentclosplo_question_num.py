# Generated by Django 4.2.1 on 2023-11-25 10:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0023_alter_addassessmentclosplo_question_wise_map_clos_plos'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='addassessmentclosplo',
            name='question_num',
        ),
    ]
