# Generated by Django 4.1.5 on 2023-04-17 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0003_rename_time_shft_studentregistercourse_time_shift'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentregistercourse',
            name='active',
            field=models.BooleanField(default=True, max_length=50),
        ),
    ]
