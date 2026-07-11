from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from . import forms, logic, models


def index(request):
    return render(request, "rc/index.html", {"foo": "bar"})


def new_project(request):
    if request.method == "POST":
        form = forms.NewProjectForm(request.POST, request.FILES)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            project = models.ClipProject(
                project_name=cleaned_data["name"],
                slug=cleaned_data["slug"],
                current_version=None,  # Will be overridden shortly
                # TODO: Can current_version be set to a new ClipVersion object, if we do it in the same atomic transaction?
                base_file=cleaned_data["file"],
                # upload_datetime is automatic
            )
            # FIXME: Create TWO new ClipVersions!
            project.save()
            project_url = reverse("project_index", kwargs=dict(project_slug=project.slug))
            return HttpResponseRedirect(project_url)
    else:
        form = forms.NewProjectForm()

    return render(request, "rc/new.html", {"form": form, "suggestion": logic.suggest_slug()})


def project_index(request, project_slug: str):
    project = get_object_or_404(models.ClipProject, slug=project_slug)
    return render(request, "rc/project_index.html", {"project": "XXX"})


def next_open(request, project_slug: str):
    return HttpResponse(f"Next open of project {project_slug}.")


def specific_version(request, project_slug: str, version_id: int):
    return HttpResponse(f"Version {version_id}, hopefully of project {project_slug}.")
