from django.contrib import messages
from django.db import models

from count_history_v3.base.models import ChartType, Dataset, Parameter


# Create your models here.
class Query(models.Model):
    json_query = models.JSONField(null=False, blank=False, unique=True)

    @classmethod
    def get_clean_query_dict(cls, request, has_query):
        clean_query_dict = {}
        raw_param_value_dict = {}
        ignore_url_params = ["dataset", "chart", "count", "chart_total"]
        for param_value_string in request.META["QUERY_STRING"].lower().split("&"):
            param_value_string_split = param_value_string.split("=")
            if len(param_value_string_split) == 2:
                param = param_value_string_split[0].lower()
                if param not in raw_param_value_dict:
                    if param in ignore_url_params:
                        raw_param_value_dict[param] = param_value_string_split[
                            1
                        ].lower()
                    else:
                        if not has_query:
                            if "param_order" not in raw_param_value_dict:
                                raw_param_value_dict["param_order"] = []
                            raw_param_value_dict["param_order"].append(param)
                            raw_param_value_dict[param] = [
                                param_value_string_split[1].lower()
                            ]
                else:
                    if param in ignore_url_params:
                        messages.add_message(
                            request,
                            messages.WARNING,
                            f"Only set the {param} parameter once in the URL.",
                        )
                    else:
                        if not has_query:
                            if "param_order" not in raw_param_value_dict:
                                raw_param_value_dict["param_order"] = []
                            raw_param_value_dict["param_order"].append(param)
                            raw_param_value_dict[param].append(
                                param_value_string_split[1].lower()
                            )
            elif param_value_string_split[0] or len(param_value_string_split) > 2:
                messages.add_message(
                    request,
                    messages.WARNING,
                    "Query parameter not set equal to a value. Is there an & or = missing in the URL?",
                )
                return clean_query_dict
            else:
                pass  # i don't know what could lead me here?

        if "dataset" in raw_param_value_dict:
            if Dataset.objects.filter(label=raw_param_value_dict["dataset"]).exists():
                clean_query_dict["dataset"] = raw_param_value_dict["dataset"]
                if "chart" in raw_param_value_dict:
                    if (
                        ChartType.objects.filter(label=raw_param_value_dict["chart"])
                        .filter(dataset=clean_query_dict["dataset"])
                        .exists()
                    ):
                        clean_query_dict["chart"] = raw_param_value_dict["chart"]
                    else:
                        messages.add_message(
                            request,
                            messages.WARNING,
                            "Unknown chart associated with dataset.",
                        )
                        return clean_query_dict
                    if "count" in raw_param_value_dict:
                        if (
                            ChartType.objects.filter(
                                label=raw_param_value_dict["chart"]
                            )
                            .filter(dataset=clean_query_dict["dataset"])
                            .filter(
                                count_options__has_key=raw_param_value_dict["count"]
                            )
                            .exists()
                        ):
                            clean_query_dict["count"] = raw_param_value_dict["count"]
                        else:
                            messages.add_message(
                                request,
                                messages.WARNING,
                                "Unknown count associated with chart.",
                            )
                            return clean_query_dict
                        if "chart_total" in raw_param_value_dict:
                            if (
                                ChartType.objects.filter(
                                    label=raw_param_value_dict["chart"]
                                )
                                .filter(dataset=clean_query_dict["dataset"])
                                .filter(
                                    chart_options__totals__has_key=raw_param_value_dict[
                                        "chart_total"
                                    ]
                                )
                                .exists()
                            ):
                                clean_query_dict["chart_total"] = raw_param_value_dict[
                                    "chart_total"
                                ]
                            else:
                                pass
                    else:
                        messages.add_message(
                            request, messages.WARNING, "No count chosen"
                        )
                        return clean_query_dict
                else:
                    messages.add_message(request, messages.WARNING, "Unknown chart")
                    return clean_query_dict
            else:
                messages.add_message(request, messages.WARNING, "Unknown dataset")
                return clean_query_dict
        else:
            messages.add_message(request, messages.WARNING, "No dataset chosen.")
            return clean_query_dict

        # print(f"raw={raw_param_value_dict}")
        if has_query:
            pass  # this request is coming from chart/views.py GetDataView
        else:
            if "param_order" in raw_param_value_dict:
                clean_query_dict["param_order"] = []
                for i in range(0, len(raw_param_value_dict["param_order"])):
                    param_label = raw_param_value_dict["param_order"][i]
                    if (
                        Parameter.objects.filter(label__iexact=param_label)
                        .filter(dataset__label=clean_query_dict["dataset"])
                        .filter(chart_type__label=clean_query_dict["chart"])
                        .exists()
                    ):
                        param_index = (
                            raw_param_value_dict["param_order"][: i + 1].count(
                                param_label
                            )
                            - 1
                        )
                        values_split = raw_param_value_dict[param_label][
                            param_index
                        ].split("|")
                        clean_qid_list = []
                        for value_id in values_split:
                            try:
                                int_qid = int(value_id)
                                if int_qid in clean_qid_list:
                                    pass
                                else:
                                    qid_already_listed = False
                                    if param_label in clean_query_dict:
                                        for qid_list in clean_query_dict[param_label]:
                                            if int_qid in qid_list:
                                                qid_already_listed = True
                                    if not qid_already_listed:
                                        if Parameter.is_valid(
                                            int_qid,
                                            param_label,
                                            clean_query_dict["chart"],
                                            clean_query_dict["dataset"],
                                        ):
                                            clean_qid_list.append(int_qid)
                                        else:
                                            messages.add_message(
                                                request,
                                                messages.WARNING,
                                                "Filter parameter value is equal to an unknown QID in the URL.",
                                            )
                            except ValueError:
                                messages.add_message(
                                    request,
                                    messages.WARNING,
                                    "Filter parameter value is equal to an unknown QID in the URL",
                                )

                        if param_label not in clean_query_dict:
                            clean_query_dict[param_label] = []
                        if clean_qid_list:
                            clean_query_dict[param_label].append(clean_qid_list)
                            clean_query_dict["param_order"].append(param_label)
                    else:
                        messages.add_message(
                            request, messages.WARNING, "Unknown parameter label"
                        )

        # print(f"clean={clean_query_dict}")
        return clean_query_dict
