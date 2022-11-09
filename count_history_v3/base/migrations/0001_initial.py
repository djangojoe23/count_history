# Generated by Django 4.0.8 on 2022-11-08 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ChartType',
            fields=[
                ('label', models.CharField(max_length=200, primary_key=True, serialize=False)),
                ('count_options', models.JSONField(default=dict)),
                ('chart_prefs', models.JSONField(default=dict)),
            ],
        ),
        migrations.CreateModel(
            name='Dataset',
            fields=[
                ('label', models.CharField(max_length=200, primary_key=True, serialize=False)),
                ('title', models.CharField(default='Title', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Parameter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=200)),
                ('title', models.CharField(max_length=200)),
                ('chart_type', models.ManyToManyField(to='base.charttype')),
                ('dataset', models.ManyToManyField(to='base.dataset')),
            ],
        ),
        migrations.AddField(
            model_name='charttype',
            name='dataset',
            field=models.ManyToManyField(to='base.dataset'),
        ),
    ]
