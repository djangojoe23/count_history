# Generated by Django 4.0.8 on 2022-11-08 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('humans', '0002_alter_wikipedia_connections'),
    ]

    operations = [
        migrations.CreateModel(
            name='Update',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
            ],
        ),
        migrations.AddField(
            model_name='human',
            name='pages',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='human',
            name='updates',
            field=models.ManyToManyField(to='humans.update'),
        ),
    ]
