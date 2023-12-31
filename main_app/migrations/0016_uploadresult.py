# Generated by Django 4.1.5 on 2023-04-20 17:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0015_rename_assessment_number_addassessmentclosplo_assessment_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='UploadResult',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('department', models.CharField(default='', max_length=100)),
                ('programme', models.CharField(default='', max_length=100)),
                ('batch', models.IntegerField(default='')),
                ('time_shift', models.CharField(choices=[('Morning', 'Morning'), ('Evening', 'Evening')], default='', max_length=50)),
                ('course', models.CharField(default='', max_length=100)),
                ('assessment_type', models.CharField(default='', max_length=50)),
                ('assessment_name', models.CharField(default='', max_length=50)),
                ('total_plos_clos_cover', models.CharField(default='', max_length=100)),
                ('total_marks', models.IntegerField(default='')),
                ('obtained_marks', models.IntegerField(default='')),
                ('fac', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_app.faculty')),
            ],
        ),
    ]
