from django.http import JsonResponse
from django.views.generic.base import TemplateView

from count_history_v3.base.models import ChartType, Dataset, Parameter
from count_history_v3.query.models import Query


def parse_request(query_string):
    dataset = None
    chart = None
    for param_value in query_string.split("&"):
        param_value_split = param_value.split("=")
        if param_value_split[0] == "dataset":
            dataset = param_value_split[1]
        elif param_value_split[0] == "chart":
            chart = param_value_split[1]

    return dataset, chart


# Create your views here.
class UpdateChartOptionsView(TemplateView):
    template_name = "query/chart_options.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        dataset, chart = parse_request(self.request.META["QUERY_STRING"].lower())

        if dataset:
            if Dataset.objects.filter(label=dataset).exists():
                context["chart_options"] = ChartType.objects.filter(
                    dataset__label=dataset
                )

        return context


class UpdateCountOptionsView(TemplateView):
    template_name = "query/count_options.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        dataset, chart = parse_request(self.request.META["QUERY_STRING"].lower())
        if dataset:
            if Dataset.objects.filter(label=dataset).exists():
                if chart:
                    if ChartType.objects.filter(label=chart).exists():
                        temp_count_options = (
                            ChartType.objects.filter(dataset__label=dataset)
                            .get(label=chart)
                            .count_options
                        )
                        context["count_options"] = {}
                        for option in temp_count_options["options_order"]:
                            context["count_options"][option] = temp_count_options[
                                option
                            ]

        return context


class ParameterFilterView(TemplateView):
    template_name = "query/parameter.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        dataset, chart = parse_request(self.request.META["QUERY_STRING"].lower())

        if dataset:
            if Dataset.objects.filter(label=dataset).exists():
                if chart:
                    if ChartType.objects.filter(label=chart).exists():
                        context["parameters"] = Parameter.objects.filter(
                            dataset__label=dataset
                        ).filter(chart_type__label=chart)
                        context["val_ids_chosen"] = []
                        context["chart_type"] = chart

        return context


class SearchParameterValuesView(TemplateView):
    request = None

    def render_to_response(self, context, **response_kwargs):
        if self.request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest":
            dataset_label = self.request.GET.get("dataset")
            param_label = self.request.GET.get("parameter")
            search_string = self.request.GET.get("search")

            result_dict = {}
            if dataset_label and param_label and search_string:
                result_dict = Query.search_parameter_values(
                    dataset_label, param_label, search_string
                )

            return JsonResponse(result_dict, safe=False, **response_kwargs)
        else:
            return super().render_to_response(context, **response_kwargs)
