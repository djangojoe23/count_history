from django.urls import path

from count_history_v3.query.views import (
    ParameterFilterView,
    SearchParameterValuesView,
    UpdateChartOptionsView,
    UpdateCountOptionsView,
)

app_name = "query"
urlpatterns = [
    path("parameter-filter/", ParameterFilterView.as_view(), name="query_parameter"),
    path("chart-options/", UpdateChartOptionsView.as_view(), name="chart_options"),
    path("count-options/", UpdateCountOptionsView.as_view(), name="count_options"),
    path(
        "parameter-values/",
        SearchParameterValuesView.as_view(),
        name="parameter_values",
    ),
]
