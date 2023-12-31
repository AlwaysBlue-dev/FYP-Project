# Generated by Django 4.1.5 on 2023-04-19 17:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0011_addcourseclo_clos_objective'),
    ]

    operations = [
        migrations.CreateModel(
            name='MapCourseCloPlo',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('course', models.CharField(default='', max_length=100)),
                ('mapped_clos_plos', models.CharField(default='', max_length=50)),
                ('total_mapped_clos_plos', models.CharField(default='', max_length=50)),
                ('fac', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_app.faculty')),
            ],
        ),
    ]
