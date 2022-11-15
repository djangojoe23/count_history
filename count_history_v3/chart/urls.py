from django.urls import path

from count_history_v3.chart.views import GetDataView, GetTitlesView

app_name = "chart"
urlpatterns = [
    path("get-data/", GetDataView.as_view(), name="get_data"),
    path("get-titles/", GetTitlesView.as_view(), name="get_titles"),
]
