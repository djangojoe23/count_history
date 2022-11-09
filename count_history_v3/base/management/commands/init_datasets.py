from django.core.management.base import BaseCommand

from count_history_v3.base.models import ChartType, Dataset, Parameter


class Command(BaseCommand):
    help = "This puts initial values in the base models."

    datasets = {
        "humans": {
            "title": "Notable Humans",
            "chart_types": {
                "line": {
                    "count_options": {
                        "births": "Notable Births",
                        "deaths": "Notable Deaths",
                        "births|deaths": "Notable Births & Deaths",
                        "dataset": "Notable Humans in Dataset",
                        "options_order": [
                            "births",
                            "deaths",
                            "births|deaths",
                            "dataset",
                        ],
                    },
                    "chart_prefs": {
                        "totals": {
                            "single": "Single Total",
                            "compare": "Compare Totals",
                            "stack": "Stack Totals",
                            "options_order": ["single", "compare", "stack"],
                        }
                    },
                    "parameters": [
                        "gender",
                        "occupation",
                        "ethnicity",
                        "religion",
                        "citizenship",
                        "position",
                        "birthplace",
                        "birth_country",
                        "birth_continent",
                        "deathplace",
                        "death_country",
                        "death_continent",
                        "burialplace",
                        "burial_country",
                        "burial_continent",
                        "education",
                        "degree",
                        "field",
                        "political_party",
                        "membership",
                        "handedness",
                    ],
                },
                "map": {
                    "count_options": {
                        "births": "Notable Births",
                        "deaths": "Notable Deaths",
                        "burials": "Notable Burials",
                        "births|deaths": "Notable Births & Deaths",
                        "births|burials": "Notable Births & Burials",
                        "deaths|burials": "Notable Deaths & Burials",
                        "births|deaths|burials": "Notable Births, Deaths & Burials",
                        "dataset": "Notable Humans in Dataset",
                        "options_order": [
                            "births",
                            "deaths",
                            "burials",
                            "births|deaths",
                            "births|burials",
                            "deaths|burials",
                            "births|deaths|burials",
                            "dataset",
                        ],
                    },
                    "chart_prefs": {"totals": {"single": "Single Total"}},
                    "parameters": [
                        "gender",
                        "occupation",
                        "ethnicity",
                        "religion",
                        "citizenship",
                        "position",
                        "birthplace",
                        "birth_country",
                        "birth_continent",
                        "deathplace",
                        "death_country",
                        "death_continent",
                        "burialplace",
                        "burial_country",
                        "burial_continent",
                        "education",
                        "degree",
                        "field",
                        "political_party",
                        "membership",
                        "handedness",
                    ],
                },
            },
        }
    }

    parameters = {
        "gender": {"title": "Gender"},
        "occupation": {"title": "Occupation"},
        "ethnicity": {"title": "Ethnic Group"},
        "religion": {"title": "Religion"},
        "citizenship": {"title": "Citizenship"},
        "position": {"title": "Position Held"},
        "birthplace": {"title": "Birth Place"},
        "birth_country": {"title": "Country Associated with Birth Place"},
        "birth_continent": {"title": "Continent Associated with Birth Place"},
        "deathplace": {"title": "Death Place"},
        "death_country": {"title": "Country Associated with Death Place"},
        "death_continent": {"title": "Continent Associated with Death Place"},
        "burialplace": {"title": "Burial Place"},
        "burial_country": {"title": "Country Associated with Burial Place"},
        "burial_continent": {"title": "Continent Associated with Burial Place"},
        "education": {"title": "Educated At"},
        "degree": {"title": "Academic Degree"},
        "field": {"title": "Field of Work"},
        "political_party": {"title": "Political Party"},
        "membership": {"title": "Member Of"},
        "handedness": {"title": "Handedness"},
    }

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        for dataset_label in self.datasets:
            dataset_entry = {
                "label": dataset_label,
                "title": self.datasets[dataset_label]["title"],
            }
            dataset_obj, created = Dataset.objects.update_or_create(
                label=dataset_label,
                title=self.datasets[dataset_label]["title"],
                defaults=dataset_entry,
            )

            for chart_type in self.datasets[dataset_label]["chart_types"]:
                chart_obj, created = ChartType.objects.update_or_create(
                    label=chart_type,
                    defaults={
                        "label": chart_type,
                        "count_options": self.datasets[dataset_label]["chart_types"][
                            chart_type
                        ]["count_options"],
                        "chart_prefs": self.datasets[dataset_label]["chart_types"][
                            chart_type
                        ]["chart_prefs"],
                    },
                )
                chart_obj.dataset.add(dataset_obj)

        for parameter_label in self.parameters:
            parameter_entry = {
                "label": parameter_label,
                "title": self.parameters[parameter_label]["title"],
            }
            parameter_obj, created = Parameter.objects.update_or_create(
                label=parameter_label,
                title=self.parameters[parameter_label]["title"],
                defaults=parameter_entry,
            )

            for dataset in Dataset.objects.all():
                for chart in ChartType.objects.all():
                    if chart.label in self.datasets[dataset.label]:
                        if (
                            parameter_label
                            in self.datasets[dataset.label]["chart_type"][chart.label][
                                "parameters"
                            ]
                        ):
                            parameter_obj.dataset.add(dataset)
                            parameter_obj.chart_type.add(chart)
