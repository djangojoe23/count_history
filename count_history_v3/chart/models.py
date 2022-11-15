from django.db import models
from django.db.models import Q

from count_history_v3.base.models import ChartType, Parameter
from count_history_v3.humans.models import Human


# Create your models here.
class Chart(models.Model):

    # what fields should a chart model have?

    @classmethod
    def get_titles(cls, query_dict, counting_label, chart_type, dataset_label):
        dataset_model = None

        if dataset_label == "humans":
            dataset_model = Human

        chart_obj = ChartType.objects.get(label=chart_type)
        counting_label = chart_obj.count_options[counting_label]
        parameter_titles = {}
        for parameter in query_dict:
            parameter_titles[parameter] = Parameter.objects.get(
                label=parameter
            ).title.lower()
        title, subtitle, x_title, y_title = dataset_model.get_chart_titles(
            counting_label, chart_type, parameter_titles, query_dict
        )

        return title, subtitle, x_title, y_title

    @classmethod
    def get_data(cls, query_dict, counting_label, chart_type, dataset_label):

        data_for_chart = {}
        if dataset_label == "humans":
            dataset_model = Human
        else:
            return data_for_chart

        if ChartType.objects.filter(
            label=chart_type, dataset__label=dataset_label
        ).exists():
            get_all_data = getattr(dataset_model, f"get_all_{chart_type}_data")
            all_data = get_all_data(counting_label)
        else:
            return data_for_chart

        q_filters = Q()
        if query_dict:
            for parameter in query_dict:
                for value_list in query_dict[parameter]:
                    q_filters.add(
                        dataset_model.get_q_filter(parameter, value_list), Q.AND
                    )

        queried_data = all_data.filter(q_filters)

        if queried_data.count() > 0:
            get_chart_data = getattr(dataset_model, f"get_{chart_type}_chart_data")
            raw_chart_data = get_chart_data(counting_label, queried_data)
            if chart_type == "line":
                series_prev_total_dict = {}
                if raw_chart_data:
                    for series in raw_chart_data:
                        series_prev_total_dict[series] = 0
                        time_sorted = sorted(raw_chart_data[series].keys())
                        running_total = 0
                        previous_total = 0
                        for t in time_sorted:
                            running_total += raw_chart_data[series][t]
                            if running_total != previous_total:
                                if t not in data_for_chart:
                                    data_for_chart[t] = {}
                                data_for_chart[t][series] = running_total
                            previous_total = running_total

                    data_for_chart = dict(sorted(data_for_chart.items()))
                    for t in data_for_chart:
                        for series in raw_chart_data:
                            if series not in data_for_chart[t]:
                                data_for_chart[t][series] = series_prev_total_dict[
                                    series
                                ]
                            else:
                                series_prev_total_dict[series] = data_for_chart[t][
                                    series
                                ]
            elif chart_type == "map":
                pass
            else:
                return data_for_chart

            return data_for_chart
