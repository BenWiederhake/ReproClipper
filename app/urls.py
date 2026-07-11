from django.urls import include, path

from . import views

project_patterns = [
    path("", views.project_index, name="project_index"),
    path("next_open", views.next_open, name="next_open"),
    path("v/<int:version_id>/", views.specific_version, name="specific_version"),
]

urlpatterns = [
    path("", views.index, name="index"),
    path("new/", views.new_project, name="new_project"),
    path("p/<slug:project_slug>/", include(project_patterns)),
]
