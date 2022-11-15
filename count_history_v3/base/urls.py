from django.urls import path
from django.views.generic import TemplateView

from count_history_v3.base.views import AnalyzeTemplateView

app_name = "base"
urlpatterns = [
    path("", TemplateView.as_view(template_name="base/home.html"), name="home"),
    path("about/", TemplateView.as_view(template_name="base/about.html"), name="about"),
    path("analyze/", AnalyzeTemplateView.as_view(), name="analyze"),
]
