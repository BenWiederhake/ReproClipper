from django import forms

from . import logic, models


class NewProjectForm(forms.Form):
    # project_name = models.TextField()
    # slug = models.SlugField(max_length=50)
    # base_file = models.FileField(upload_to=FILE_UPLOAD_STRFTIME, max_length=MAX_LENGTH_FILENAME)
    # upload_datetime = models.DateTimeField(auto_now_add=True)

    name = forms.CharField(label="Project name", max_length=100, required=False)
    slug = forms.SlugField(label="Slug", max_length=20, required=False)
    file = forms.FileField()

    def clean(self):
        cleaned_data = super().clean()
        
        file = cleaned_data.get("file")
        name = cleaned_data.get("name")
        if file and not name:
            name = file.name
            cleaned_data["name"] = name
        slug = cleaned_data.get("slug")
        if name and not slug:
            slug = logic.slugify_name(name)
            cleaned_data["slug"] = slug
        slug_exists = True
        try:
            models.ClipProject.objects.get(slug=slug)
        except models.ClipProject.DoesNotExist:
            slug_exists = False
        if slug_exists:
            raise ValidationError(
                f"Slug '{slug}' is already taken"
            )
