from django import forms
from .models import Lecutre, Quiz, Assignment, Announcement, QuizSubmission, AssignmentSubmission

class ClassroomForm(forms.Form):
    classroom_name = forms.CharField(max_length=100)
    classroom_desc = forms.CharField(widget=forms.Textarea)
    class_code = forms.CharField(max_length=20)

class LectureUploadForm(forms.ModelForm):
    class Meta:
        model = Lecutre
        fields = ['lec_name', 'lec_desc', 'lec_file']

class QuizUploadForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['quiz_name', 'quiz_desc', 'quiz_file', 'quiz_deadline', 'quiz_marks']

class AssignmentUploadForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['assign_name', 'assign_desc','assign_file', 'assign_deadline','assign_marks']

class AnnouncementUploadForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['ann_name', 'ann_desc']

class QuizSubmissionForm(forms.ModelForm):
    class Meta:
        model = QuizSubmission
        fields = ['quiz_name','quiz_file']

class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['assign_name','assign_file']



