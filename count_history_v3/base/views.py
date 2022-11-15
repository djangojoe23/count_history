import json

from django.views.generic.base import TemplateView

from count_history_v3.base.models import ChartType, Dataset, Parameter
from count_history_v3.query.models import Query


# Create your views here.
class AnalyzeTemplateView(TemplateView):
    template_name = "base/analyze.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # default values in case the user did not choose something initially
        context["has_sidebar"] = True
        context["dataset_options"] = Dataset.objects.all()
        context["dataset"] = None  # context["dataset_options"].first().label
        context[
            "chart_options"
        ] = None  # ChartType.objects.filter(dataset__label=context["dataset"])
        context["chart"] = None  # context["chart_options"].first().label
        context[
            "chart_preferences"
        ] = None  # context["chart_options"].get(label=context["chart"]).chart_options
        context[
            "count_options"
        ] = None  # context["chart_options"].get(label=context["chart"]).count_options
        context["count"] = None  # list(context["count_options"].keys())[0]
        context["json_param_order"] = json.dumps([])
        context["json_param_value_dict"] = json.dumps({})

        cleaned_query = Query.get_clean_query_dict(self.request, False)
        if "dataset" in cleaned_query:
            if Dataset.objects.filter(label=cleaned_query["dataset"]).exists():
                context["dataset"] = cleaned_query["dataset"]
                context["chart_options"] = ChartType.objects.filter(
                    dataset__label=cleaned_query["dataset"]
                )
                if "chart" in cleaned_query:
                    if (
                        context["chart_options"]
                        .filter(label=cleaned_query["chart"])
                        .exists()
                    ):
                        context["chart"] = cleaned_query["chart"]
                        context["chart_preferences"] = (
                            context["chart_options"]
                            .get(label=context["chart"])
                            .chart_options
                        )
                        if "chart_total" in cleaned_query:
                            context["chart_total"] = cleaned_query["chart_total"]
                            cleaned_query.pop("chart_total")
                        context["parameters"] = Parameter.objects.filter(
                            dataset__label=cleaned_query["dataset"]
                        ).filter(chart_type__label=cleaned_query["chart"])
                        temp_count_options = (
                            context["chart_options"]
                            .get(label=cleaned_query["chart"])
                            .count_options
                        )
                        context["count_options"] = {}
                        for option in temp_count_options["options_order"]:
                            context["count_options"][option] = temp_count_options[
                                option
                            ]
                        if "count" in cleaned_query:
                            context["count"] = cleaned_query["count"]
                            if "param_order" in cleaned_query:
                                context["param_order"] = cleaned_query["param_order"]
                                context["json_param_order"] = json.dumps(
                                    cleaned_query["param_order"]
                                )
                                [
                                    cleaned_query.pop(key)
                                    for key in [
                                        "dataset",
                                        "chart",
                                        "count",
                                        "param_order",
                                    ]
                                ]
                                context["param_value_dict"] = cleaned_query
                                context["json_param_value_dict"] = json.dumps(
                                    cleaned_query
                                )

        return context
