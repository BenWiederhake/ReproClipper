from django.db import models

MAX_SLUG_LENGTH = 50
MAX_LENGTH_FILENAME = 200
FILE_UPLOAD_STRFTIME = "uploads/%Y/%m/%d/"


class ClipProject(models.Model):
    project_name: models.Field = models.TextField()
    slug: models.Field = models.SlugField(max_length=MAX_SLUG_LENGTH)
    # Even though there always must be a "current version", we have to create it NULLABLE,
    # or else we run into a chicken-and-egg problem:
    current_version: models.Field = models.ForeignKey(to="ClipVersion", on_delete=models.RESTRICT, related_name="+none+", null=True)
    base_file: models.Field = models.FileField(upload_to=FILE_UPLOAD_STRFTIME, max_length=MAX_LENGTH_FILENAME)
    upload_datetime: models.Field = models.DateTimeField(auto_now_add=True)


class ClipVersion(models.Model):
    parent_project: models.Field = models.ForeignKey(to=ClipProject, on_delete=models.RESTRICT)
    parent_version: models.Field = models.ForeignKey(to="self", on_delete=models.RESTRICT, null=True)
    bug_present: models.Field = models.BooleanField(null=True, default=None)
    amount_of_times_loaded: models.Field = models.IntegerField(default=0)
    segment_list: models.Field = models.JSONField(default=list)
    last_datetime_loaded: models.Field = models.DateTimeField(null=True, default=None)
    created_datetime: models.Field = models.DateTimeField(auto_now_add=True)
    decided_datetime: models.Field = models.DateTimeField(null=True, default=None)
