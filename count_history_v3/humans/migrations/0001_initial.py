# Generated by Django 4.0.8 on 2022-11-08 09:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Human',
            fields=[
                ('qid', models.PositiveBigIntegerField(default=0, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Nonhuman',
            fields=[
                ('qid', models.PositiveBigIntegerField(default=0, primary_key=True, serialize=False)),
                ('label', models.CharField(blank=True, max_length=200, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('lastupdate', models.DateField(blank=True, null=True)),
                ('parameter', models.ManyToManyField(related_name='parameter', to='base.parameter')),
            ],
        ),
        migrations.CreateModel(
            name='Lifedate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('b', 'birth'), ('d', 'death')], max_length=1)),
                ('year', models.SmallIntegerField(blank=True, null=True)),
                ('month', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('day', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('precision', models.PositiveSmallIntegerField(blank=True)),
                ('calendar', models.CharField(choices=[('Q1985786', 'Julian'), ('Q1985727', 'Gregorian')], max_length=8)),
            ],
            options={
                'unique_together': {('type', 'year', 'month', 'day', 'precision', 'calendar')},
            },
        ),
        migrations.CreateModel(
            name='Wikipedia',
            fields=[
                ('qid', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='humans.human')),
                ('enwikititle', models.SlugField(blank=True, max_length=200, null=True)),
                ('pagesize', models.PositiveIntegerField(blank=True, null=True)),
                ('recentviews', models.PositiveIntegerField(blank=True, null=True)),
                ('grade', models.CharField(choices=[('f', 'Featured'), ('g', 'Good'), ('u', 'Ungraded')], max_length=1)),
                ('editcount', models.PositiveIntegerField(blank=True, null=True)),
                ('recentedits', models.PositiveIntegerField(blank=True, null=True)),
                ('connections', models.ManyToManyField(related_name='connection', to='humans.wikipedia')),
            ],
        ),
        migrations.CreateModel(
            name='Wikidata',
            fields=[
                ('qid', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='humans.human')),
                ('label', models.CharField(blank=True, max_length=200, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('twitterfollowers', models.PositiveIntegerField(blank=True, null=True)),
                ('twitterid', models.PositiveBigIntegerField(blank=True, null=True)),
                ('birthdate', models.ManyToManyField(related_name='birthdate', to='humans.lifedate')),
                ('birthplace', models.ManyToManyField(related_name='birthplace', to='humans.nonhuman')),
                ('burialplace', models.ManyToManyField(related_name='burialplace', to='humans.nonhuman')),
                ('citizenship', models.ManyToManyField(related_name='citizenship', to='humans.nonhuman')),
                ('deathdate', models.ManyToManyField(related_name='deathdate', to='humans.lifedate')),
                ('deathplace', models.ManyToManyField(related_name='deathplace', to='humans.nonhuman')),
                ('degree', models.ManyToManyField(related_name='degree', to='humans.nonhuman')),
                ('education', models.ManyToManyField(related_name='education', to='humans.nonhuman')),
                ('ethnicity', models.ManyToManyField(related_name='ethnicity', to='humans.nonhuman')),
                ('field', models.ManyToManyField(related_name='field', to='humans.nonhuman')),
                ('gender', models.ManyToManyField(related_name='gender', to='humans.nonhuman')),
                ('handedness', models.ManyToManyField(related_name='handedness', to='humans.nonhuman')),
                ('membership', models.ManyToManyField(related_name='membership', to='humans.nonhuman')),
                ('occupation', models.ManyToManyField(related_name='occupation', to='humans.nonhuman')),
                ('political_party', models.ManyToManyField(related_name='political_party', to='humans.nonhuman')),
                ('position', models.ManyToManyField(related_name='position', to='humans.nonhuman')),
                ('religion', models.ManyToManyField(related_name='religion', to='humans.nonhuman')),
                ('wikipedia', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='humans.wikipedia')),
            ],
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('nonhuman', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='humans.nonhuman')),
                ('latitude', models.DecimalField(blank=True, decimal_places=3, max_digits=6, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=3, max_digits=6, null=True)),
                ('precision', models.DecimalField(blank=True, decimal_places=8, max_digits=10, null=True)),
                ('lastupdate', models.DateField(blank=True, null=True)),
                ('continent', models.ManyToManyField(related_name='continent', to='humans.nonhuman')),
                ('country', models.ManyToManyField(related_name='country', to='humans.nonhuman')),
            ],
        ),
    ]
