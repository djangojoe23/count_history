# Generated by Django 4.0.8 on 2022-11-13 10:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('humans', '0016_wikipedia_wikidata_wikipedia'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='place',
            name='lastupdate',
        ),
    ]