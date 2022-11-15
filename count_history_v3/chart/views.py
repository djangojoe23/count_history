import json

from django.http import JsonResponse
from django.views.generic.base import TemplateView

from count_history_v3.chart.models import Chart
from count_history_v3.query.models import Query


# Create your views here.
class GetDataView(TemplateView):
    def get(self, request, *args, **kwargs):
        cleaned_query = Query.get_clean_query_dict(self.request, True)

        filter_dict = json.loads(self.request.GET.get("filter"))

        if "dataset" in cleaned_query:
            dataset_label = cleaned_query["dataset"]
        else:
            dataset_label = None

        if "chart" in cleaned_query:
            chart_type = cleaned_query["chart"]
        else:
            chart_type = None

        if "count" in cleaned_query:
            counting = cleaned_query["count"]
        else:
            counting = None

        chart_data = Chart.get_data(dataset_label, chart_type, counting, filter_dict)

        return JsonResponse(chart_data, safe=False)


class GetTitlesView(TemplateView):
    template_name = "chart/chart-titles.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cleaned_query = Query.get_clean_query_dict(self.request, True)

        if "dataset" in cleaned_query:
            dataset_label = cleaned_query["dataset"]
        else:
            dataset_label = None

        if "chart" in cleaned_query:
            chart_type = cleaned_query["chart"]
        else:
            chart_type = None

        if "count" in cleaned_query:
            counting = cleaned_query["count"]
        else:
            counting = None

        filter_dict = json.loads(self.request.GET.get("filter"))

        chart_title = ""
        chart_subtitle = ""
        chart_x_title = ""
        chart_y_title = ""

        if dataset_label and chart_type and counting:
            (
                chart_title,
                chart_subtitle,
                chart_x_title,
                chart_y_title,
            ) = Chart.get_titles(dataset_label, chart_type, counting, filter_dict)

        context["chart_title"] = chart_title
        context["chart_subtitle"] = chart_subtitle
        context["chart_x_title"] = chart_x_title
        context["chart_y_title"] = chart_y_title

        return context
