from djongo import models
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# Create your models here.

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

class Note(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='notes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    @property
    def mongoid(self):
        return str(self._id)

class GKEntry(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    GK_TYPE_CHOICES = (
        ('nepal', 'Nepali GK'),
        ('world', 'World GK'),
        ('technical', 'Technical GK'),
    )
    type = models.CharField(max_length=20, choices=GK_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    document = models.FileField(upload_to='gk/docs/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def mongoid(self):
        return str(self._id)

class GKQuestion(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    entry = models.ForeignKey(GKEntry, on_delete=models.CASCADE, related_name='questions')
    question = models.TextField()
    answer = models.TextField(blank=True)

    @property
    def mongoid(self):
        return str(self._id)

# Remove question/answer/document from Article
class Article(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    CATEGORY_CHOICES = (
        ('nepal', 'Nepal GK'),
        ('world', 'World GK'),
        ('technical', 'Technical GK'),
        ('blog', 'Blog'),
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='blog/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):  # noqa: A003
        return f"/blog/{self.pk}/"

    @property
    def mongoid(self):
        return str(self._id)

class Pradesh(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    PROVINCE_CHOICES = [
        (1, 'Koshi'),
        (2, 'Madhesh'),
        (3, 'Bagmati'),
        (4, 'Gandaki'),
        (5, 'Lumbini'),
        (6, 'Karnali'),
        (7, 'Sudurpashchim'),
    ]
    province = models.PositiveSmallIntegerField(choices=PROVINCE_CHOICES, default=1)
    title = models.CharField(max_length=200)
    document = models.FileField(upload_to='pradesh/docs/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_province_display()} - {self.title}"

    @property
    def mongoid(self):
        return str(self._id)

class PradeshQA(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    pradesh = models.ForeignKey(Pradesh, on_delete=models.CASCADE, related_name='qas')
    question = models.TextField()
    answer = models.TextField(blank=True)

    def __str__(self):
        return f"Q: {self.question[:30]}..." if self.question else "Q: ..."

    @property
    def mongoid(self):
        return str(self._id)

class Category(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    @property
    def mongoid(self):
        return str(self._id)

class ModelSet(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='model_sets', null=True)
    timer_hours = models.PositiveIntegerField(default=0)
    timer_minutes = models.PositiveIntegerField(default=0)
    timer_seconds = models.PositiveIntegerField(default=0)
    file = models.FileField(upload_to='model_sets/', blank=True, null=True)
    interactive_url = models.URLField(blank=True, null=True)

    def get_absolute_url(self):  # noqa: A003
        return f"/model-sets/{self.pk}/"

    @property
    def mongoid(self):
        return str(self._id)

class ModelSetQuestion(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    model_set = models.ForeignKey(ModelSet, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_option = models.CharField(max_length=1, choices=[
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
    ])
    explanation = models.TextField(blank=True)

    def __str__(self):
        return self.question_text[:50]

    @property
    def mongoid(self):
        return str(self._id)

class Quiz(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    title = models.CharField(max_length=200)
    topic = models.CharField(max_length=100)
    level = models.CharField(max_length=50)

    def get_absolute_url(self):  # noqa: A003
        return f"/quizzes/{self.pk}/"

    @property
    def mongoid(self):
        return str(self._id)

class TemplateResource(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='templates/images/', blank=True, null=True)
    file = models.FileField(upload_to='templates/docs/', blank=True, null=True)
    description = models.TextField()

    @property
    def mongoid(self):
        return str(self._id)

class GalleryImage(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    title = models.CharField(max_length=200)
    file = models.ImageField(upload_to='gallery/', blank=True, null=True)
    description = models.TextField(blank=True)
    caption = models.CharField(max_length=200, blank=True)

    @property
    def mongoid(self):
        return str(self._id)

class ContactMessage(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    reply = models.TextField(blank=True, null=True)  # Admin reply

    @property
    def mongoid(self):
        return str(self._id)

class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')

class Job(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    title = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    vacancies = models.PositiveIntegerField(default=1)
    opening_date = models.DateField()
    application_deadline = models.DateField()
    more_details = models.URLField(blank=True)
    job_type = models.CharField(max_length=20, choices=(
        ('job', 'Job'),
        ('internship', 'Internship'),
    ))
    location = models.CharField(max_length=200)
    posted_at = models.DateTimeField(auto_now_add=True)

    @property
    def mongoid(self):
        return str(self._id)

    def __str__(self):
        return f"{self.title} ({self.position})"

# New Objective Models
class ObjectiveSubject(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def mongoid(self):
        return str(self._id)

class ObjectiveSet(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    subject = models.ForeignKey(ObjectiveSubject, on_delete=models.CASCADE, related_name='sets')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.subject.name} - {self.title}"

    @property
    def mongoid(self):
        return str(self._id)

class ObjectiveMCQ(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    set = models.ForeignKey(ObjectiveSet, on_delete=models.CASCADE, related_name='mcqs')
    question = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_answer = models.CharField(max_length=1, choices=[
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
    ])
    explanation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.set.title} - Q{self.question[:50]}..."

    @property
    def mongoid(self):
        return str(self._id)

class CurrentEvent(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='current_events/images/', blank=True, null=True)
    document = models.FileField(upload_to='current_events/docs/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return f"/current-event/{self.pk}/"

    @property
    def mongoid(self):
        return str(self._id)

# Subjective Question Management Models
class SubjectiveSubject(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def mongoid(self):
        return str(self._id)

class SubjectiveChapter(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    subject = models.ForeignKey(SubjectiveSubject, on_delete=models.CASCADE, related_name='chapters')
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject.name} - {self.name}"

    @property
    def mongoid(self):
        return str(self._id)

class SubjectiveQA(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    chapter = models.ForeignKey(SubjectiveChapter, on_delete=models.CASCADE, related_name='qas')
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Q: {self.question[:50]}..."

    @property
    def mongoid(self):
        return str(self._id)


