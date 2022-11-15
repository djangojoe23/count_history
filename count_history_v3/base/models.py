from django.db import models

from count_history_v3.humans.models import Nonhuman


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

    @classmethod
    def is_parameter_and_value_valid(
        cls, value_id, parameter_label, chart_type, dataset_label
    ):

        if Parameter.objects.filter(
            label=parameter_label, dataset__label=dataset_label, chart__label=chart_type
        ).exists():
            pass
        else:
            return False

        if dataset_label == "humans":
            dataset_model = Nonhuman
        else:
            return False

        # If we made it this far, we know that the parameter is valid for the chart type and the dataset
        # Still need to check if the value is valid for the parameter
        return dataset_model.is_value_valid(value_id, parameter_label)

    @classmethod
    def search_parameter_values(cls, search_str, parameter_label, dataset_label):
        if dataset_label == "humans":
            datset_model = Nonhuman
        else:
            datset_model = None

        if datset_model:
            search_result = datset_model.search_parameter_values(
                search_str, parameter_label
            )
        else:
            search_result = []

        return search_result
