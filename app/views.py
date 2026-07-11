from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.timezone import now

from . import forms, logic, models


def index(request):
    projects_sorted = models.ClipProject.objects.all().order_by(
        "-upload_datetime", "-id"
    )
    return render(request, "rc/index.html", {"projects_sorted": projects_sorted})


def new_project(request):
    if request.method == "POST":
        form = forms.NewProjectForm(request.POST, request.FILES)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            # FIXME: Should use a transaction or something, so that here cannot be an inconsistent state.

            # First, create an empty project:
            project = models.ClipProject(
                project_name=cleaned_data["name"],
                slug=cleaned_data["slug"],
                current_version=None,  # Will be overridden shortly
                # TODO: Can current_version be set to a new ClipVersion object, if we do it in the same atomic transaction?
                base_file=cleaned_data["file"],
                # upload_datetime is automatic
            )
            project.save()

            # Next, create a "full" version, i.e. with all the data in it:
            span_list = logic.make_span_list(cleaned_data["file"].size)
            version = models.ClipVersion(
                parent_project=project,
                parent_version=None,
                bug_present=True,  # Otherwise, project wouldn't have started
                amount_of_times_loaded=0,
                span_list_converted_to_str=logic.spans_encode(span_list),
                last_datetime_loaded=None,
                # created_datetime is automatic
                decided_datetime=now(),
            )
            version.save()
            project.current_version = version
            project.save()

            # Finally, create the first test version (this overwrites project.current_version):
            sub_version = logic.create_new_unsaved_version(version)
            sub_version.save()

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
