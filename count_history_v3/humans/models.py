# from collections import Counter

from django.db import models

# from django.db.models import F, Max, Q


# Create your models here.
class Update(models.Model):
    date = models.DateField()


class Webpage(models.Model):
    slug = models.SlugField(primary_key=True, max_length=200)


class Human(models.Model):
    qid = models.PositiveBigIntegerField(primary_key=True, default=0)
    found_on = models.ManyToManyField(Webpage, blank=True)
    found_on_log = models.JSONField(default=dict, null=False, blank=False)
    updates = models.ManyToManyField(Update)


class Nonhuman(models.Model):
    qid = models.PositiveBigIntegerField(primary_key=True, default=0)
    label = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    lastupdate = models.DateField(null=True, blank=True)
    parameter = models.ManyToManyField("base.Parameter", related_name="parameter")


class Place(models.Model):
    nonhuman = models.OneToOneField(
        Nonhuman, on_delete=models.CASCADE, primary_key=True
    )
    latitude = models.DecimalField(
        max_digits=6, decimal_places=3, blank=True, null=True
    )
    longitude = models.DecimalField(
        max_digits=6, decimal_places=3, blank=True, null=True
    )
    precision = models.DecimalField(
        max_digits=10, decimal_places=8, blank=True, null=True
    )
    country = models.ManyToManyField(
        Nonhuman,
        related_name="country",
    )
    continent = models.ManyToManyField(
        Nonhuman,
        related_name="continent",
    )
    lastupdate = models.DateField(null=True, blank=True)


class Lifedate(models.Model):
    class Types(models.TextChoices):
        BIRTH = "b", "birth"
        DEATH = "d", "death"

    class Calendars(models.TextChoices):
        JULIAN = "Q1985786", "Julian"
        GREGORIAN = "Q1985727", "Gregorian"

    type = models.CharField(max_length=1, choices=Types.choices)
    year = models.SmallIntegerField(blank=True, null=True)
    month = models.PositiveSmallIntegerField(blank=True, null=True)
    day = models.PositiveSmallIntegerField(blank=True, null=True)
    precision = models.PositiveSmallIntegerField(blank=True, null=False)
    calendar = models.CharField(max_length=8, choices=Calendars.choices)

    class Meta:
        unique_together = ["type", "year", "month", "day", "precision", "calendar"]


class Wikipedia(models.Model):
    class Grades(models.TextChoices):
        FEATURED = "f", "Featured"
        GOOD = "g", "Good"
        UNGRADED = "u", "Ungraded"

    qid = models.OneToOneField(Human, on_delete=models.CASCADE, primary_key=True)
    enwikititle = models.SlugField(max_length=200, blank=True, null=True)
    pagesize = models.PositiveIntegerField(blank=True, null=True)
    recentviews = models.PositiveIntegerField(blank=True, null=True)
    grade = models.CharField(max_length=1, choices=Grades.choices)
    editcount = models.PositiveIntegerField(blank=True, null=True)
    recentedits = models.PositiveIntegerField(blank=True, null=True)
    connections = models.ManyToManyField("self")


class Wikidata(models.Model):
    qid = models.OneToOneField(Human, on_delete=models.CASCADE, primary_key=True)
    label = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    birthdate = models.ManyToManyField(Lifedate, related_name="birthdate")
    deathdate = models.ManyToManyField(Lifedate, related_name="deathdate")
    gender = models.ManyToManyField(Nonhuman, related_name="gender")
    citizenship = models.ManyToManyField(Nonhuman, related_name="citizenship")
    ethnicity = models.ManyToManyField(Nonhuman, related_name="ethnicity")
    religion = models.ManyToManyField(Nonhuman, related_name="religion")
    occupation = models.ManyToManyField(Nonhuman, related_name="occupation")
    position = models.ManyToManyField(Nonhuman, related_name="position")
    birthplace = models.ManyToManyField(Nonhuman, related_name="birthplace")
    deathplace = models.ManyToManyField(Nonhuman, related_name="deathplace")
    burialplace = models.ManyToManyField(Nonhuman, related_name="burialplace")
    education = models.ManyToManyField(Nonhuman, related_name="education")
    degree = models.ManyToManyField(Nonhuman, related_name="degree")
    field = models.ManyToManyField(Nonhuman, related_name="field")
    political_party = models.ManyToManyField(Nonhuman, related_name="political_party")
    membership = models.ManyToManyField(Nonhuman, related_name="membership")
    handedness = models.ManyToManyField(Nonhuman, related_name="handedness")
    twitterfollowers = models.PositiveIntegerField(null=True, blank=True)
    twitterid = models.PositiveBigIntegerField(null=True, blank=True)
    wikipedia = models.OneToOneField(Wikipedia, on_delete=models.CASCADE, null=True)
