from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.timezone import now
from typing import Optional

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

            # Finally, create the first test version:
            sub_version = logic.create_new_unsaved_version(version)
            sub_version.save()
            project.current_version = sub_version
            project.save()

            project_url = reverse("project_index", kwargs=dict(project_slug=project.slug))
            return HttpResponseRedirect(project_url)
    else:
        form = forms.NewProjectForm()

    return render(request, "rc/new.html", {"form": form, "suggestion": logic.suggest_slug()})


def apply_project_action(project: models.ClipProject, req_type: str, req_version: str, req_present: str) -> Optional[str]:
    try:
        version_id: int = int(req_version)
    except ValueError:
        return f"Invalid POST presence version {req_version}, not a number?!"
    # TODO: Inconsistent behavior, should return a post_error instead:
    version = get_object_or_404(models.ClipVersion, id=version_id, parent_project=project)
    if req_type == "presence":
        if project.current_version.id != version_id:
            return f"Invalid POST presence version {req_version}, not selected?!"
        if req_present == "present":
            version.bug_present = True
        elif req_present == "absent":
            version.bug_present = False
        else:
            return f"Invalid POST presence present-value {req_present}?!"
        version.decided_datetime = now()
        version.save()
        sub_version = logic.create_new_unsaved_version(version)
        sub_version.save()
        # We need to make sure that 'sub_version' propagates to the caller, so we cannot easily fold this into logic.create_new_unsaved_version():
        project.current_version = sub_version
        project.save()
        return None
    elif req_type == "selection":
        if project.current_version.id == version_id:
            return f"Invalid POST selection version {req_version}, already selected?!"
        project.current_version = version
        project.save()
        return None
    else:
        return f"Invalid POST type {req_type}?!"


def project_index(request, project_slug: str):
    project: models.ClipProject = get_object_or_404(models.ClipProject, slug=project_slug)
    post_error: Optional[str] = None
    if request.method == "POST":
        req_type = request.POST.get("type", "<NOVALUE>")
        req_version = request.POST.get("version", "<NOVALUE>")
        req_present = request.POST.get("present", "<NOVALUE>")
        post_error = apply_project_action(project, req_type, req_version, req_present)
    return render(request, "rc/project_index.html", {"project": project, "post_error": post_error})


def next_open(request, project_slug: str):
    project = get_object_or_404(models.ClipProject, slug=project_slug)
    content = logic.reconstruct_content(project.current_version)
    return HttpResponse(content)
    # amount_of_times_loaded: models.Field = models.IntegerField(default=0)


def specific_version(request, project_slug: str, version_id: int):
    project = get_object_or_404(models.ClipProject, slug=project_slug)
    version = get_object_or_404(models.ClipVersion, id=version_id, parent_project=project)
    content = logic.reconstruct_content(version)
    return HttpResponse(content)
    # amount_of_times_loaded: models.Field = models.IntegerField(default=0)


def project_delete(request, project_slug: str):
    project: models.ClipProject = get_object_or_404(models.ClipProject, slug=project_slug)
    if request.method == "POST":
        with transaction.atomic():
            project.current_version = None
            project.save()
            project.clipversion_set.all().delete()  # type: ignore[attr-defined]
            project.delete()
        return HttpResponseRedirect(reverse("index"))
    return render(request, "rc/project_delete.html", {"project": project})
