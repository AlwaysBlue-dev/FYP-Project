# Generated by Django 4.1.5 on 2023-04-19 17:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0009_alter_addcourseclo_course'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='addcourseclo',
            name='clos_objective',
        ),
    ]
