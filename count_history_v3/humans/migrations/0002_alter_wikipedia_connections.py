# Generated by Django 4.0.8 on 2022-11-08 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('humans', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wikipedia',
            name='connections',
            field=models.ManyToManyField(to='humans.wikipedia'),
        ),
    ]
