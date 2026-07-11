from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    return HttpResponse("Hello, world. You're at the repro_clipper index.")


def project_index(request, project_slug: str):
    return HttpResponse(f"This is about project {project_slug}.")


def next_open(request, project_slug: str):
    return HttpResponse(f"Next open of project {project_slug}.")


def specific_version(request, project_slug: str, version_id: int):
    return HttpResponse(f"Version {version_id}, hopefully of project {project_slug}.")
