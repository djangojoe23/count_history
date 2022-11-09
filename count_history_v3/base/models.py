from django.db import models

# from count_history_v3.humans.models import Nonhuman


# Create your models here.
class Dataset(models.Model):
    label = models.CharField(max_length=200, primary_key=True)
    title = models.CharField(max_length=200, default="Title")


class ChartType(models.Model):
    label = models.CharField(max_length=200, primary_key=True)
    dataset = models.ManyToManyField(Dataset)
    count_options = models.JSONField(default=dict, null=False, blank=False)
    chart_prefs = models.JSONField(default=dict, null=False, blank=False)


class Parameter(models.Model):
    label = models.CharField(max_length=200, blank=False, null=False)
    title = models.CharField(max_length=200, blank=False, null=False)
    chart_type = models.ManyToManyField(ChartType)
    dataset = models.ManyToManyField(Dataset)
