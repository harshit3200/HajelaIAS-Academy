from django import forms
from tinymce.widgets import TinyMCE
from .models import InputSuggestion, Area, Section, PartName, ChapterName, TopicName, SubTopicName
from ckeditor.fields import RichTextField 

class QuestionFilterForm(forms.Form):
    area_name = forms.ModelMultipleChoiceField(
        queryset=Area.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    section_name = forms.ModelMultipleChoiceField(
        queryset=Section.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    part_name = forms.ModelMultipleChoiceField(
        queryset=PartName.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    chapter_name = forms.ModelMultipleChoiceField(
        queryset=ChapterName.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    topic_name = forms.ModelMultipleChoiceField(
        queryset=TopicName.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    subtopic_name = forms.ModelMultipleChoiceField(
        queryset=SubTopicName.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )


from django import forms
from ckeditor.widgets import CKEditorWidget
from .models import InputSuggestion, Area, PartName, ChapterName, TopicName, SubTopicName, ExamName

class InputSuggestionForm(forms.ModelForm):
    brief_description = forms.CharField(widget=CKEditorWidget())
    details = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = InputSuggestion
        fields = [
            'language',
            'brief_description',
            'details',
            'area_name',
            'part_name',
            'chapter_name',
            'topic_name',
            'subtopic_name',
            'exams',                 # ✅ new ManyToMany field
            'question_video',
            'question_link',
            'other_text',
            'source',
            'approval_status',
            'credit_or_courtesy',    # ✅ new text field for credit/courtesy
        ]
        widgets = {
            'language': forms.Select(attrs={'class': 'form-control'}),
            'area_name': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'part_name': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'chapter_name': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'topic_name': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'subtopic_name': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'exams': forms.SelectMultiple(attrs={'class': 'form-control'}),  # ✅
            'question_video': forms.FileInput(attrs={'class': 'form-control'}),
            'question_link': forms.URLInput(attrs={'class': 'form-control'}),
            'other_text': forms.Textarea(attrs={'class': 'form-control'}),
            'source': forms.Select(attrs={'class': 'form-control'}),
            'approval_status': forms.Select(attrs={'class': 'form-control'}),
            'credit_or_courtesy': forms.TextInput(attrs={'class': 'form-control'}),  # ✅
        }


class UploadFileForm(forms.Form):
    file = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        label="Upload File"
    )


from django import forms
from .models import LectureNote

class LectureNoteForm(forms.ModelForm):
    note_file_en = forms.FileField(required=False, label="English File")
    note_file_hi = forms.FileField(required=False, label="Hindi File")

    class Meta:
        model = LectureNote
        fields = ['note_type', 'ctpl', 'area', 'part', 'chapter', 'topic', 'subtopic']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['topic'].required = False
        self.fields['subtopic'].required = False
