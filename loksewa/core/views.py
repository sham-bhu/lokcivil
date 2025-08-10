from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .models import User
from django import forms
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Note, Article, Pradesh, ModelSet, Quiz, TemplateResource, GalleryImage, Job, ObjectiveSubject, ObjectiveSet, ObjectiveMCQ
from django.views.decorators.csrf import csrf_exempt
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse, HttpResponseRedirect
from .models import Bookmark
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordResetView
from .models import GKEntry, GKQuestion, PradeshQA
from .models import CurrentEvent
from bson import ObjectId
from .forms import SubjectiveSubjectForm, SubjectiveChapterForm, SubjectiveQAForm, CategoryForm, ModelSetForm, ModelSetQuestionForm
from .models import SubjectiveSubject, SubjectiveChapter, SubjectiveQA
from django.shortcuts import get_object_or_404
from django.utils import timezone
import datetime

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label='First Name')
    last_name = forms.CharField(max_length=30, required=True, label='Last Name')
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    # Remove the role field from the form
    # role = forms.ChoiceField(choices=User.ROLE_CHOICES)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            # Simple validation without complex queries
            try:
                # Just check for exact match to avoid Djongo issues
                if User.objects.filter(username=username).exists():
                    raise forms.ValidationError('A user with that username already exists.')
            except Exception as e:
                # If database query fails, skip validation for now
                pass
        
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'user'  # Always set role to 'user' on signup
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

def signup(request):
    if request.method == 'POST':
        print("=== SIGNUP DEBUG ===")
        print("POST data received:", dict(request.POST))
        form = CustomUserCreationForm(request.POST)
        print("Form is valid:", form.is_valid())
        if form.is_valid():
            print("Form validation passed, attempting to save user...")
            try:
                user = form.save()
                print("User saved successfully:", user.username)
                login(request, user)
                print("User logged in successfully")
                return redirect('/')
            except Exception as e:
                print("=== EXCEPTION DETAILS ===")
                print("Exception type:", type(e).__name__)
                print("Exception message:", str(e))
                import traceback
                print("Full traceback:")
                traceback.print_exc()
                # More specific error handling
                if "iLIKE" in str(e) or "SQLDecodeError" in str(e):
                    form.add_error(None, 'Database connection issue. Please try again or contact support.')
                else:
                    form.add_error(None, f'Registration error: {str(e)}')
        else:
            print("Form validation failed:")
            print("Form errors:", form.errors)
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

# Create your views here.

def home(request):
    return render(request, 'index.html')

def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

def admin_forbidden(request):
    return render(request, 'admin/forbidden.html', status=403)

@login_required
@user_passes_test(is_admin, login_url='/accounts/admin/forbidden/')
def admin_dashboard(request):
    user_count = User.objects.count()
    note_count = Note.objects.count()
    article_count = Article.objects.count()
    pradesh_count = Pradesh.objects.count()
    modelset_count = ModelSet.objects.count()
    quiz_count = Quiz.objects.count()
    job_count = Job.objects.count()
    return render(request, 'admin/dashboard.html', {
        'user_count': user_count,
        'note_count': note_count,
        'article_count': article_count,
        'pradesh_count': pradesh_count,
        'modelset_count': modelset_count,
        'quiz_count': quiz_count,
        'job_count': job_count,
    })

# Notes page
@login_required
def notes(request):
    q = request.GET.get('q', '')
    if q:
        # Use regex for case-insensitive search with Djongo
        import re
        pattern = re.compile(re.escape(q), re.IGNORECASE)
        notes = Note.objects.filter(title__regex=pattern)
    else:
        notes = Note.objects.all()
    bookmarks = []
    if request.user.is_authenticated:
        bookmarks = Bookmark.objects.filter(user=request.user, content_type=ContentType.objects.get_for_model(Note)).values_list('object_id', flat=True)
    return render(request, 'notes.html', {'notes': notes, 'bookmarks': bookmarks})

# GK page
def gk(request):
    tab = request.GET.get('tab', 'nepal')
    gk_entries = GKEntry.objects.filter(type=tab)
    return render(request, 'gk.html', {'gk_entries': gk_entries, 'tab': tab})

# GK detail page
def gk_detail(request, pk):
    from .models import GKEntry
    from bson import ObjectId
    try:
        if isinstance(pk, str):
            pk = ObjectId(pk)
        gk = GKEntry.objects.get(_id=pk)
        questions = gk.questions.all()
        return render(request, 'gk_detail.html', {'gk': gk, 'questions': questions})
    except (GKEntry.DoesNotExist, ValueError, TypeError):
        from django.http import Http404
        raise Http404('GK entry not found')

# Pradesh Bishesh page
def pradesh(request):
    province_map = {
        1: 'Koshi',
        2: 'Madhesh',
        3: 'Bagmati',
        4: 'Gandaki',
        5: 'Lumbini',
        6: 'Karnali',
        7: 'Sudurpashchim',
    }
    selected_province = request.GET.get('province')
    pradeshes = Pradesh.objects.all()
    if selected_province and selected_province.isdigit():
        pradeshes = pradeshes.filter(province=int(selected_province))
    provinces = [(k, v) for k, v in province_map.items()]
    return render(request, 'pradesh.html', {
        'pradeshes': pradeshes,
        'provinces': provinces,
        'selected_province': int(selected_province) if selected_province and selected_province.isdigit() else None,
    })

# Pradesh Bishesh detail page
def pradesh_detail(request, pk):
    from bson import ObjectId
    try:
        if isinstance(pk, str):
            pk = ObjectId(pk)
        pradesh = Pradesh.objects.get(_id=pk)
        qas = pradesh.qas.all()
        return render(request, 'pradesh_detail.html', {'pradesh': pradesh, 'qas': qas})
    except (Pradesh.DoesNotExist, ValueError, TypeError):
        from django.http import Http404
        raise Http404('Pradesh entry not found')

# Model Sets page
def model_sets(request):
    model_sets = ModelSet.objects.all()
    return render(request, 'model_sets.html', {'model_sets': model_sets})

# Quizzes page
def quizzes(request):
    topic = request.GET.get('topic', '')
    level = request.GET.get('level', '')
    quizzes = Quiz.objects.all()
    topics = Quiz.objects.values_list('topic', flat=True).distinct()
    levels = Quiz.objects.values_list('level', flat=True).distinct()
    if topic:
        quizzes = quizzes.filter(topic=topic)
    if level:
        quizzes = quizzes.filter(level=level)
    bookmarks = []
    if request.user.is_authenticated:
        bookmarks = Bookmark.objects.filter(user=request.user, content_type=ContentType.objects.get_for_model(Quiz)).values_list('object_id', flat=True)
    return render(request, 'current_event.html', {'quizzes': quizzes, 'topics': topics, 'levels': levels, 'topic': topic, 'level': level, 'bookmarks': bookmarks})

# Templates page
def templates_page(request):
    templates = TemplateResource.objects.all()
    return render(request, 'templates.html', {'templates': templates})

# Blog page
def blog(request):
    articles = Article.objects.filter(category='blog')
    bookmarks = []
    if request.user.is_authenticated:
        bookmarks = Bookmark.objects.filter(user=request.user, content_type=ContentType.objects.get_for_model(Article)).values_list('object_id', flat=True)
    return render(request, 'blog.html', {'articles': articles, 'bookmarks': bookmarks})

# Gallery page
def gallery(request):
    images = GalleryImage.objects.all()
    return render(request, 'gallery.html', {'images': images})

# Contact page
@csrf_exempt
def contact(request):
    if request.method == 'POST':
        from .models import ContactMessage
        ContactMessage.objects.create(
            name=request.POST.get('first_name', '') + ' ' + request.POST.get('last_name', ''),
            email=request.POST.get('email'),
            message=request.POST.get('message'),
        )
        return render(request, 'contact.html', {'info': 'Your message has been sent to the admin. You will receive a reply soon.'})
    return render(request, 'contact.html')

# Services page
def services(request):
    return render(request, 'services.html')

# Job Board page
def job_board(request):
    jobs = Job.objects.all()  # Removed order_by for Djongo compatibility
    return render(request, 'job_board.html', {'jobs': jobs})

# Admin job post form
class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'position', 'vacancies', 'opening_date', 'application_deadline', 'more_details', 'job_type', 'location']

@user_passes_test(lambda u: u.is_authenticated and u.role == 'admin', login_url='/accounts/admin/forbidden/')
def job_post(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/accounts/job-board/')
    else:
        form = JobForm()
    return render(request, 'job_post.html', {'form': form})

@login_required
def toggle_bookmark(request, model_name, object_id):
    user = request.user
    content_type = ContentType.objects.get(model=model_name)
    bookmark, created = Bookmark.objects.get_or_create(user=user, content_type=content_type, object_id=object_id)
    if not created:
        bookmark.delete()
        status = 'removed'
    else:
        status = 'added'
    if request.is_ajax():
        return JsonResponse({'status': status})
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def profile(request):
    from .models import ContactMessage
    messages = ContactMessage.objects.filter(email=request.user.email)  # Removed order_by for Djongo compatibility
    return render(request, 'registration/profile.html', {
        'user': request.user,
        'contact_messages': messages,
    })

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, 'registration/edit_profile.html', {'form': form})

# Password reset functionality temporarily disabled
# class DjongoPasswordResetForm(PasswordResetForm):
#     def get_queryset(self):
#         """Override to use case-sensitive email search for Djongo compatibility."""
#         from django.contrib.auth import get_user_model
#         return get_user_model()._default_manager.all()

#     def get_users(self, email):
#         # Fetch all users and filter in Python for Djongo compatibility
#         users = self.get_queryset()
#         for user in users:
#             if user.email == email and user.is_active and user.has_usable_password():
#                 yield user

# class DjongoPasswordResetView(PasswordResetView):
#     form_class = DjongoPasswordResetForm

# Admin Notes Management
@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def manage_notes(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        file = request.FILES.get('file')
        
        if title and file:
            Note.objects.create(title=title, file=file)
            messages.success(request, 'Note uploaded successfully!')
            return redirect('manage_notes')
        else:
            messages.error(request, 'Please provide both title and file.')
    
    notes = Note.objects.all()  # Removed order_by for Djongo compatibility
    return render(request, 'admin/manage_notes.html', {'notes': notes})

# Delete Note
@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def delete_note(request, note_id):
    try:
        # Convert string to ObjectId if needed
        from bson import ObjectId
        if isinstance(note_id, str):
            note_id = ObjectId(note_id)
        note = Note.objects.get(_id=note_id)
        note.delete()
        messages.success(request, 'Note deleted successfully!')
    except (Note.DoesNotExist, ValueError, TypeError):
        messages.error(request, 'Note not found!')
    return redirect('manage_notes')

# Placeholder views for other management pages
@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def manage_quizzes(request):
    return render(request, 'admin/coming_soon.html', {'title': 'Manage Current Event', 'description': 'Start/end current events, add questions, view results.'})

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def manage_blog(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.FILES.get('image')
        
        if title and content:
            article = Article.objects.create(
                title=title,
                content=content,
                category='blog',
                image=image
            )
            messages.success(request, 'Blog post created successfully!')
            return redirect('manage_blog')
        else:
            messages.error(request, 'Please provide title and content.')
    
    articles = Article.objects.filter(category='blog')  # Removed order_by for Djongo compatibility
    return render(request, 'admin/manage_blog.html', {'articles': articles})

# Edit Blog Post
@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def edit_blog(request, article_id):
    from bson import ObjectId
    try:
        if isinstance(article_id, str):
            article_id = ObjectId(article_id)
        article = Article.objects.get(_id=article_id, category='blog')
        if request.method == 'POST':
            title = request.POST.get('title')
            content = request.POST.get('content')
            image = request.FILES.get('image')
            
            if title and content:
                article.title = title
                article.content = content
                if image:
                    article.image = image
                article.save()
                messages.success(request, 'Blog post updated successfully!')
                return redirect('manage_blog')
            else:
                messages.error(request, 'Please provide title and content.')
        
        return render(request, 'admin/edit_blog.html', {'article': article})
    except (Article.DoesNotExist, ValueError, TypeError):
        messages.error(request, 'Blog post not found!')
        return redirect('manage_blog')

# Delete Blog Post
@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def delete_blog(request, article_id):
    from bson import ObjectId
    try:
        if isinstance(article_id, str):
            article_id = ObjectId(article_id)
        article = Article.objects.get(_id=article_id, category='blog')
        article.delete()
        messages.success(request, 'Blog post deleted successfully!')
    except (Article.DoesNotExist, ValueError, TypeError):
        messages.error(request, 'Blog post not found!')
    
    return redirect('manage_blog')

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def manage_templates(request):
    from .models import TemplateResource
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        file = request.FILES.get('file')
        if title and description:
            TemplateResource.objects.create(
                title=title,
                description=description,
                image=image,
                file=file
            )
            messages.success(request, 'Template added successfully!')
            return redirect('manage_templates')
        else:
            messages.error(request, 'Please provide title and description.')
    templates = TemplateResource.objects.all()  # Removed order_by for Djongo compatibility
    # Add id_str and id_generation_time for template-safe access
    for t in templates:
        t.id_str = str(t._id)
        t.id_generation_time = getattr(t._id, 'generation_time', None)
    return render(request, 'admin/manage_templates.html', {'templates': templates})

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def edit_template(request, template_id):
    from .models import TemplateResource
    from bson import ObjectId
    try:
        if isinstance(template_id, str):
            template_id = ObjectId(template_id)
        template = TemplateResource.objects.get(_id=template_id)
        if request.method == 'POST':
            template.title = request.POST.get('title')
            template.description = request.POST.get('description')
            image = request.FILES.get('image')
            file = request.FILES.get('file')
            if image:
                template.image = image
            if file:
                template.file = file
            template.save()
            messages.success(request, 'Template updated successfully!')
            return redirect('manage_templates')
        return render(request, 'admin/edit_template.html', {'template': template})
    except (TemplateResource.DoesNotExist, ValueError, TypeError):
        messages.error(request, 'Template not found!')
        return redirect('manage_templates')

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def delete_template(request, template_id):
    from .models import TemplateResource
    from bson import ObjectId
    try:
        if isinstance(template_id, str):
            template_id = ObjectId(template_id)
        template = TemplateResource.objects.get(_id=template_id)
        template.delete()
        messages.success(request, 'Template deleted successfully!')
    except (TemplateResource.DoesNotExist, ValueError, TypeError):
        messages.error(request, 'Template not found!')
    return redirect('manage_templates')

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def manage_gk(request):
    if request.method == 'POST':
        type_ = request.POST.get('type')
        title = request.POST.get('title')
        document = request.FILES.get('document')
        questions = request.POST.getlist('question')
        answers = request.POST.getlist('answer')
        if type_ and title:
            entry = GKEntry.objects.create(type=type_, title=title, document=document)
            for q, a in zip(questions, answers):
                if q.strip():
                    GKQuestion.objects.create(entry=entry, question=q, answer=a)
            messages.success(request, 'GK entry added successfully!')
            return redirect('manage_gk')
        else:
            messages.error(request, 'Please provide GK type and title.')
    gk_entries = GKEntry.objects.all()  # Removed order_by for Djongo compatibility
    return render(request, 'admin/manage_gk.html', {'gk_entries': gk_entries})

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def edit_gk(request, gk_id):
    from bson import ObjectId
    try:
        if isinstance(gk_id, str):
            gk_id = ObjectId(gk_id)
        entry = GKEntry.objects.get(_id=gk_id)
        if request.method == 'POST':
            entry.type = request.POST.get('type')
            entry.title = request.POST.get('title')
            document = request.FILES.get('document')
            if document:
                entry.document = document
            entry.save()
            # Update questions
            GKQuestion.objects.filter(entry=entry).delete()
            questions = request.POST.getlist('question')
            answers = request.POST.getlist('answer')
            for q, a in zip(questions, answers):
                if q.strip():
                    GKQuestion.objects.create(entry=entry, question=q, answer=a)
            messages.success(request, 'GK entry updated successfully!')
            return redirect('manage_gk')
        return render(request, 'admin/edit_gk.html', {'entry': entry, 'questions': entry.questions.all()})
    except (GKEntry.DoesNotExist, ValueError, TypeError):
        messages.error(request, 'GK entry not found!')
        return redirect('manage_gk')

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def delete_gk(request, gk_id):
    from bson import ObjectId
    try:
        if isinstance(gk_id, str):
            gk_id = ObjectId(gk_id)
        entry = GKEntry.objects.get(_id=gk_id)
        entry.delete()
        messages.success(request, 'GK entry deleted successfully!')
    except (GKEntry.DoesNotExist, ValueError, TypeError):
        messages.error(request, 'GK entry not found!')
    return redirect('manage_gk')

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def manage_pradesh(request):
    from .models import Pradesh, PradeshQA
    from .forms import PradeshForm, PradeshQAForm
    if request.method == 'POST':
        form = PradeshForm(request.POST, request.FILES)
        questions = request.POST.getlist('question')
        answers = request.POST.getlist('answer')
        print('DEBUG: questions =', questions)
        print('DEBUG: answers =', answers)
        if form.is_valid():
            pradesh = form.save()
            # Handle Q&A pairs if provided
            for q, a in zip(questions, answers):
                if q.strip():
                    PradeshQA.objects.create(pradesh=pradesh, question=q, answer=a)
            messages.success(request, 'Pradesh entry added successfully!')
            return redirect('manage_pradesh')
        else:
            messages.error(request, 'Please fill all required fields.')
    form = PradeshForm()
    pradesh_entries = Pradesh.objects.all()  # Removed order_by for Djongo compatibility
    return render(request, 'admin/manage_pradesh.html', {'form': form, 'pradesh_entries': pradesh_entries})

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def edit_pradesh(request, pradesh_id):
    from .models import Pradesh, PradeshQA
    from .forms import PradeshForm
    from bson import ObjectId
    try:
        if isinstance(pradesh_id, str):
            pradesh_id = ObjectId(pradesh_id)
        pradesh = Pradesh.objects.get(_id=pradesh_id)
        if request.method == 'POST':
            form = PradeshForm(request.POST, request.FILES, instance=pradesh)
            if form.is_valid():
                pradesh = form.save()
                # Update Q&A
                PradeshQA.objects.filter(pradesh=pradesh).delete()
                questions = request.POST.getlist('question')
                answers = request.POST.getlist('answer')
                for q, a in zip(questions, answers):
                    if q.strip():
                        PradeshQA.objects.create(pradesh=pradesh, question=q, answer=a)
                messages.success(request, 'Province entry updated successfully!')
                return redirect('manage_pradesh')
        else:
            form = PradeshForm(instance=pradesh)
        qas = pradesh.qas.all()
        return render(request, 'admin/edit_pradesh.html', {'form': form, 'pradesh': pradesh, 'qas': qas})
    except (Pradesh.DoesNotExist, ValueError, TypeError):
        messages.error(request, 'Province entry not found!')
        return redirect('manage_pradesh')

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def delete_pradesh(request, pradesh_id):
    from .models import Pradesh
    from bson import ObjectId
    try:
        if isinstance(pradesh_id, str):
            pradesh_id = ObjectId(pradesh_id)
        pradesh = Pradesh.objects.get(_id=pradesh_id)
        pradesh.delete()
        messages.success(request, 'Province entry deleted successfully!')
    except (Pradesh.DoesNotExist, ValueError, TypeError):
        messages.error(request, 'Province entry not found!')
    return redirect('manage_pradesh')

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def manage_model_sets(request):
    return render(request, 'admin/coming_soon.html', {'title': 'Manage Model Sets', 'description': 'Upload and organize practice question papers.'})

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def manage_gallery(request):
    from .models import GalleryImage
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        file = request.FILES.get('file')
        if title:
            GalleryImage.objects.create(title=title, description=description, file=file)
            messages.success(request, 'Gallery image added successfully!')
            return redirect('manage_gallery')
        else:
            messages.error(request, 'Please provide a title.')
    images = GalleryImage.objects.all()  # Removed order_by for Djongo compatibility
    # Add id_str and id_generation_time for template-safe access
    for img in images:
        img.id_str = str(img._id)
        img.id_generation_time = getattr(img._id, 'generation_time', None)
    return render(request, 'admin/manage_gallery.html', {'images': images})

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def edit_gallery(request, image_id):
    from .models import GalleryImage
    from bson import ObjectId
    try:
        if isinstance(image_id, str):
            image_id = ObjectId(image_id)
        image = GalleryImage.objects.get(_id=image_id)
        if request.method == 'POST':
            title = request.POST.get('title')
            description = request.POST.get('description')
            file = request.FILES.get('file')
            if title:
                image.title = title
                image.description = description
                if file:
                    image.file = file
                image.save()
                messages.success(request, 'Gallery image updated successfully!')
                return redirect('manage_gallery')
            else:
                messages.error(request, 'Please provide a title.')
        return render(request, 'admin/edit_gallery.html', {'image': image})
    except (GalleryImage.DoesNotExist, ValueError, TypeError):
        messages.error(request, 'Gallery image not found!')
        return redirect('manage_gallery')

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def delete_gallery(request, image_id):
    from .models import GalleryImage
    from bson import ObjectId
    try:
        if isinstance(image_id, str):
            image_id = ObjectId(image_id)
        image = GalleryImage.objects.get(_id=image_id)
        image.delete()
        messages.success(request, 'Gallery image deleted successfully!')
    except (GalleryImage.DoesNotExist, ValueError, TypeError):
        messages.error(request, 'Gallery image not found!')
    return redirect('manage_gallery')

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def manage_jobs(request):
    from .models import Job
    if request.method == 'POST':
        title = request.POST.get('title')
        position = request.POST.get('position')
        vacancies = request.POST.get('vacancies')
        opening_date = request.POST.get('opening_date')
        application_deadline = request.POST.get('application_deadline')
        more_details = request.POST.get('more_details')
        job_type = request.POST.get('job_type')
        location = request.POST.get('location')
        if title and position and vacancies and opening_date and application_deadline and job_type and location:
            Job.objects.create(
                title=title,
                position=position,
                vacancies=vacancies,
                opening_date=opening_date,
                application_deadline=application_deadline,
                more_details=more_details,
                job_type=job_type,
                location=location
            )
            messages.success(request, 'Job posted successfully!')
            return redirect('manage_jobs')
        else:
            messages.error(request, 'Please fill all required fields.')
    jobs = Job.objects.all()  # Removed order_by for Djongo compatibility
    return render(request, 'admin/manage_jobs.html', {'jobs': jobs})

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def edit_job(request, job_id):
    from .models import Job
    from bson import ObjectId
    try:
        if isinstance(job_id, str):
            job_id = ObjectId(job_id)
        job = Job.objects.get(_id=job_id)
        if request.method == 'POST':
            job.title = request.POST.get('title')
            job.position = request.POST.get('position')
            job.vacancies = request.POST.get('vacancies')
            job.opening_date = request.POST.get('opening_date')
            job.application_deadline = request.POST.get('application_deadline')
            job.more_details = request.POST.get('more_details')
            job.job_type = request.POST.get('job_type')
            job.location = request.POST.get('location')
            job.save()
            messages.success(request, 'Job updated successfully!')
            return redirect('manage_jobs')
        return render(request, 'admin/edit_job.html', {'job': job})
    except (Job.DoesNotExist, ValueError, TypeError):
        messages.error(request, 'Job not found!')
        return redirect('manage_jobs')

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def delete_job(request, job_id):
    from .models import Job
    from bson import ObjectId
    try:
        if isinstance(job_id, str):
            job_id = ObjectId(job_id)
        job = Job.objects.get(_id=job_id)
        job.delete()
        messages.success(request, 'Job deleted successfully!')
    except (Job.DoesNotExist, ValueError, TypeError):
        messages.error(request, 'Job not found!')
    return redirect('manage_jobs')

def blog_detail(request, pk):
    from .models import Article
    try:
        # Convert string to ObjectId if needed
        from bson import ObjectId
        if isinstance(pk, str):
            pk = ObjectId(pk)
        article = Article.objects.get(_id=pk, category='blog')
        return render(request, 'blog_detail.html', {'article': article})
    except (Article.DoesNotExist, ValueError, TypeError):
        from django.http import Http404
        raise Http404('Blog post not found')

@login_required(login_url='/login/')
def objectives(request):
    subjects = ObjectiveSubject.objects.all()
    return render(request, 'objectives.html', {'subjects': subjects})

@login_required(login_url='/login/')
def subjectives(request):
    subjects = SubjectiveSubject.objects.prefetch_related('chapters__qas').all()  # Removed order_by for Djongo compatibility
    return render(request, 'subjectives.html', {'subjects': subjects})

def subjective_chapters(request, subject_id):
    from bson import ObjectId
    subject_id = ObjectId(subject_id)
    subject = SubjectiveSubject.objects.get(_id=subject_id)
    chapters = subject.chapters.all()  # Removed order_by for Djongo compatibility
    return render(request, 'subjective_chapters.html', {'subject': subject, 'chapters': chapters})

def subjective_qas(request, subject_id, chapter_id):
    from bson import ObjectId
    subject_id = ObjectId(subject_id)
    chapter_id = ObjectId(chapter_id)
    subject = SubjectiveSubject.objects.get(_id=subject_id)
    chapter = SubjectiveChapter.objects.get(_id=chapter_id, subject=subject)
    qas = chapter.qas.all()  # Removed order_by for Djongo compatibility
    return render(request, 'subjective_qas.html', {'subject': subject, 'chapter': chapter, 'qas': qas})

@login_required(login_url='/login/')
def objective_subject_detail(request, subject_id):
    from bson import ObjectId
    try:
        if isinstance(subject_id, str):
            subject_id = ObjectId(subject_id)
        subject = ObjectiveSubject.objects.get(_id=subject_id)
        sets = subject.sets.all()
        return render(request, 'objective_subject_detail.html', {'subject': subject, 'sets': sets})
    except (ObjectiveSubject.DoesNotExist, ValueError, TypeError):
        from django.http import Http404
        raise Http404('Subject not found')

@login_required(login_url='/login/')
def objective_set_detail(request, set_id):
    from bson import ObjectId
    try:
        if isinstance(set_id, str):
            set_id = ObjectId(set_id)
        obj_set = ObjectiveSet.objects.get(_id=set_id)
        mcqs = obj_set.mcqs.all()
        return render(request, 'objective_set_detail.html', {'set': obj_set, 'mcqs': mcqs})
    except (ObjectiveSet.DoesNotExist, ValueError, TypeError):
        from django.http import Http404
        raise Http404('Set not found')

# Admin Objective views
@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def manage_objectives(request):
    subjects = ObjectiveSubject.objects.all()
    return render(request, 'admin/manage_objectives.html', {'subjects': subjects})

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def manage_subjectives(request):
    if request.method == 'POST':
        form = SubjectiveSubjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject created successfully!')
            return redirect('manage_subjectives')
    else:
        form = SubjectiveSubjectForm()
    subjects = SubjectiveSubject.objects.prefetch_related('chapters__qas').all()  # Removed order_by for Djongo compatibility
    total_chapters = sum(subject.chapters.count() for subject in subjects)
    total_qas = sum(qa.count() for subject in subjects for qa in [chapter.qas for chapter in subject.chapters.all()])
    return render(request, 'admin/manage_subjectives.html', {
        'form': form,
        'subjects': subjects,
        'total_chapters': total_chapters,
        'total_qas': total_qas,
    })

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def manage_subjective_chapters(request, subject_id):
    subject_id = ObjectId(subject_id)
    subject = SubjectiveSubject.objects.get(_id=subject_id)
    if request.method == 'POST':
        form = SubjectiveChapterForm(request.POST)
        if 'subject' in form.fields:
            del form.fields['subject']
        if form.is_valid():
            chapter = form.save(commit=False)
            chapter.subject = subject
            chapter.save()
            messages.success(request, 'Chapter created successfully!')
            return redirect('manage_subjective_chapters', subject_id=subject.mongoid)
    else:
        form = SubjectiveChapterForm()
        if 'subject' in form.fields:
            del form.fields['subject']
    chapters = subject.chapters.all()  # Removed order_by for Djongo compatibility
    return render(request, 'admin/manage_subjective_chapters.html', {'form': form, 'subject': subject, 'chapters': chapters})

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def manage_subjective_qas(request, chapter_id):
    chapter_id = ObjectId(chapter_id)
    chapter = SubjectiveChapter.objects.get(_id=chapter_id)
    if request.method == 'POST':
        questions = request.POST.getlist('question')
        answers = request.POST.getlist('answer')
        created = 0
        for q, a in zip(questions, answers):
            if q.strip() and a.strip():
                SubjectiveQA.objects.create(chapter=chapter, question=q.strip(), answer=a.strip())
                created += 1
        if created:
            messages.success(request, f'{created} Q&A added successfully!')
        else:
            messages.error(request, 'Please provide at least one valid Q&A.')
        return redirect('manage_subjective_qas', chapter_id=chapter.mongoid)
    qas = chapter.qas.all()  # Removed order_by for Djongo compatibility
    return render(request, 'admin/manage_subjective_qas.html', {'chapter': chapter, 'qas': qas})

# User-facing view to display all subjectives
def subjectives(request):
    subjects = SubjectiveSubject.objects.prefetch_related('chapters__qas').all()  # Removed order_by for Djongo compatibility
    return render(request, 'subjectives.html', {'subjects': subjects})

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def manage_objective_subjects(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        if name:
            ObjectiveSubject.objects.create(name=name, description=description)
            return redirect('manage_objective_subjects')
    
    subjects = ObjectiveSubject.objects.all()
    return render(request, 'admin/manage_objective_subjects.html', {'subjects': subjects})

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def edit_objective_subject(request, subject_id):
    from bson import ObjectId
    try:
        if isinstance(subject_id, str):
            subject_id = ObjectId(subject_id)
        subject = ObjectiveSubject.objects.get(_id=subject_id)
        
        if request.method == 'POST':
            subject.name = request.POST.get('name')
            subject.description = request.POST.get('description', '')
            subject.save()
            return redirect('manage_objective_subjects')
        
        return render(request, 'admin/edit_objective_subject.html', {'subject': subject})
    except (ObjectiveSubject.DoesNotExist, ValueError, TypeError):
        from django.http import Http404
        raise Http404('Subject not found')

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def delete_objective_subject(request, subject_id):
    from bson import ObjectId
    try:
        if isinstance(subject_id, str):
            subject_id = ObjectId(subject_id)
        subject = ObjectiveSubject.objects.get(_id=subject_id)
        subject.delete()
        return redirect('manage_objective_subjects')
    except (ObjectiveSubject.DoesNotExist, ValueError, TypeError):
        from django.http import Http404
        raise Http404('Subject not found')

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def manage_objective_sets(request, subject_id):
    from bson import ObjectId
    try:
        if isinstance(subject_id, str):
            subject_id = ObjectId(subject_id)
        subject = ObjectiveSubject.objects.get(_id=subject_id)
        
        if request.method == 'POST':
            title = request.POST.get('title')
            description = request.POST.get('description', '')
            if title:
                ObjectiveSet.objects.create(subject=subject, title=title, description=description)
                return redirect('manage_objective_sets', subject_id=subject.mongoid)
        
        sets = subject.sets.all()
        return render(request, 'admin/manage_objective_sets.html', {'subject': subject, 'sets': sets})
    except (ObjectiveSubject.DoesNotExist, ValueError, TypeError):
        from django.http import Http404
        raise Http404('Subject not found')

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def edit_objective_set(request, set_id):
    from bson import ObjectId
    try:
        if isinstance(set_id, str):
            set_id = ObjectId(set_id)
        obj_set = ObjectiveSet.objects.get(_id=set_id)
        
        if request.method == 'POST':
            obj_set.title = request.POST.get('title')
            obj_set.description = request.POST.get('description', '')
            obj_set.save()
            return redirect('manage_objective_sets', subject_id=obj_set.subject.mongoid)
        
        return render(request, 'admin/edit_objective_set.html', {'set': obj_set})
    except (ObjectiveSet.DoesNotExist, ValueError, TypeError):
        from django.http import Http404
        raise Http404('Set not found')

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def delete_objective_set(request, set_id):
    from bson import ObjectId
    try:
        if isinstance(set_id, str):
            set_id = ObjectId(set_id)
        obj_set = ObjectiveSet.objects.get(_id=set_id)
        subject_id = obj_set.subject.mongoid
        obj_set.delete()
        return redirect('manage_objective_sets', subject_id=subject_id)
    except (ObjectiveSet.DoesNotExist, ValueError, TypeError):
        from django.http import Http404
        raise Http404('Set not found')

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def manage_objective_mcqs(request, set_id):
    from bson import ObjectId
    try:
        if isinstance(set_id, str):
            set_id = ObjectId(set_id)
        obj_set = ObjectiveSet.objects.get(_id=set_id)
        
        if request.method == 'POST':
            question = request.POST.get('question')
            option_a = request.POST.get('option_a')
            option_b = request.POST.get('option_b')
            option_c = request.POST.get('option_c')
            option_d = request.POST.get('option_d')
            correct_answer = request.POST.get('correct_answer')
            explanation = request.POST.get('explanation', '')
            
            if question and option_a and option_b and option_c and option_d and correct_answer:
                ObjectiveMCQ.objects.create(
                    set=obj_set,
                    question=question,
                    option_a=option_a,
                    option_b=option_b,
                    option_c=option_c,
                    option_d=option_d,
                    correct_answer=correct_answer,
                    explanation=explanation
                )
                return redirect('manage_objective_mcqs', set_id=obj_set.mongoid)
        
        mcqs = obj_set.mcqs.all()
        return render(request, 'admin/manage_objective_mcqs.html', {'set': obj_set, 'mcqs': mcqs})
    except (ObjectiveSet.DoesNotExist, ValueError, TypeError):
        from django.http import Http404
        raise Http404('Set not found')

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def edit_objective_mcq(request, mcq_id):
    from bson import ObjectId
    try:
        if isinstance(mcq_id, str):
            mcq_id = ObjectId(mcq_id)
        mcq = ObjectiveMCQ.objects.get(_id=mcq_id)
        
        if request.method == 'POST':
            mcq.question = request.POST.get('question')
            mcq.option_a = request.POST.get('option_a')
            mcq.option_b = request.POST.get('option_b')
            mcq.option_c = request.POST.get('option_c')
            mcq.option_d = request.POST.get('option_d')
            mcq.correct_answer = request.POST.get('correct_answer')
            mcq.explanation = request.POST.get('explanation', '')
            mcq.save()
            return redirect('manage_objective_mcqs', set_id=mcq.set.mongoid)
        
        return render(request, 'admin/edit_objective_mcq.html', {'mcq': mcq})
    except (ObjectiveMCQ.DoesNotExist, ValueError, TypeError):
        from django.http import Http404
        raise Http404('MCQ not found')

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def delete_objective_mcq(request, mcq_id):
    from bson import ObjectId
    try:
        if isinstance(mcq_id, str):
            mcq_id = ObjectId(mcq_id)
        mcq = ObjectiveMCQ.objects.get(_id=mcq_id)
        set_id = mcq.set.mongoid
        mcq.delete()
        return redirect('manage_objective_mcqs', set_id=set_id)
    except (ObjectiveMCQ.DoesNotExist, ValueError, TypeError):
        from django.http import Http404
        raise Http404('MCQ not found')

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def manage_current_event(request):
    events = CurrentEvent.objects.all()  # Removed order_by for Djongo compatibility
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        document = request.FILES.get('document')
        CurrentEvent.objects.create(title=title, description=description, image=image, document=document)
        messages.success(request, 'Current event created successfully!')
        return redirect('manage_current_event')
    return render(request, 'admin/manage_current_event.html', {'events': events})

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def edit_current_event(request, event_id):
    try:
        if isinstance(event_id, str):
            event_id = ObjectId(event_id)
        event = CurrentEvent.objects.get(_id=event_id)
        if request.method == 'POST':
            event.title = request.POST.get('title')
            event.description = request.POST.get('description')
            if request.FILES.get('image'):
                event.image = request.FILES.get('image')
            if request.FILES.get('document'):
                event.document = request.FILES.get('document')
            event.save()
            messages.success(request, 'Current event updated successfully!')
            return redirect('manage_current_event')
        return render(request, 'admin/edit_current_event.html', {'event': event})
    except (CurrentEvent.DoesNotExist, ValueError, TypeError):
        return HttpResponseForbidden('Event not found or invalid.')

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def delete_current_event(request, event_id):
    try:
        if isinstance(event_id, str):
            event_id = ObjectId(event_id)
        event = CurrentEvent.objects.get(_id=event_id)
        event.delete()
        messages.success(request, 'Current event deleted successfully!')
        return redirect('manage_current_event')
    except (CurrentEvent.DoesNotExist, ValueError, TypeError):
        return HttpResponseForbidden('Event not found or invalid.')

def current_event(request):
    events = CurrentEvent.objects.all()  # Removed order_by for Djongo compatibility
    return render(request, 'current_event.html', {'events': events})

def current_event_detail(request, pk):
    from bson import ObjectId
    from .models import CurrentEvent
    try:
        if isinstance(pk, str):
            pk = ObjectId(pk)
        event = CurrentEvent.objects.get(_id=pk)
        return render(request, 'current_event_detail.html', {'event': event})
    except (CurrentEvent.DoesNotExist, ValueError, TypeError):
        from django.http import Http404
        raise Http404('Current event not found')

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def edit_subjective_chapter(request, chapter_id):
    chapter_id = ObjectId(chapter_id)
    chapter = get_object_or_404(SubjectiveChapter, _id=chapter_id)
    if request.method == 'POST':
        form = SubjectiveChapterForm(request.POST, instance=chapter)
        if form.is_valid():
            form.save()
            messages.success(request, 'Chapter updated successfully!')
            return redirect('manage_subjective_chapters', subject_id=chapter.subject.mongoid)
    else:
        form = SubjectiveChapterForm(instance=chapter)
    return render(request, 'admin/edit_subjective_chapter.html', {'form': form, 'chapter': chapter})

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def delete_subjective_chapter(request, chapter_id):
    chapter_id = ObjectId(chapter_id)
    chapter = get_object_or_404(SubjectiveChapter, _id=chapter_id)
    subject_id = chapter.subject.mongoid
    chapter.delete()
    messages.success(request, 'Chapter deleted successfully!')
    return redirect('manage_subjective_chapters', subject_id=subject_id)

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def edit_subjective_qa(request, qa_id):
    qa_id = ObjectId(qa_id)
    qa = get_object_or_404(SubjectiveQA, _id=qa_id)
    if request.method == 'POST':
        form = SubjectiveQAForm(request.POST, instance=qa)
        if form.is_valid():
            form.save()
            messages.success(request, 'Q&A updated successfully!')
            return redirect('manage_subjective_qas', chapter_id=qa.chapter.mongoid)
    else:
        form = SubjectiveQAForm(instance=qa)
    return render(request, 'admin/edit_subjective_qa.html', {'form': form, 'qa': qa})

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def delete_subjective_qa(request, qa_id):
    qa_id = ObjectId(qa_id)
    qa = get_object_or_404(SubjectiveQA, _id=qa_id)
    chapter_id = qa.chapter.mongoid
    qa.delete()
    messages.success(request, 'Q&A deleted successfully!')
    return redirect('manage_subjective_qas', chapter_id=chapter_id)

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def edit_subjective_subject(request, subject_id):
    subject_id = ObjectId(subject_id)
    subject = get_object_or_404(SubjectiveSubject, _id=subject_id)
    if request.method == 'POST':
        form = SubjectiveSubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject updated successfully!')
            return redirect('manage_subjectives')
    else:
        form = SubjectiveSubjectForm(instance=subject)
    return render(request, 'admin/edit_subjective_subject.html', {'form': form, 'subject': subject})

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def delete_subjective_subject(request, subject_id):
    subject_id = ObjectId(subject_id)
    subject = get_object_or_404(SubjectiveSubject, _id=subject_id)
    subject.delete()
    messages.success(request, 'Subject deleted successfully!')
    return redirect('manage_subjectives')

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def manage_categories(request):
    from .models import Category
    categories = Category.objects.all()  # Removed order_by for Djongo compatibility
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully!')
            return redirect('manage_categories')
    else:
        form = CategoryForm()
    return render(request, 'admin/manage_categories.html', {'categories': categories, 'form': form})

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def edit_category(request, category_id):
    from .models import Category
    try:
        if isinstance(category_id, str):
            category_id = ObjectId(category_id)
        category = Category.objects.get(_id=category_id)
        if request.method == 'POST':
            form = CategoryForm(request.POST, instance=category)
            if form.is_valid():
                form.save()
                messages.success(request, 'Category updated successfully!')
                return redirect('manage_categories')
        else:
            form = CategoryForm(instance=category)
        return render(request, 'admin/edit_category.html', {'form': form, 'category': category})
    except (Category.DoesNotExist, ValueError, TypeError):
        messages.error(request, 'Category not found!')
        return redirect('manage_categories')

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def delete_category(request, category_id):
    from .models import Category
    try:
        if isinstance(category_id, str):
            category_id = ObjectId(category_id)
        category = Category.objects.get(_id=category_id)
        category.delete()
        messages.success(request, 'Category deleted successfully!')
    except (Category.DoesNotExist, ValueError, TypeError):
        messages.error(request, 'Category not found!')
    return redirect('manage_categories')

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def manage_model_sets(request):
    from .models import ModelSet
    model_sets = ModelSet.objects.all()  # Removed order_by for Djongo compatibility
    if request.method == 'POST':
        form = ModelSetForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Model Set added successfully!')
            return redirect('manage_model_sets')
    else:
        form = ModelSetForm()
    return render(request, 'admin/manage_model_sets.html', {'model_sets': model_sets, 'form': form})

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def edit_model_set(request, set_id):
    from .models import ModelSet
    try:
        if isinstance(set_id, str):
            set_id = ObjectId(set_id)
        model_set = ModelSet.objects.get(_id=set_id)
        if request.method == 'POST':
            form = ModelSetForm(request.POST, request.FILES, instance=model_set)
            if form.is_valid():
                form.save()
                messages.success(request, 'Model Set updated successfully!')
                return redirect('manage_model_sets')
        else:
            form = ModelSetForm(instance=model_set)
        return render(request, 'admin/edit_model_set.html', {'form': form, 'model_set': model_set})
    except (ModelSet.DoesNotExist, ValueError, TypeError):
        messages.error(request, 'Model Set not found!')
        return redirect('manage_model_sets')

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def delete_model_set(request, set_id):
    from .models import ModelSet
    try:
        if isinstance(set_id, str):
            set_id = ObjectId(set_id)
        model_set = ModelSet.objects.get(_id=set_id)
        model_set.delete()
        messages.success(request, 'Model Set deleted successfully!')
    except (ModelSet.DoesNotExist, ValueError, TypeError):
        messages.error(request, 'Model Set not found!')
    return redirect('manage_model_sets')

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def manage_model_set_questions(request, set_id):
    from .models import ModelSet, ModelSetQuestion
    try:
        if isinstance(set_id, str):
            set_id = ObjectId(set_id)
        model_set = ModelSet.objects.get(_id=set_id)
        questions = ModelSetQuestion.objects.filter(model_set=model_set)
        if request.method == 'POST':
            form = ModelSetQuestionForm(request.POST)
            if form.is_valid():
                q = form.save(commit=False)
                q.model_set = model_set
                q.save()
                messages.success(request, 'Question added successfully!')
                return redirect('manage_model_set_questions', set_id=str(model_set._id))
        else:
            form = ModelSetQuestionForm(initial={'model_set': model_set})
        return render(request, 'admin/manage_model_set_questions.html', {'model_set': model_set, 'questions': questions, 'form': form})
    except (ModelSet.DoesNotExist, ValueError, TypeError):
        messages.error(request, 'Model Set not found!')
        return redirect('manage_model_sets')

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def edit_model_set_question(request, question_id):
    from .models import ModelSetQuestion
    try:
        if isinstance(question_id, str):
            question_id = ObjectId(question_id)
        question = ModelSetQuestion.objects.get(_id=question_id)
        if request.method == 'POST':
            form = ModelSetQuestionForm(request.POST, instance=question)
            if form.is_valid():
                form.save()
                messages.success(request, 'Question updated successfully!')
                return redirect('manage_model_set_questions', set_id=str(question.model_set._id))
        else:
            form = ModelSetQuestionForm(instance=question)
        return render(request, 'admin/edit_model_set_question.html', {'form': form, 'question': question})
    except (ModelSetQuestion.DoesNotExist, ValueError, TypeError):
        messages.error(request, 'Question not found!')
        return redirect('manage_model_sets')

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def delete_model_set_question(request, question_id):
    from .models import ModelSetQuestion
    try:
        if isinstance(question_id, str):
            question_id = ObjectId(question_id)
        question = ModelSetQuestion.objects.get(_id=question_id)
        set_id = str(question.model_set._id)
        question.delete()
        messages.success(request, 'Question deleted successfully!')
        return redirect('manage_model_set_questions', set_id=set_id)
    except (ModelSetQuestion.DoesNotExist, ValueError, TypeError):
        messages.error(request, 'Question not found!')
        return redirect('manage_model_sets')

@login_required
@user_passes_test(is_admin, login_url='/admin/forbidden/')
def bulk_add_model_set_questions(request, set_id):
    from .models import ModelSet, ModelSetQuestion
    try:
        if isinstance(set_id, str):
            set_id = ObjectId(set_id)
        model_set = ModelSet.objects.get(_id=set_id)
        if request.method == 'POST':
            questions_data = request.POST.getlist('question_text')
            option_a_data = request.POST.getlist('option_a')
            option_b_data = request.POST.getlist('option_b')
            option_c_data = request.POST.getlist('option_c')
            option_d_data = request.POST.getlist('option_d')
            correct_option_data = request.POST.getlist('correct_option')
            explanation_data = request.POST.getlist('explanation')
            count = 0
            for i in range(len(questions_data)):
                if questions_data[i].strip():
                    ModelSetQuestion.objects.create(
                        model_set=model_set,
                        question_text=questions_data[i],
                        option_a=option_a_data[i],
                        option_b=option_b_data[i],
                        option_c=option_c_data[i],
                        option_d=option_d_data[i],
                        correct_option=correct_option_data[i],
                        explanation=explanation_data[i]
                    )
                    count += 1
            messages.success(request, f'{count} questions added successfully!')
            return redirect('manage_model_set_questions', set_id=str(model_set._id))
        return render(request, 'admin/bulk_add_model_set_questions.html', {'model_set': model_set})
    except (ModelSet.DoesNotExist, ValueError, TypeError):
        messages.error(request, 'Model Set not found!')
        return redirect('manage_model_sets')

# User-facing: List all categories
@login_required
def model_set_categories(request):
    from .models import Category
    categories = Category.objects.all()  # Removed order_by for Djongo compatibility
    return render(request, 'model_set_categories.html', {'categories': categories})

# User-facing: List all model sets in a category
@login_required
def model_sets_by_category(request, category_id):
    from .models import Category, ModelSet
    from bson import ObjectId
    try:
        if isinstance(category_id, str):
            category_id = ObjectId(category_id)
        category = Category.objects.get(_id=category_id)
        model_sets = ModelSet.objects.filter(category=category)
        return render(request, 'model_set_list.html', {'category': category, 'model_sets': model_sets})
    except (Category.DoesNotExist, ValueError, TypeError):
        from django.http import Http404
        raise Http404('Category not found')

# User-facing: Start page for a model set
@login_required
def model_set_start(request, set_id):
    from .models import ModelSet
    from bson import ObjectId
    try:
        if isinstance(set_id, str):
            set_id = ObjectId(set_id)
        model_set = ModelSet.objects.get(_id=set_id)
        return render(request, 'model_set_start.html', {'model_set': model_set})
    except (ModelSet.DoesNotExist, ValueError, TypeError):
        from django.http import Http404
        raise Http404('Model Set not found')

# User-facing: Test interface for a model set
@login_required
def model_set_test(request, set_id):
    from .models import ModelSet, ModelSetQuestion
    from bson import ObjectId
    try:
        if isinstance(set_id, str):
            set_id = ObjectId(set_id)
        model_set = ModelSet.objects.get(_id=set_id)
        questions = list(ModelSetQuestion.objects.filter(model_set=model_set))
        total_seconds = model_set.timer_hours * 3600 + model_set.timer_minutes * 60 + model_set.timer_seconds
        if request.method == 'POST':
            user_answers = {}
            for q in questions:
                user_answers[str(q._id)] = request.POST.get(f'answer_{q._id}', '')
            start_time = request.session.get(f'model_set_{set_id}_start_time')
            if start_time:
                elapsed = (timezone.now() - datetime.datetime.fromisoformat(start_time)).total_seconds()
            else:
                elapsed = 0
            correct = 0
            results = []
            for q in questions:
                user_ans = user_answers.get(str(q._id), '')
                is_correct = (user_ans == q.correct_option)
                if is_correct:
                    correct += 1
                results.append({'question': q, 'user_answer': user_ans, 'is_correct': is_correct})
            score = correct
            percent = (score / len(questions)) * 100 if questions else 0
            request.session.pop(f'model_set_{set_id}_start_time', None)
            return render(request, 'model_set_result.html', {
                'model_set': model_set,
                'results': results,
                'score': score,
                'percent': percent,
                'elapsed': int(elapsed),
                'total': len(questions),
            })
        # GET: start timer
        request.session[f'model_set_{set_id}_start_time'] = timezone.now().isoformat()
        return render(request, 'model_set_test.html', {
            'model_set': model_set,
            'questions': questions,
            'total_seconds': total_seconds,
        })
    except (ModelSet.DoesNotExist, ValueError, TypeError):
        from django.http import Http404
        raise Http404('Model Set not found')
