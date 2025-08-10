from django import forms
from .models import Pradesh, PradeshQA, SubjectiveSubject, SubjectiveChapter, SubjectiveQA, Category, ModelSet, ModelSetQuestion

class PradeshForm(forms.ModelForm):
    class Meta:
        model = Pradesh
        fields = '__all__'

class PradeshQAForm(forms.ModelForm):
    class Meta:
        model = PradeshQA
        fields = '__all__'

# Subjective CRUD forms
class SubjectiveSubjectForm(forms.ModelForm):
    class Meta:
        model = SubjectiveSubject
        fields = ['name']

class SubjectiveChapterForm(forms.ModelForm):
    class Meta:
        model = SubjectiveChapter
        fields = ['subject', 'name']

class SubjectiveQAForm(forms.ModelForm):
    class Meta:
        model = SubjectiveQA
        fields = ['chapter', 'question', 'answer']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']

class ModelSetForm(forms.ModelForm):
    class Meta:
        model = ModelSet
        fields = ['title', 'description', 'category', 'timer_hours', 'timer_minutes', 'timer_seconds', 'file', 'interactive_url']

class ModelSetQuestionForm(forms.ModelForm):
    class Meta:
        model = ModelSetQuestion
        fields = ['model_set', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option', 'explanation'] 