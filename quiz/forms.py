from django import forms
from django.forms import inlineformset_factory
from django.contrib.auth.models import User
from .models import Quiz, Question, Answer


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'question_type', 'image', 'video', 'time_limit']
        widgets = {
            'text': forms.TextInput(attrs={'placeholder': 'Question text'}),
            'time_limit': forms.NumberInput(attrs={'min': 5, 'max': 300}),
            'video': forms.URLInput(attrs={'placeholder': 'YouTube embed URL (optional)'}),
        }


AnswerFormSet = inlineformset_factory(
    Question,
    Answer,
    fields=['text', 'is_correct'],
    extra=4,
    max_num=6,
    can_delete=True,
    widgets={
        'text': forms.TextInput(attrs={'placeholder': 'Answer option'}),
    },
)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class JoinQuizForm(forms.Form):
    invite_code = forms.CharField(
        max_length=8,
        widget=forms.TextInput(attrs={'placeholder': 'Enter invite code'}),
        label='',
    )
