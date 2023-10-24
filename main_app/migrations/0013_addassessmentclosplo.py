# Generated by Django 4.1.5 on 2023-04-19 20:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0012_mapcoursecloplo'),
    ]

    operations = [
        migrations.CreateModel(
            name='AddAssessmentCLOSPLO',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('course', models.CharField(default='', max_length=100)),
                ('assessment_type', models.CharField(default='', max_length=50)),
                ('assessment_number', models.CharField(default='', max_length=50)),
                ('mapped_clos_plos', models.CharField(max_length=100, default="")),
                ('questions', models.CharField(default='', max_length=100)),
                ('question_num', models.CharField(default='', max_length=50)),
                ('question_wise_map_clos_plos', models.CharField(default='', max_length=50)),
                ('fac', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_app.faculty')),
            ],
        ),
    ]
