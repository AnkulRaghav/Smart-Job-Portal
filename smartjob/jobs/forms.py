from django import forms

from accounts.forms import style_fields

from .models import Application, Job

MAX_RESUME_MB = 2


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ["title", "company", "location", "job_type", "salary", "skills", "description", "is_active"]
        widgets = {"description": forms.Textarea(attrs={"rows": 7})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_fields(self)


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["resume", "cover_note"]
        widgets = {"cover_note": forms.Textarea(attrs={"rows": 4})}
        labels = {"resume": "Resume (PDF or TXT, max 2 MB)"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_fields(self)

    def clean_resume(self):
        f = self.cleaned_data["resume"]
        if not f.name.lower().endswith((".pdf", ".txt")):
            raise forms.ValidationError("Only PDF or TXT resumes are allowed.")
        if f.size > MAX_RESUME_MB * 1024 * 1024:
            raise forms.ValidationError(f"File too large (max {MAX_RESUME_MB} MB).")
        return f


class StatusForm(forms.Form):
    application_id = forms.IntegerField(widget=forms.HiddenInput)
    status = forms.ChoiceField(choices=Application.STATUS_CHOICES)
