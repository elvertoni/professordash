from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("htmx/feed-entregas/", views.FeedEntregasView.as_view(), name="htmx_feed_entregas"),
    path("htmx/stats-turmas/", views.StatsTurmasView.as_view(), name="htmx_stats_turmas"),
]
