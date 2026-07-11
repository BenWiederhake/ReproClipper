from django.db import models

# TODO: django.utils.timezone.now()

MAX_SLUG_LENGTH = 50
MAX_LENGTH_FILENAME = 200
FILE_UPLOAD_STRFTIME = "uploads/%Y/%m/%d/"


class ClipProject(models.Model):
    project_name = models.TextField()
    slug = models.SlugField(max_length=MAX_SLUG_LENGTH)
    # Even though there always must be a "current version", we have to create it NULLABLE,
    # or else we run into a chicken-and-egg problem:
    current_version = models.ForeignKey(to="ClipVersion", on_delete=models.RESTRICT, related_name="+none+", null=True)
    base_file = models.FileField(upload_to=FILE_UPLOAD_STRFTIME, max_length=MAX_LENGTH_FILENAME)
    upload_datetime = models.DateTimeField(auto_now_add=True)


class ClipVersion(models.Model):
    parent_project = models.ForeignKey(to=ClipProject, on_delete=models.RESTRICT)
    parent_version = models.ForeignKey(to="self", on_delete=models.RESTRICT, null=True)
    user_decision = models.BooleanField(null=True, default=None)
    amount_of_times_loaded = models.IntegerField(default=0)
    last_datetime_loaded = models.DateTimeField(null=True, default=None)
    created_datetime = models.DateTimeField(auto_now_add=True)
    decided_datetime = models.DateTimeField(null=True, default=None)
