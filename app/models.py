from django.db import models
from typing import List

MAX_SLUG_LENGTH = 50
MAX_LENGTH_FILENAME = 200
FILE_UPLOAD_STRFTIME = "uploads/%Y/%m/%d/"


def impossible():
    return None  # Would yield a ConsistencyError upon insertion


class ClipProject(models.Model):
    project_name: models.Field = models.TextField()
    slug: models.Field = models.SlugField(max_length=MAX_SLUG_LENGTH)
    # Even though there always must be a "current version", we have to create it NULLABLE,
    # or else we run into a chicken-and-egg problem:
    current_version: models.Field = models.ForeignKey(to="ClipVersion", on_delete=models.RESTRICT, related_name="+none+", null=True)
        # TODO: current_version doesn't need an index
    base_file: models.Field = models.FileField(upload_to=FILE_UPLOAD_STRFTIME, max_length=MAX_LENGTH_FILENAME)
    upload_datetime: models.Field = models.DateTimeField(auto_now_add=True)

    def clipversion_set_ordered(self):
        return self.clipversion_set.all().order_by(
            "-created_datetime", "-id"
        )


# Can't access module "logic" due to circular dependencies.
# Python handles these surprisingly well, but I'd rather just avoid it altogether.
# Instead, this function gets replaced when module 'logic' loads:
def lazy_init_fn__compute_size_linear(version: "ClipVersion") -> int:
    raise AssertionError("Should have been replaced on load of 'logic'.")


class ClipVersion(models.Model):
    parent_project: models.Field = models.ForeignKey(to=ClipProject, on_delete=models.RESTRICT)
    parent_version: models.Field = models.ForeignKey(to="self", on_delete=models.RESTRICT, null=True)
        # TODO: parent_version doesn't need an index, probably?
    bug_present: models.Field = models.BooleanField(null=True, default=None)
    amount_of_times_loaded: models.Field = models.IntegerField(default=0)
    span_list_converted_to_str: models.Field = models.TextField(default=impossible)
    last_datetime_loaded: models.Field = models.DateTimeField(null=True, default=None)
    created_datetime: models.Field = models.DateTimeField(auto_now_add=True)
    decided_datetime: models.Field = models.DateTimeField(null=True, default=None)

    def compute_size_linear(self) -> int:
        return lazy_init_fn__compute_size_linear(self)
